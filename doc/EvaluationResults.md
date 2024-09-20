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
|                   Name                   | Build System |      Language      |                              Description                              | Comment                                       | Repository                                           | Add. Dependencies*                                 |
|:----------------------------------------:|:------------:|:------------------:|:---------------------------------------------------------------------:|-----------------------------------------------|------------------------------------------------------|----------------------------------------------------|
|                 libavtp                  |    meson     |         C          |   Open-source implementation of IEEE Audio Video Transport Protocol   |                                               | https://github.com/Avnu/libavtp                      |                                                    |
|         FOX toolkit (meson fork)         |    meson     |     mostly C++     |                    C++ Toolkit for developing GUIs                    | Available for both targeted build systems     | https://github.com/franko/fox                        | libxext-dev libx11-dev                             |
|         FOX Toolkit (cmake fork)         |    cmake     |     mostly C++     |                    C++ Toolkit for developing GUIs                    | Available for both targeted build systems     | https://github.com/devinsmith/fox                    | libxext-dev libx11-dev                             |
|                Qt Creator                |    cmake     |     mostly C++     |        Cross-platform Editor for development with Qt framework        | Big project                                   | https://github.com/jeandet/qt-creator                | see "Compiling Qt Creator" in corresponding README |
|       C++ Best Practices Template        |    cmake     |        C++         |                   Project Template for C++ projects                   | Available for both targeted build systems     | https://github.com/cpp-best-practices/cmake_template |                                                    |
| C++ Best Practices Template (meson port) |    meson     |        C++         |                   Project Template for C++ projects                   | Available for both targeted build systems     | https://github.com/jpakkane/gamejammeson             |                                                    |
|           meson bootstrap demo           |    meson     |      mostly C      |       Demo for C project development in lightweight environment       |                                               | https://github.com/alann-sapone/meson-bootstrap      | glib2.0-dev                                        |
|                Dear ImGui                |      -       | mostly C++, some C |                   C++ GUI with minimal dependencies                   | Edge case: Self-contained/has no build system | https://github.com/ocornut/imgui                     |                                                    |
|           WOTPP macro language           |    meson     | mostly C++, some C |           Macro language for producing/manipulating strings           |                                               | https://github.com/wotpp/wotpp                       | libasan (optional)                                 |
|          Phosphor Power Monitor          |    meson     |        C++         |            Power Supply Monitoring Application (on paper)             | Edge case: Exactly 0 tests!                   | https://github.com/openbmc/phosphor-power-monitor    |                                                    |
|                 XZ Utils                 |    cmake     |         C          |          CLI Tools for general-purpose data (de)compression           |                                               | https://github.com/tukaani-project/xz/               |                                                    |
|            libuv (cmake port)            |    cmake     |         C          |                Cross-platform asynchronous I/O library                | Edge case: libuv source provided as submodule | https://github.com/jen20/libuv-cmake                 |                                                    |
|            lambda coroutines             |    cmake     |        C++         | Lightweight coroutine/multitasking function utility for C++14 lambdas |                                               | https://github.com/lefticus/lambda_coroutines        |                                                    |

\* additional dependencies installed via apt if not stated otherwise

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

## Results 2024-09-XX+ *(commit XXXXXXX)*
Every sample project was run twice. On one execution, `--dg_disable_dot_graphs` was added to the command.  
TODO: something about how the CMake projects were modified

|       Sample project        | File Size (MB, raw) | File Size (MB, no dot) | File Size (MB, with dot) | Runtime (s, no dot) | Runtime (s, with dot) | Overall Result | Converter | Doc. Gen. | TC Eval. | Ran through? | Logs OK? | Output OK? | Details |
|:---------------------------:|---------------------|------------------------|--------------------------|---------------------|-----------------------|:--------------:|:---------:|:---------:|:--------:|:------------:|:--------:|:----------:|---------|
|                             |                     |                        |                          |                     |                       |                |           |           |          |              |          |            |         |
|                             |                     |                        |                          |                     |                       |                |           |           |          |              |          |            |         |
|                             |                     |                        |                          |                     |                       |                |           |           |          |              |          |            |         |

