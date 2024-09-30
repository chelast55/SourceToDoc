# Using the Comment Converter

Specify `--converter <type>` to use the comment converter.

Where `type` can be one of the following:

- `default`
- `comment_style`
- `command_style`
- `find_and_replace` 

Use `--cc_replace replace|append|inline` to specify how the new comments should be placed on the old comments.
- `replace` - Replaces old comments with new comments.
- `append` - Places new comments in a new "comment block" under old comments.
- `inline` - Places new comments under old comments in the same "comment block" of the old comments.

These options change how the source files are parsed:
- `--cc_c_regex <Python RegEx>` - Matches filenames to find C source files.
    - Default: `.*\.[ch]`
- `--cc_cxx_regex <Python RegEx>`- Matches filenames to find C++ source files.
    - Default: `.*\.(c(pp|xx|c)|h(pp|xx|h)?`
- If a filename matches both, the file will be identified as a C source file.

## Default Comment Converter

Specify `--converter` or `--converter default` to use the default comment converter.

In short, it changes:

- `// ...` to `/// ...`, and
- `/* ... */` to `/** ... */`

More precisely, it changes (see Comment Style):

- `c_line` to `triple_slash_line`
- `c_block` to `javadoc_block`
- `c_block_inline` to `javadoc_block_inline`

Other styles are ignored, because they are already doxygen-style.

## Comment Style Converter

Specify `--converter comment_style` to use the Comment Style Converter.

Then use `--cc_style <style>` to specify the desired comment style:

- `c_line` (`// ...`)
- `c_block_inline` (`/* ... */`)
- `c_block` (`/* ... */`)
- `javadoc_block` (`/** ... */`)
- `javadoc_block_inline`  (`/** ... */`)
- `javadoc_block_member_inline` (`/**< ... */`)
- `qt_line` (`//! ...`)
- `qt_line_member` (`//!< ...`)
- `qt_block` (`/*! ... */`)
- `qt_block_inline` (`/*! ... */`)
- `qt_block_member_inline` (`/*!< ... */`)
- `triple_slash_line` (`/// ...`)
- `triple_slash_line_member` (`///< ...`)

`inline` means, that the start and end delimiter pairs are at the same line.

For example, this comment will be recognized as a `c_block_inline`:

```c
/* a */
/* b */
```

Example (For brevity, other required arguments by the toolchain are omitted):

```sh
python main.py --converter comment_style --style javadoc_block ...
```

This will be converted:

```c
// a
// b
void f(void);
```

to this:

```c
/**
 * a
 * b
 */
void f(void);
```

Set `--cc_only_after_member` to limit the conversion to the comments that are after members of structs/classes/ ... .

The only allowed target styles are:

- `javadoc_block_member_inline`
- `qt_block_member_inline`
- `triple_slash_line_member`

because otherwise the mapping between comments and symbols can be changed if other styles are allowed.

## LLM Converter

Specify `--converter function_comment_llm` to use the LLM Converter. It uses the OpenAI API Client.

The converted comments will have the `javadoc_block` style. Comments that are already doxygen-style comments will not be converted. 

Required options:

- `--cc_openai_base_url`
- `--cc_openai_api_key`
- `--cc_llm_model`

Optional options:

- `--cc_c_system_prompt <text>` - To override the default system prompt for C source files.
- `--cc_c_user_prompt_template <text>` - To override the default user prompt, by default `{}` (a placeholder where the comment and its function text will be placed; internally roughly `<text>.format(comment+symbol)` is used before it gets passed to a LLM), for C source files.
- `--cc_cxx_system_prompt <text>` - To override the default system prompt, for C++ source files.
- `--cc_cxx_user_prompt_template <text>` - See `--cc_c_user_prompt_template`, but for C++ source files.

## Other Converters

Specify `--converter command_style` to change the doxygen command style in comments.

Required options:

- `--cc_command_style default|javadoc`
    - `default` - Changes `@<command>` to `\command` or 
    - `javadoc` - Changes `\<command>` to `@command`

Specify `--converter find_and_replace` to substitute characters in comments.

Required options:
- `--cc_find <Python RegEx>` - To find characters in comments.
- `--cc_substitution <text>` - Replaces characters matched by `--cc_find`.
