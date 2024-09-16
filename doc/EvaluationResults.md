# Evaluation on open-source projects

## Process
TODO: elaborate
`python main.py --converter --project_name NAME`


## Sample Projects Overview
|                   Name                   | Build System |      Language      | Description                                                           | Comment                                       | Repository                                           | Add. Dependencies*                                 |
|:----------------------------------------:|:------------:|:------------------:|-----------------------------------------------------------------------|-----------------------------------------------|------------------------------------------------------|----------------------------------------------------|
|                 libavtp                  |    meson     |         C          | Open-source implementation of IEEE Audio Video Transport Protocol     |                                               | https://github.com/Avnu/libavtp                      |                                                    |
|         FOX toolkit (meson fork)         |    meson     |     mostly C++     | C++ Toolkit for developing GUIs                                       | Available for both targeted build systems     | https://github.com/franko/fox                        | libxext-dev libx11-dev                             |
|         FOX Toolkit (cmake fork)         |    cmake     |     mostly C++     | C++ Toolkit for developing GUIs                                       | Available for both targeted build systems     | https://github.com/devinsmith/fox                    | libxext-dev libx11-dev                             |
|                Qt Creator                |    cmake     |     mostly C++     | Cross-platform Editor for development with Qt framework               | Big project                                   | https://github.com/jeandet/qt-creator                | see "Compiling Qt Creator" in corresponding README |
|       C++ Best Practices Template        |    cmake     |        C++         | Project Template for C++ projects                                     | Available for both targeted build systems     | https://github.com/cpp-best-practices/cmake_template |                                                    |
| C++ Best Practices Template (meson port) |    meson     |        C++         | Project Template for C++ projects                                     | Available for both targeted build systems     | https://github.com/jpakkane/gamejammeson             |                                                    |
|           meson bootstrap demo           |    meson     |      mostly C      | Demo for C project development in lightweight environment             |                                               | https://github.com/alann-sapone/meson-bootstrap      | glib2.0-dev                                        |
|                Dear ImGui                |      -       | mostly C++, some C | C++ GUI with minimal dependencies                                     | Edge case: Self-contained/has no build system | https://github.com/ocornut/imgui                     |                                                    |
|           WOTPP macro language           |    meson     | mostly C++, some C | Macro language for producing/manipulating strings                     |                                               | https://github.com/wotpp/wotpp                       | libasan (optional)                                 |
|            COD microframework            |    meson     |         C          | C Microframework for generating websites with minimal dependencies    |                                               | https://github.com/bitmodo/cod                       |                                                    |
|          Phosphor Power Monitor          |    meson     |        C++         | Power Supply Monitoring Application                                   | Edge case: Exactly 0 tests!                   | https://github.com/openbmc/phosphor-power-monitor    |                                                    |
|                 XZ Utils                 |    cmake     |         C          | CLI Tools for general-purpose data (de)compression                    |                                               | https://github.com/tukaani-project/xz/               |                                                    |
|            libuv (cmake port)            |    cmake     |         C          | Cross-platform asynchronous I/O library                               | Edge case: libuv source provided as submodule | https://github.com/jen20/libuv-cmake                 |                                                    |
|            lambda coroutines             |    cmake     |        C++         | Lightweight coroutine/multitasking function utility for C++14 lambdas |                                               | https://github.com/lefticus/lambda_coroutines        |                                                    |

\* additional dependencies installed via apt if not stated otherwise

## Results 2024-09-16+ *(commit e830305)*
Note, that test coverage evaluation for cmake projects is not implemented yet in this version.

| Sample project              | Result  | Details                                                                                            |
|-----------------------------|---------|----------------------------------------------------------------------------------------------------|
| meson bootstrap demo        | WAITING | Ran through without major errors, but no further evaluation yet                                    |
| C++ Best Practices Template | WAITING | Ran through without major errors, but no further evaluation yet                                    |
| libavtp                     | WAITING | Ran through without major errors, but no further evaluation yet                                    |
| FOX toolkit                 | WAITING | Ran through without major errors, but no further evaluation yet                                    |
| WOTPP macro language        | WAITING | Ran through without major errors, but no further evaluation yet                                    |
| COD microframework          | WAITING | Ran through without major errors, but no further evaluation yet                                    |
| Phosphor Power Monitor      | WAITING | Ran through without major errors, but no further evaluation yet                                    |
| Dear ImGui                  | FAILED  | Converter fails, contains comment lines starting with "//" when expecting "///", could be fixable  |
| Dear ImGui (no converter)   | MIXED   | FileNotFoundError when coverage report directory is not captured, although it should probably      |

General observation: warning for unsupported tag "PROJECT_ICON" in Doxyfile.in is always raised
