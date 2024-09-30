# Evaluation on open-source projects

## Process
If not stated otherwise, benchmarks were run on a Linux VM with the following specifications:
- Virtual Box (hosted on Windows 10)
- Ubuntu 24.04 LTS (ships with Python 3.12)
- 8 CPU Cores (AMD Ryzen 1700X)
- 24 GB RAM
- Virtual Hard Drive on SSD (Samsung 750 EVO)
- Software installed as explained in README

This repository was cloned with git (main branch) and all selected sample projects were also cloned and placed as subdirectories in the root ("SourceToDoc" directory).
After setup, the following command was run for all selected sample projects.
```commandline
python main.py --measure_runtime --converter --project_name NAME
```

## Sample Projects Overview
|                   Name                   | Build System |      Language      |                            Description                            | File Size (MB) | C/C++ Lines of Code | C/C++ Lines of Comment | No. Test Cases | Comment                                       | Repository                                                                                                         | Add. Dependencies*                                 |
|:----------------------------------------:|:------------:|:------------------:|:-----------------------------------------------------------------:|---------------:|--------------------:|-----------------------:|---------------:|-----------------------------------------------|--------------------------------------------------------------------------------------------------------------------|----------------------------------------------------|
|                 libavtp                  |    meson     |         C          | Open-source implementation of IEEE Audio Video Transport Protocol |            0.5 |                7498 |                   1670 |                |                                               | https://github.com/Avnu/libavtp                                                                                    |                                                    |
|         FOX toolkit (meson fork)         |    meson     |     mostly C++     |                  C++ Toolkit for developing GUIs                  |           28.4 |             2221581 |                  61093 |                | Available for both targeted build systems     | https://github.com/franko/fox                                                                                      | libxext-dev libx11-dev                             |
|         FOX Toolkit (cmake fork)         |    cmake     |     mostly C++     |                  C++ Toolkit for developing GUIs                  |           25.7 |              211521 |                  60761 |                | Available for both targeted build systems     | https://github.com/devinsmith/fox                                                                                  | libxext-dev libx11-dev                             |
|       C++ Best Practices Template        |    cmake     |        C++         |                 Project Template for C++ projects                 |            1.0 |                 288 |                     17 |                | Available for both targeted build systems     | https://github.com/cpp-best-practices/cmake_template                                                               |                                                    |
| C++ Best Practices Template (meson port) |    meson     |        C++         |                 Project Template for C++ projects                 |            0.1 |                 311 |                     21 |                | Available for both targeted build systems     | https://github.com/jpakkane/gamejammeson                                                                           |                                                    |
|           meson bootstrap demo           |    meson     |      mostly C      |     Demo for C project development in lightweight environment     |            0.0 |                  35 |                      0 |                |                                               | https://github.com/alann-sapone/meson-bootstrap                                                                    | glib2.0-dev                                        |
|                Dear ImGui                |      -       | mostly C++, some C |                 C++ GUI with minimal dependencies                 |           99.5 |               59112 |                  18402 |                | Edge case: Self-contained/has no build system | https://github.com/ocornut/imgui                                                                                   |                                                    |
|           WOTPP macro language           |    meson     | mostly C++, some C |         Macro language for producing/manipulating strings         |            1.0 |                4673 |                    680 |                |                                               | https://github.com/wotpp/wotpp                                                                                     | libasan (optional)                                 |
|          Phosphor Power Monitor          |    meson     |        C++         |          Power Supply Monitoring Application (on paper)           |            0.0 |                   8 |                     15 |              0 | Edge case: Exactly 0 tests!                   | https://github.com/openbmc/phosphor-power-monitor                                                                  |                                                    |
|                 XZ Utils                 |    cmake     |         C          |        CLI Tools for general-purpose data (de)compression         |           11.8 |               33604 |                  17827 |                |                                               | https://github.com/tukaani-project/xz/                                                                             |                                                    |
|            libuv (cmake port)            |    cmake     |         C          |              Cross-platform asynchronous I/O library              |           21.0 |               59363 |                  10596 |                | Edge case: libuv source provided as submodule | https://github.com/jen20/libuv-cmake                                                                               |                                                    |
|         CMake tutorial (step 5)          |    cmake     |        C++         |         Excerpt from example CMake project about testing          |            0.0 |                  66 |                      6 |                |                                               | https://cmake.org/cmake/help/latest/_downloads/bc2a2d94a75e2d8ef62c1e24a0b5281c/cmake-3.30.3-tutorial-source.zip   |                                                    |

