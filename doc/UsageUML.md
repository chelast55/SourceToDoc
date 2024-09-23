Use `--generate_uml_diagrams` with `--uml_compilation_db_dir <path>` to generate some class, package and include diagrams using [clang-uml](https://clang-uml.github.io).
```commandline
python main.py \
  --project_name <project_name> \
  --project_path <project_path> \
  --generate_uml_diagrams \
  --uml_compilation_db_dir <dir_with_compile_commands.json>
```
- A `default-clang-uml.yaml` file will be created in `project_path`
- If `--uml_sequence_diagrams` is specified, `clang-uml-sequence-diagrams.yaml` will be created
  - Qualified names of functions and methods will extracted and included in `clang-uml-sequence-diagrams.yaml`
- `clang-uml` will run to generate `.puml` files
- `plantuml` (if found in `PATH`, else specify `--uml_plantuml_jar_path <path>`) will run to generate `.svg` files
- `HTML` files will be created to view the generated `.svg` files

Note: Try `--uml_query_driver .` on macOS or Linux if `clang-uml` can't generate diagrams. It will pass the argument `--query-driver .` to `clang-uml`.

More options:
- `--uml_find_option all|exclude_private_and_protected|only_main_function` filters functions if `--uml_sequence_diagrams` is specified
- `--uml_include_path` filters source files