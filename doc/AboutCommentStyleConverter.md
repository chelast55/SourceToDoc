# About the Comment Style Converter

Comments in C and C++:

_Line comments_:

```c
// This is a line comment

// Multiple // at the start of every new line
// are needed to span multiple lines
```

Line comments start with a `//` delimiter and end at the next occurring line break.

_Block comments_:

```c
/* This is a block comment */

/* This is a block comment that spans multiple lines
 * <- this exists for aesthetics
 */
```

Block comments start with a `/*` delimiter and end at the next occurring `*/` delimiter.

The goal of the Comment Style Converter is to format arbitrary C comments to doxygen-style comments.

```c
/// Additional / after //
//! Additional ! after // (Qt style)
/** Additional * after /* (Qt style) */
/*! Additional ! after /* (JavaDoc style) */
```

The above comments are typically placed above functions, classes, ... . There are also comments after members:

```c
int a; ///< Additional /< after //
```

## Principle of the Comment Style Converter

The Comment Style Converter uses pattern matching on the comment to identify the style of that comment, for example

```c
// Hello
// World
```

will be identified as a `c_line` comment, because it starts with `//` at every line.

The converter knows `c_line` (string identifier internally used in the program) has the start delimiter `//` and will remove it at every line:

```
 Hello
 World
```

This will be unindented:

```
Hello
World
```

Finally, If the desired comment style is `triple_slash_line`, the converter will add `///` at every line:

```c
/// Hello
/// World
```

For aesthetics, additional spaces are also added.

If the desired comment style is `javadoc_block`, the converter will add `/**` at the start and `*/`:

```c
/**
 * Hello
 * World
 */
```

For aesthetics, additional spaces (including) and `*` are also added.

This approach makes it possible to convert a comment with a arbitrary style to another arbitrary style (except if a line comment contains a `*/` string)

## Considerations

### Comments over Multiple Lines

Every comment can span multiple lines when the start delimiter is used multiple times:

```c
// ...
// ...
/// ...
///< ...
```

This will be identified as a `c_block` comment, so `//` will be removed (Reason: If there exist a line comment starting with a less specific delimiter, it will be assumed that other characters are not part of the delimiter).

Converting the comment to `qt_line` style:

```c
//! ...
//! ...
//!/ ...
//!/< ...
```

The same applies to block comments that start and end at the same line.

### `*/` in a Line Comment

`*/` can be part of the content of the line comment:

```c
// .+-*/
```

It cannot be converted to some block style:

```c
/** .+-*/ */
```

because block comments cannot be nested in C and C++.

Wo choose to convert it to a different line style for the Default Converter:

```c
/// Allow 0123456789.+-*/
```

The Comment Style Converter will skip line comments that have one or more `*/`.