\* additional dependencies installed via apt if not stated otherwise

The most recent version on the master/main branch at the time of running the benchmarks was used.  
Lines of Code/Comment were measured with [cloc](https://github.com/AlDanial/cloc). Only C/C++ LoC were considered, because everything else should not have any effect on Converter and Code Coverage and only minor effects on the Documentation generation (potentially creating HTML pages and copying content, but no static analysis and interlinking).

## Results 2024-09-16+ *(commit e830305)*
Note, that test coverage evaluation for cmake projects is not implemented yet in this version.

|       Sample project        | Overall Result | Converter | Doc. Gen. |      TC Eval.      |    Ran through?    | Logs OK? | Output OK? | Details                                                                                           |
|:---------------------------:|:--------------:|:---------:|:---------:|:------------------:|:------------------:|:--------:|:----------:|---------------------------------------------------------------------------------------------------|
|    meson bootstrap demo     |    WAITING     |   PASS    |   PASS    |        FAIL        |        PASS        |   PASS   |    FAIL    | Missing links in doc/tc report                                                                    |
| C++ Best Practices Template |    WAITING     |   PASS    |   PASS    |        FAIL        |        PASS        |   PASS   |    FAIL    | Missing links in doc/tc report                                                                    |
|           libavtp           |    WAITING     |   PASS    |   PASS    |        FAIL        |        PASS        |   PASS   |    FAIL    | Missing links in doc/tc report                                                                    |
|         FOX toolkit         |    WAITING     |   PASS    |   PASS    |        FAIL        |        PASS        |   PASS   |    FAIL    | Missing links in doc/tc report                                                                    |
|    WOTPP macro language     |    WAITING     |   PASS    |   PASS    |        FAIL        |        PASS        |   PASS   |    FAIL    | Missing links in doc/tc report                                                                    |
|   Phosphor Power Monitor    |    WAITING     |   PASS    |   PASS    |        FAIL        |        PASS        |   PASS   |    FAIL    | Missing links in doc/tc report                                                                    |
|         Dear ImGui          |      FAIL      |   FAIL    | d. n. r.  |      d. n. r.      |        FAIL        |   FAIL   |  d. n. r.  | Converter fails, contains comment lines starting with "//" when expecting "///", could be fixable |
|  Dear ImGui (no converter)  |     MIXED      |   PASS    |   PASS    | FAIL (technically) | FAIL (technically) |   PASS   |    FAIL    | FileNotFoundError when coverage report directory is not captured, although it should probably     |

General observations:  
for Doc. Gen.: 
- warning for unsupported tag "PROJECT_ICON" in Doxyfile.in is always raised (Ubuntu doxygen version 1.9.8, does not appear on Windows with doxygen 1.10.0)
for TC Eval.:  
- links to TC report in Doxygen output are generated regardless of TC report actually existing
- technically, reports should not be generated at all, as we figured out lcov installation via pip is broken
  - was still possible due to gcovr installation in outer scope from earlier installation, but gcovr reports don't support linking without method (NOT an easy fix)
  - switching to installing lcov via apt

## Additional comparison Converter with vs. without LLM (FOX toolkit meson fork) *(commit 55133c5)*
This benchmark was run on Windows 10 (AMD Ryzen 1700X, Nvidia GTX 1070, 32GB DDR4 RAM, Samsung SSD 750 EVO).  
Fox toolkit was chosen for this "sample benchmark", because it contains many block comments near functions, that would likely help understanding the architecture, if they were to appear in the generated API documentation.
Only the Comment Converter was used:  
### No LLM:
```commandline
python main.py --measure_runtime --project_name fox --disable_doc_gen --disable_test_cov --converter
```
Runtime (Converter): 38.33 seconds

### With LLM (llama3 via Ollama): 
```commandline
python main.py --measure_runtime --project_name fox --disable_doc_gen --disable_test_cov --converter function_comment_llm --cc_openai_base_url http://localhost:11434/v1 --cc_openai_api_key ollama --cc_llm_model llama3
```
Runtime (Converter): 1075.97 seconds

## Results 2024-09-26+ *(commit 50d9f1d)*
Every sample project was run twice. On one execution, `--dg_disable_dot_graphs` was added to the command.  

Added `"--tc_coverage_tyoe cmake` for CMake projects. CMake Projects had to be modified for test coverage support as follows:

### CMake Tutorial Step 5
- "Finish the Tutorial"
- insert the following lines in CMakeLists.txt just below `project(...)`
```cmake
list(APPEND CMAKE_MODULE_PATH ${CMAKE_CURRENT_LIST_DIR}/modules)
include(CodeCoverage)
append_coverage_compiler_flags()
```
- add https://github.com/bilke/cmake-modules/blob/master/CodeCoverage.cmake to project's root/modules

### FOX Toolkt (cmake fork)
- add line `enable_testing()` to CMakeLists.txt
- Still says `No tests were found!!!` (not necessarily our problem)
- **Removed for redundancy** as this adds nothing new except the CMake build

### C++ Best Practices Template
- see CMake Tutorial Step 5 (exclding the "Finish the Tutorial" step)
- because of converter bug: src/ftxui_sample/main.cpp nt main(...) -> int main
Ran, but did not finish :/
(build/_deps/catch2-build/src/src/catch2/internal/... expected, but hierarchy ended at build/_deps/catch2-build/src)
- worked on another machine ...for some unexplainable reason
- **Removed for redundancy** as this adds nothing new except the CMake build

### XZ Utils
- ignore build instructions and especially `tests/code_coverage.sh`
- same procedure as CMake Tutorial Step 5

### libuv (cmake port)
- `No tests were found!!!`
- judging from `CMakeLists.txt`, a separate executable for tests should be generated
- build seemed successful, but we could not locate any executable

| Sample project                           | Build System | File Size (MB, src) | File Size (MB, no dot) | File Size (MB, with dot) | Runtime Converter (s) | Runtime Doc. Gen. (s, no dot) | Runtime Doc. Gen. (s, with dot) | Runtime T. C. Eval. (s) | Overall Result | Converter | Doc. Gen. | TC Eval. |  Ran through?  |      Logs OK?       | Output OK? | Details                                                       |
|:-----------------------------------------|--------------|--------------------:|-----------------------:|-------------------------:|----------------------:|------------------------------:|--------------------------------:|------------------------:|:--------------:|:---------:|:---------:|:--------:|:--------------:|:-------------------:|:----------:|---------------------------------------------------------------|
| C++ Best Practices Template (meson port) | meson        |                 0.1 |  (seems incorrect) 177 |                        2 |                  0.70 |        (seems incorrect) 8.59 |                            0.32 |                       - |                |   PASS    |   PASS    |   FAIL   |      PASS      | yes                 | no tc      | geninfo error, can probably be bypassed (manually)            |
| CMake tutorial (step 5)                  | cmake        |                 0.0 |                      1 |                        2 |                  0.64 |                          0.09 |                            0.16 |                    3.67 | PASS           |   PASS    |   PASS    |   PASS   |      PASS      | yes                 | yes        |                                                               |
| FOX toolkit (meson fork)                 | meson        |                28.4 |                    515 |                     2320 |                     - |                         14.57 |                     (< ImGui) - |                       - |                |   PASS    |   PASS    |   FAIL   |      FAIL      | no runtimes with TC |            | Linking failed (utf-8 decode error), but report was generated |
| ImGui                                    | -            |                99.5 |                    119 |                     1620 |                     - |                          4.10 |                         1357.06 |                    0.40 |                |   FAIL    |   PASS    |   PASS   | FAIL (w. conv) |                     | no tc      | No build tool -> no tc                                        |
| libavtp                                  | meson        |                 0.5 |                     11 |                       27 |                  0.61 |                          0.29 |                            4.20 |                    6.90 | PASS           |   PASS    |   PASS    |   PASS   |      PASS      | yes                 | yes        |                                                               |
| libuv (cmake port)                       | cmake        |                21.0 |                     95 |                     1690 |                     - |                          2.37 |                          299.16 |                       - |                |   FAIL    |   PASS    |   FAIL   | FAIL (w. conv) |                     | no tc      | No tests are built, error on project side                     |
| meson bootstrap demo                     | meson        |                 0.0 |                      1 |                        1 |                  0.02 |                          9.09 |                            0.17 |                    5.32 | PASS           |   PASS    |   PASS    |   PASS   |      PASS      | yes                 | yes        |                                                               |
| Phosphor Power Monitor                   | meson        |                 0.0 |                      1 |                        1 |                  0.22 |                          0.08 |                            0.11 |                       - |                |   PASS    |   PASS    |   FAIL   |      PASS      | yes                 |            | No tests -> no tc                                             |
| WOTPP macro language                     | meson        |                 1.0 |                     10 |                       24 |                  4.38 |                          0.45 |                            2.80 |                       - |                |   PASS    |   PASS    |   FAIL   |      FAIL      |                     |            | No tests are built, probably needs specific arg               |
| XZ Utils                                 | cmake        |                11.8 |                     58 |                      163 |                     - |                          2.04 |                           14.99 |                   31.82 |                |   FAIL    |   PASS    |   PASS   | FAIL (w. conv) |                     |            |                                                               |

### Notes:
Converter: no cases encountered, where it broke source code

#### ImGui converter error
```sh
4/35 Converting file "/home/testuser/SourceToDoc/imgui/imgui.h"
Extracting comments
Traceback (most recent call last):
  File "/home/testuser/SourceToDoc/main.py", line 28, in <module>
    run_comment_converter(parser, config.project_path, **vars(config.args))
  File "/home/testuser/SourceToDoc/sourcetodoc/docstring/cli.py", line 82, in run_comment_converter
    converter.convert_files(src_path)
  File "/home/testuser/SourceToDoc/sourcetodoc/docstring/converter.py", line 102, in convert_files
    self._convert_file(file, self.c_extractor)
  File "/home/testuser/SourceToDoc/sourcetodoc/docstring/converter.py", line 121, in _convert_file
    result: str = self._convert_string(code, extractor)
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/testuser/SourceToDoc/sourcetodoc/docstring/converter.py", line 151, in _convert_string
    comments = extractor.extract_comments(code)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/testuser/SourceToDoc/sourcetodoc/docstring/extractors/c_libclang_extractor.py", line 34, in extract_comments
    return self.extractor.extract_comments(code)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/testuser/SourceToDoc/sourcetodoc/docstring/extractors/libclang_extractor.py", line 65, in extract_comments
    symbol_range = self.__class__._get_symbol_range_by_line_and_column(code, node)
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/testuser/SourceToDoc/sourcetodoc/docstring/extractors/libclang_extractor.py", line 112, in _get_symbol_range_by_line_and_column
    start, end = index_from_coordinates(code, [
    ^^^^^^^^^^
  File "/home/testuser/SourceToDoc/sourcetodoc/common/helpers.py", line 74, in index_from_coordinates
    raise ValueError(f"No index was found for Line: {line} and Column: {column}")
ValueError: No index was found for Line: 0 and Column: 0
```

#### libuv converter error
```sh
70/315 Converting file "/home/testuser/SourceToDoc/libuv-cmake/libuv/src/win/winapi.h"
Extracting comments
Traceback (most recent call last):
  File "/home/testuser/SourceToDoc/main.py", line 28, in <module>
    run_comment_converter(parser, config.project_path, **vars(config.args))
  File "/home/testuser/SourceToDoc/sourcetodoc/docstring/cli.py", line 82, in run_comment_converter
    converter.convert_files(src_path)
  File "/home/testuser/SourceToDoc/sourcetodoc/docstring/converter.py", line 102, in convert_files
    self._convert_file(file, self.c_extractor)
  File "/home/testuser/SourceToDoc/sourcetodoc/docstring/converter.py", line 121, in _convert_file
    result: str = self._convert_string(code, extractor)
                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/testuser/SourceToDoc/sourcetodoc/docstring/converter.py", line 151, in _convert_string
    comments = extractor.extract_comments(code)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/testuser/SourceToDoc/sourcetodoc/docstring/extractors/c_libclang_extractor.py", line 34, in extract_comments
    return self.extractor.extract_comments(code)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/testuser/SourceToDoc/sourcetodoc/docstring/extractors/libclang_extractor.py", line 65, in extract_comments
    symbol_range = self.__class__._get_symbol_range_by_line_and_column(code, node)
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/testuser/SourceToDoc/sourcetodoc/docstring/extractors/libclang_extractor.py", line 112, in _get_symbol_range_by_line_and_column
    start, end = index_from_coordinates(code, [
    ^^^^^^^^^^
  File "/home/testuser/SourceToDoc/sourcetodoc/common/helpers.py", line 74, in index_from_coordinates
    raise ValueError(f"No index was found for Line: {line} and Column: {column}")
ValueError: No index was found for Line: 0 and Column: 0
```

#### Phosphor tc error
````sh
[1/3] Compiling C++ object src/psu-monitor/psu-monitor.p/main.cpp.o
[2/3] Linking target src/psu-monitor/psu-monitor
[2/3] Running all tests.
No tests defined.
[1/1] Generates HTML coverage report
FAILED: meson-internal__coverage-html 
/home/testuser/SourceToDoc/venv/bin/meson --internal coverage --html /home/testuser/SourceToDoc/phosphor-power-monitor /home/testuser/SourceToDoc/phosphor-power-monitor/subprojects /home/testuser/SourceToDoc/phosphor-power-monitor/build /home/testuser/SourceToDoc/phosphor-power-monitor/build/meson-logs --llvm-cov llvm-cov-16
Ubuntu LLVM version 16.0.6
  Optimized build.
genhtml: LCOV version 2.0-1
Capturing coverage data from /home/testuser/SourceToDoc/phosphor-power-monitor/build
geninfo cmd: '/usr/bin/geninfo /home/testuser/SourceToDoc/phosphor-power-monitor/build --output-filename /home/testuser/SourceToDoc/phosphor-power-monitor/build/meson-logs/coverage.info.initial --initial --memory 0'
Found gcov version: 13.2.0
Using intermediate gcov format
Writing temporary data to /tmp/geninfo_dat17jb
Scanning /home/testuser/SourceToDoc/phosphor-power-monitor/build for .gcno files ...
Found 1 graph files in /home/testuser/SourceToDoc/phosphor-power-monitor/build
Processing /home/testuser/SourceToDoc/phosphor-power-monitor/build/src/psu-monitor/psu-monitor.p/main.cpp.gcno
Finished .info-file creation
Capturing coverage data from /home/testuser/SourceToDoc/phosphor-power-monitor/build
geninfo cmd: '/usr/bin/geninfo /home/testuser/SourceToDoc/phosphor-power-monitor/build --output-filename /home/testuser/SourceToDoc/phosphor-power-monitor/build/meson-logs/coverage.info.run --no-checksum --rc branch_coverage=1 --memory 0 --branch-coverage'
Found gcov version: 13.2.0
Using intermediate gcov format
Writing temporary data to /tmp/geninfo_datA1Ww
Scanning /home/testuser/SourceToDoc/phosphor-power-monitor/build for .gcda files ...
geninfo: ERROR: no .gcda files found in /home/testuser/SourceToDoc/phosphor-power-monitor/build
	(use "geninfo --ignore-errors empty ..." to bypass this error)
Traceback (most recent call last):
  File "/home/testuser/SourceToDoc/venv/bin/meson", line 8, in <module>
    sys.exit(main())
             ^^^^^^
  File "/home/testuser/SourceToDoc/venv/lib/python3.12/site-packages/mesonbuild/mesonmain.py", line 291, in main
    return run(sys.argv[1:], launcher)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/testuser/SourceToDoc/venv/lib/python3.12/site-packages/mesonbuild/mesonmain.py", line 279, in run
    return run_script_command(args[1], args[2:])
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/testuser/SourceToDoc/venv/lib/python3.12/site-packages/mesonbuild/mesonmain.py", line 220, in run_script_command
    return module.run(script_args)
           ^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/testuser/SourceToDoc/venv/lib/python3.12/site-packages/mesonbuild/scripts/coverage.py", line 208, in run
    return coverage(options.outputs, options.source_root,
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/testuser/SourceToDoc/venv/lib/python3.12/site-packages/mesonbuild/scripts/coverage.py", line 121, in coverage
    subprocess.check_call([lcov_exe,
  File "/usr/lib/python3.12/subprocess.py", line 413, in check_call
    raise CalledProcessError(retcode, cmd)
subprocess.CalledProcessError: Command '['lcov', '--directory', '/home/testuser/SourceToDoc/phosphor-power-monitor/build', '--capture', '--output-file', '/home/testuser/SourceToDoc/phosphor-power-monitor/build/meson-logs/coverage.info.run', '--no-checksum', '--rc', 'branch_coverage=1']' returned non-zero exit status 1.
ninja: build stopped: subcommand failed.
````

#### WOTPP tc error
````sh
The Meson build system
Version: 1.5.2
Source dir: /home/testuser/SourceToDoc/wotpp
Build dir: /home/testuser/SourceToDoc/wotpp/build
Build type: native build
Project name: wot++
Project version: 1.0
C compiler for the host machine: cc (gcc 13.2.0 "cc (Ubuntu 13.2.0-23ubuntu4) 13.2.0")
C linker for the host machine: cc ld.bfd 2.42
C++ compiler for the host machine: c++ (gcc 13.2.0 "c++ (Ubuntu 13.2.0-23ubuntu4) 13.2.0")
C++ linker for the host machine: c++ ld.bfd 2.42
Host machine cpu family: x86_64
Host machine cpu: x86_64
Compiler for C++ supports arguments -Wlogical-op: YES 
Compiler for C++ supports arguments -Wduplicated-branches: YES 
Compiler for C++ supports arguments -Wduplicated-cond: YES 
Compiler for C++ supports arguments -Wno-unused-parameter: YES 
Library stdc++fs found: YES
Program tests/run_test.py found: NO

meson.build:186:14: ERROR: Program 'tests/run_test.py' not found or not executable

A full log can be found at /home/testuser/SourceToDoc/wotpp/build/meson-logs/meson-log.txt
ninja: error: loading 'build.ninja': No such file or directory
ninja: error: loading 'build.ninja': No such file or directory
````

#### fox meson linker error
````sh
Traceback (most recent call last):
  File "/home/testuser/SourceToDoc/main.py", line 98, in <module>
    link_all_tc_report_and_documentation_files(config.out_path_relative / Path(config.args.project_name))
  File "/home/testuser/SourceToDoc/sourcetodoc/testcoverage/linker.py", line 74, in link_all_tc_report_and_documentation_files
    _insert_link(tc_file, marker_line_in_tc_files, link_to_dg_class_file)
  File "/home/testuser/SourceToDoc/sourcetodoc/testcoverage/linker.py", line 114, in _insert_link
    lines: list[str] = file.readlines()
                       ^^^^^^^^^^^^^^^^
  File "<frozen codecs>", line 322, in decode
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xeb in position 8189: invalid continuation byte
````