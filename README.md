# SourceToDoc
Forschungsprojekt INF 2024 "Reverse Engineering of Documentation and Design for Independently Developed Safety-Related Projects"

## Setup
To ensure that all submodules are also cloned, use the following command:
```sh
git clone --recurse-submodules https://github.com/chelast55/SourceToDoc.git
```
### Linux (Debian/Ubuntu)
When using Linux, you have to begin the following example commands with `python3` instad of `python`, if you have not installed `python-is-python3`.  
All Dependencies can be installed via *apt* and *pip* packet managers.  
If you have not installed `python(3.12)` yet or your default `python(3)` version is older than `3.12`, install it first (`python3.12` and `python3.12-venv` via apt) and make sure 
to address it with `python3.12`.
With that out of the way, you can continue installing the non-python dependencies via apt:
```sh
sudo apt install python3-venv doxygen graphviz cmake libcmocka-dev
```
Next, navigate to or open a terminal in the main directory of the freshly downloaded repository (SourceToDoc).  
There, create a virtual environment and activate it:
```sh
python -m venv venv
source venv/bin/activate
```
Within the virtual environment (likely indicated by a `(venv)` at the beginning of your command line), you can install the python dependencies:
(additional requirements are not required for python includes, but for running the test coverage part of the toolchain)
```sh
pip install -r requirements.txt
pip install -r requirements_additional.txt
pip install pytest  # only required if you want to run the unit tests for this toolchain
```
Now, you should be able to run the whole toolchain!

### Windows
Various Dependencies have to be installed manually on Windows.
Most of them have installer executables:
(Where applicable, make sure, the box for adding it to the Windows Path is ticked!)
- Python 3.12: https://www.python.org/downloads/
- Doxygen: https://www.doxygen.nl/download.html
- Graphviz: https://graphviz.org/download/
- CMake: https://cmake.org/download/
You should at least reboot once after all of them are installed, to ensure, Path is updated.

The final one (CMocka) is more complicated, as it has to be built from source. 
**If you do NOT plan to use the Test Coverage Evaluation part of the toolchain, you can skip these cmocka-related steps:**  
A Guide how to set it up can be found here: https://sam.hooke.me/note/2022/04/setting-up-cmocka/  
What is not mentioned in the guide, is that mingw32 (and mingw32-make) have to be installed: https://sourceforge.net/projects/mingw/ (make sure to manually enable mingw32-make)  
Additionally, an implementation of `strtok_r()` has to be added in `cmocka.c` (a public domain implementation of this function by Charlie Gordon can be found [here](http://groups.google.com/group/comp.lang.c/msg/2ab1ecbb86646684)).

All remaining Dependencies can be installed via the *pip* packet manager.
To do so, navigate to or open a PowerShell terminal in the main directory of the freshly downloaded repository (SourceToDoc).  
There, create a virtual environment and activate it:
```sh
python -m venv venv
venv\Scripts\Activate.ps1
```
Within the virtual environment (likely indicated by a `(venv)` at the beginning of your command line), you can install the python dependencies:
(additional requirements are not required for python includes, but for running the test coverage part of the toolchain)
```sh
pip install -r requirements.txt
pip install -r requirements_additional.txt
pip install pytest  # only required if you want to run the unit tests for this toolchain
```
Now, you should be able to run the whole toolchain!


## Usage
To run the toolchain in its most basic version, you have to provide at least the name of the directory (`<PROJECT_NAME>`) containing the source of the project, you want to document:   
(the `<PROJECT_NAME>` directory and your terminal instance should be in the same directory, where `main.py` is located and the Python virtual environment should be active)

```sh
python main.py --project_name <PROJECT_NAME>
```
Depending on the software project you try to document, you may not get the most out of the generated documentation. 
The source code may contain incorrectly formatted docstrings, which causes symbols (function/variable/class names etc.) not to be recognized/linked correctly or the entire docstring not to appear in the documentation at all.  
  
An additional component of the toolchain, the *comment converter*, can be enabled to preprocess the encountered docstrings. Thus, the **recommended** basic version to run the toolchain is as follows:  
(this will modify the source code (more precisely: change // and /* ... /* on symbols to /** ... */ in this case))
```sh
python main.py --project_name <PROJECT_NAME> --converter
```
Just enabling the *comment converter* like this will likely solve the issue of docstrings not being recognized. For even better results (where symbols are resolved more correctly), 
an OpenAI-API-compatible LLM can be used to preprocess docstrings:
```sh
python main.py --project_name test --project_path <path> --converter function_comment_llm --cc_openai_base_url <url> --cc_openai_api_key <key> --cc_llm_model <model>
```

If desired, all components of the toolchain can be disabled individually (`disable_doc_gen`for *documentation generation* and `disable_test_cov` for *test coverage evaluation*).  
Some recommended additional options would be `--project_number` and `--project_brief`.  
For all possible options, see:
```sh
python main.py --help
```

## File Hierarchy
TODO

 
