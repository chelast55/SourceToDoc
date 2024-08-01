# SourceToDoc
Forschungsprojekt INF 2024 "Reverse Engineering of Documentation and Design for Independently Developed Safety-Related Projects"

## Setup
To ensure that all submodules are also cloned, use the following command:
```sh
$ git clone --recurse-submodules https://github.com/chelast55/SourceToDoc.git
```
### Linux (Debian/Ubuntu)
When using Linux, you have to begin the following example commands with `python3` instad of `python`, if you have not installed `python-is-python3`.  
All Dependencies can be installed via *apt* and *pip* packet managers.  
If you have not installed `python(3.12)` yet or your default `python(3)` version is older than `3.12`, install it first and make sure, it is set as default
or you address it with `python3.12` (see https://ubuntuhandbook.org/index.php/2023/05/install-python-3-12-ubuntu/).  
With that out of the way, you can continue installing the non-python dependencies via apt:
```sh
$ sudo apt install python3-venv doxygen graphviz cmake libcmocka-dev
```
Next, navigate to or open a terminal in the main directory of the freshly downloaded repository (SourceToDoc).  
There, create a virtual environment and activate it:
```sh
$ python -m venv venv
$ source venv/bin/activate
```
Within the virtual environment (likely indicated by a `(venv)` at the beginning of your command line), you can install the python dependencies:
Python dependencies:
```sh
$ sudo pip install -r requirements.txt
```
Now, you should be able to run the whole toolchain!

### Windows
TODO


## Usage
To run the toolchain in its most basic version, you have to provide at least the name of the directory (`<PROJECT_NAME>`) containing the source of the project, you want to document:   
(the `<PROJECT_NAME>` directory and your terminal instance should be in the same directory, where `main.py` is located and the Python virtual environment should be active)

```sh
$ python main.py --project_name <PROJECT_NAME>
```
Depending on the software project you try to document, you may not get the most out of the generated documentation. The source code may contain incorrectly formatted docstrings, which causes symbols (function/variable/class names etc.) not to be recognized/linked correctly or the entire docstring not to appear in the documentation at all.  
  
An additional component of the toolchain, the *comment converter*, can be enabled to preprocess the encountered docstrings. Thus, the **recommended** basic version to run the toolchain is as follows:  
(this will modify the source code (more precisely: change // and /* ... /* on symbols to /** ... */ in this case))
```sh
$ python main.py --project_name <PROJECT_NAME> --converter
```
Just enabling the *comment converter* like this will likely solve the issue of docstrings not being recognized. For even better results (where symbols are resolved more correctly), an OpenAI-API-compatible LLM can be used to preprocess docstrings:
```sh
$ python main.py --project_name test --project_path <path> --converter function_comment_llm --cc_openai_base_url <url> --cc_openai_api_key <key> --cc_llm_model <model>
```

If desired, all components of the toolchain can be disabled individually (`disable_doc_gen`for *documentation generation* and `disable_test_cov` for *test coverage evaluation*).  
Some recommended additional options would be `--project_number` and `--project_brief`.  
For all possible options, see:
```sh
$ python main.py --help
```

## File Hierarchy
TODO

 
