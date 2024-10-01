# About Extracting Comments

To convert comments, they have to be extracted from the source files first.

## Regular Expressions

Regular expressions (more specifically, the [re](https://docs.python.org/3/library/re.html) module) is the first method we used to extract comments from strings.

For example, this matches a single C line comment:

```python
re.compile(r"//.*")
```

This matches also subsequent line comments:

```python
re.compile(r"//.*(\n( |\t)*//.*)*")
```

This matches a C block comment:

```python
re.compile(r"/\*(.|\n)*?\*/")
```

We want only comments that are before C function declarations or definitions (we call it a "symbol", the holder of the comment), so we need a regex that matches one:

```python
r"\b(?:\w+\s+){1,2}\w+\s*\([^)]*\)"
```

This works for many cases, but we think it won't work 100% reliable.

If the regex for line/block comments and C functions are concatenated, it will match only line comments before C functions.

We also want comments that are before struct, enum, typdef declarations / definitions. Global variables, variables in structs and constant in structs can also have comments.

We also want comments from C++ source files. C++ is a more complex language than C that also has classes, templates and more.

Therefore the regex based approach will be cumbersome (apart from that, regex is not powerful enough to take nested `{...}` into account).

## libclang

[libclang](https://clang.llvm.org/doxygen/group__CINDEX.html) is a C API to Clang. It can parse source code into an [Abstract Syntax Tree](https://en.wikipedia.org/wiki/Abstract_syntax_tree) (AST) that can be traversed.

There exist an official [Python binding](https://github.com/llvm/llvm-project/tree/main/clang/bindings/python) (implemented with [ctypes](https://docs.python.org/3/library/ctypes.html)) and an unofficial [Python package](https://pypi.org/project/libclang/) that also provides platform specific shared libraries.

Clang has the capabilities to include comments into an AST, and attaching it to a cursor (a pointer to a node in the AST), making it suitable for our use case.

This is how we parse a string as a C++ source file using libclang:

```python
code = "..." # String of source file

fake_path = "unsaved.cpp" # Arbitrary filename, file extenions can be changed
                          # to .c to parse it as a C source file

unsaved = [(fake_path, code)] # Treat the string in "code" as it were in the
                              # file "unsaved.cpp" (1)

tu = TranslationUnit.from_source(
    fake_path, # * (1)
    ["-fparse-all-comments"], # Include // and /* ... */ comments
    unsaved_files=unsaved, # (1)
    options=TranslationUnit.PARSE_SKIP_FUNCTION_BODIES | TranslationUnit.PARSE_INCOMPLETE,
)
```

- Be default, libclang will only include doxygen-style comments, so we need to pass the `-fparse-all-comments` options.
- We are only interested in getting comments, so we pass `TranslationUnit.PARSE_SKIP_FUNCTION_BODIES` (we don't need nodes in functions or methods) and `TranslationUnit.PARSE_INCOMPLETE` (typically used when parsing headers).

Then we traverse the AST over all nodes of the file "`unsaved.cpp`" and check with `node.raw_comment` if there exist a comment on it. If it exists, we will return the `raw_comment` (e.g. `// Hello`) with its symbol (e.g. `void f(void)`) and their start and end index in the string of the source file.

### Encountered Problems and Solutions

#### Missing Function

 `node.extent.start.offset` and `node.extent.end.offset` to get the start and end index of the node, where `extent` is of type `SourceRange`, and `start` and `end` is of type `SourceLocation`.

The libclang Python binding doesn't directly expose the functions to get the indices for the comment, but libclang does it with the C function `clang_Cursor_getCommentRange`.

We can create a binding for that function, like how the libclang binding (`cindex.py`) does it:

```python
from clang.cindex import (Cursor, SourceRange, conf, register_function)

register_function(conf.lib, ("clang_Cursor_getCommentRange", [Cursor], SourceRange), False)

# New function to get the indices
def clang_get_comment_range(cursor: Cursor) -> SourceRange:
    return conf.lib.clang_Cursor_getCommentRange(cursor)
```

If `conf` and `register_function` are not stable, `ctyles` can be directly used instead to create a binding for this function.

#### Wrong Indices

We once encountered a case where the returned indices of a comment was wrong, leading to a "damaged source file":

Snippet from [zip_decoder.c](https://github.com/freebsd/freebsd-src/blob/215fd38e2915d142cb4b0245f137329ef4da5a12/contrib/xz/src/liblzma/common/lzip_decoder.c):

```c
/// .lz member format version
uint32_t version;
```

was converted to:

```c
///**
 * .lz member format version
 */uint32_t version;
```

The returned indices were off by two characters to the right (newline is a character).

We think there can be a mismatch between string indices in Python and the returned offsets of libclang (also depending on the file encoding or the characters that can be in a file).

Because of that, we are using `line`, and `column` instead off `offset` of `SourceLocation`. We implemented a function ([IndexFinder class](https://github.com/chelast55/SourceToDoc/blob/a6cf7bdf7f4b55000a7c7a0866c65815b58e0101/sourcetodoc/common/helpers.py)) that returns an index given a line and column (`O(n)` for the first call, `O(1)` for subsequent calls).

Furthermore, we added a check that the returned indices of the comment must match the comment.

#### Line and Column can be Zero

For this typedef (Source: [winapi.h](https://github.com/libuv/libuv/blob/f806be87d3276fc9f672dbf43753a3c44dc26228/src/win/winapi.h)):

```c
/* from Winuser.h */
typedef VOID (CALLBACK* WINEVENTPROC)
             (HWINEVENTHOOK hWinEventHook,
              DWORD         event,
              HWND          hwnd,
              LONG          idObject,
              LONG          idChild,
              DWORD         idEventThread,
              DWORD         dwmsEventTime);
```

The `SourceRange` of the cursor (not the comment) looks like that:

```
<SourceRange
	start <SourceLocation file None, line 0, column 0>,
	end <SourceLocation file None, line 0, column 0>>
```

We this is because `VOID` is uppercase and libclang cannot resolve it.

As a workaround we are using `node.location` instead of `node.extent.start` for the start location and `node.location + len(node.displayname)` for the end location, where `displayname` will be `"VOID"`. The disadvantage is that the string `"typdef"` and the string until `;` won't be part of the returned symbol. To include these strings, more work is needed.

#### Multiple Comments at Once

libclang will return all comments above this function:

```c
/* block included
 */ 
// line included
void f(void);
```

Another example:

```c
// line included

// line included
void f(void);
```

We decide to select only the comments that are furthest down. For that we implemented a [parser](https://github.com/chelast55/SourceToDoc/blob/a6cf7bdf7f4b55000a7c7a0866c65815b58e0101/sourcetodoc/docstring/comment_parsing.py) to split these comments.

## More Alternatives that are not Used

### [Tree-sitter](https://tree-sitter.github.io/tree-sitter/)

With Tree-sitter parsers can be generated and used to create [concrete syntax trees](https://en.wikipedia.org/wiki/Parse_tree). There exist a [lot of parsers](https://github.com/tree-sitter/tree-sitter/wiki/List-of-parsers), including some for C and C++.

An official [binding](https://pypi.org/project/tree-sitter/) for Python exist. There are also Python packages to parse [C](https://pypi.org/project/tree-sitter-c/) and [C++](https://pypi.org/project/tree-sitter-cpp/).

We only tested Tree-sitter briefly:

- From a node, it is possible to traverse to siblings and parents directly in the tree
- Comments have their own nodes, in contrast to libclang, where a comments are attached to nodes that represent a function or something else (and [[#Multiple Comments at Once]])
- Tree-sitter is a pure parser, something like [[#Wrong Indices]] and [[#Line and Column can be Zero]] probably won't happen

We think that it may be more suitable for our use case than libclang. Because of time constraints we cannot implement a Comment Extractor with Tree-sitter.
