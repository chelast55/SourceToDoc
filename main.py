from os import chdir, system
from pathlib import Path
from argparse import Namespace

from sourcetodoc.helpers import delete_directory_if_exists
from sourcetodoc.cli.ConfiguredParser import ConfiguredParser

if __name__ == "__main__":
    args: Namespace = ConfiguredParser().parse_args()

    html_theme: str = "sphinx_rtd_theme"
    exhale_root_file_name: str = f"root_{args.project_name}"

    # Paths
    generated_docs_main_path: Path = Path("out")  # Path conf.py will be placed, everything Sphinx related is rel. to it
    project_path: Path = generated_docs_main_path.parent.absolute() / Path(args.project_name)
    doxygen_awesome_submodule_path: Path \
        = generated_docs_main_path.parent.absolute() / Path("submodules") / Path("doxygen-awesome-css")

    doc_path: Path = Path("doc") / Path(args.project_name)  # TODO: option to reverse those with a CLI parameter
    doc_path_abs: Path = generated_docs_main_path.absolute() / doc_path
    doc_source_path: Path = doc_path / Path("src")
    doc_source_path_abs: Path = doc_path_abs / Path("src")
    doxygen_path: Path = Path()
    warning_log_file_path: Path = doxygen_path / Path("doxygen_warnings.txt")
    if args.apidoc_toolchain == "doxygen-only":
        doxygen_path = doc_path
    elif args.apidoc_toolchain == "sphinx-based":
        doxygen_path = doc_source_path_abs / Path("doxygen")
    sphinx_path: Path = doc_path_abs  # Sphinx (or rather its index.html) is the "main artifact"
    exhale_containment_path: Path = doc_source_path / Path("exhale")
    exhale_containment_path_abs: Path = doc_source_path_abs / Path("exhale")
    exhale_include_path: Path = doc_path / exhale_containment_path
    graphviz_dot_path: Path = Path(r"C:\Program Files\Graphviz\bin\dot.exe")  # TODO: this needs to be addressed
    stylesheet_path: Path = doxygen_awesome_submodule_path / Path("doxygen-awesome.css")

    # conditions
    doxygen_xml_required: bool = not args.apidoc_toolchain == "doxygen"
    doxygen_html_required: bool = args.apidoc_toolchain == "doxygen"

    # file contents
    DOXYFILE_CONTENT: str = f"""
        # Project related configuration options
        DOXYFILE_ENCODING      = UTF-8
        PROJECT_NAME           = {args.project_name}
        PROJECT_NUMBER         = {args.project_number}
        PROJECT_BRIEF          = {args.project_brief}
        PROJECT_LOGO           = {args.project_logo if (args.project_logo is not None and Path(args.project_logo).is_file()) else ""}
        PROJECT_ICON           = {args.project_icon if (args.project_icon is not None and Path(args.project_icon).is_file()) else ""}
        OUTPUT_DIRECTORY       = {str(doxygen_path).replace('\\', '\\\\')}
        CREATE_SUBDIRS         = NO
        ALLOW_UNICODE_NAMES    = NO
        OUTPUT_LANGUAGE        = {args.output_language}
        BRIEF_MEMBER_DESC      = {"YES" if args.no_brief_member_desc else "NO"}
        REPEAT_BRIEF           = {"YES" if args.no_repeat_brief else "NO"}
        ABBREVIATE_BRIEF       = "The $name class" \
                                 "The $name widget" \
                                 "The $name file" \
                                 is \
                                 provides \
                                 specifies \
                                 contains \
                                 represents \
                                 a \
                                 an \
                                 the
        ALWAYS_DETAILED_SEC    = {"YES" if args.always_detailed_sec else "NO"}
        INLINE_INHERITED_MEMB  = {"YES" if args.inline_inherited_memb else "NO"}
        FULL_PATH_NAMES        = {"YES" if args.disable_full_path_names else "NO"}
        FULL_PATH_NAMES        = {"YES" if args.disable_full_path_names else "NO"}
        STRIP_FROM_PATH        = {str(project_path).replace('\\', '\\\\')}
        STRIP_FROM_INC_PATH    = 
        SHORT_NAMES            = NO
        JAVADOC_AUTOBRIEF      = NO
        JAVADOC_BANNER         = YES
        QT_AUTOBRIEF           = NO
        MULTILINE_CPP_IS_BRIEF = NO
        PYTHON_DOCSTRING       = YES
        INHERIT_DOCS           = YES
        SEPARATE_MEMBER_PAGES  = {"YES" if args.separate_member_pages else "NO"}
        TAB_SIZE               = {args.tab_size}
        ALIASES                =
        OPTIMIZE_OUTPUT_FOR_C  = {"YES" if args.optimize_output_for_c else "NO"}
        OPTIMIZE_OUTPUT_JAVA   = NO
        OPTIMIZE_FOR_FORTRAN   = NO
        OPTIMIZE_OUTPUT_VHDL   = NO
        OPTIMIZE_OUTPUT_SLICE  = NO
        EXTENSION_MAPPING      = 
        MARKDOWN_SUPPORT       = YES
        TOC_INCLUDE_HEADINGS   = {args.toc_include_headings}
        MARKDOWN_ID_STYLE      = {args.markdown_id_style}
        AUTOLINK_SUPPORT       = YES
        BUILTIN_STL_SUPPORT    = YES
        CPP_CLI_SUPPORT        = NO
        SIP_SUPPORT            = {"YES" if args.sip_support else "NO"}
        IDL_PROPERTY_SUPPORT   = {"YES" if args.disable_idl_property_support else "NO"}
        DISTRIBUTE_GROUP_DOC   = NO
        GROUP_NESTED_COMPOUNDS = {"YES" if args.group_nested_compounds else "NO"}
        SUBGROUPING            = {"YES" if args.disable_subgrouping else "NO"}
        INLINE_GROUPED_CLASSES = {"YES" if args.inline_grouped_classes else "NO"}
        INLINE_SIMPLE_STRUCTS  = {"YES" if args.inline_simple_structs else "NO"}
        TYPEDEF_HIDES_STRUCT   = {"YES" if args.typedef_hides_struct else "NO"}
        LOOKUP_CACHE_SIZE      = {2 if args.small_lookup_cache else 9}
        NUM_PROC_THREADS       = 0
        TIMESTAMP              = {args.timestamp}
        
        # Build related configuration options
        EXTRACT_ALL             = YES
        EXTRACT_PRIVATE         = {"YES" if args.disable_extract_private else "NO"}
        EXTRACT_PRIV_VIRTUAL    = {"YES" if args.disable_extract_private_virtual else "NO"}
        EXTRACT_PACKAGE         = {"YES" if args.disable_extract_package else "NO"}
        EXTRACT_STATIC          = {"YES" if args.disable_extract_static else "NO"}
        EXTRACT_LOCAL_CLASSES   = {"YES" if args.disable_extract_local_classes else "NO"}
        EXTRACT_LOCAL_METHODS   = NO
        EXTRACT_ANON_NSPACES    = {"YES" if args.disable_extract_anon_namespaces else "NO"}
        RESOLVE_UNNAMED_PARAMS  = YES
        HIDE_FRIEND_COMPOUNDS   = YES
        HIDE_IN_BODY_DOCS       = NO
        INTERNAL_DOCS           = YES
        CASE_SENSE_NAMES        = SYSTEM
        HIDE_SCOPE_NAMES        = {"YES" if args.hide_scope_names else "NO"}
        HIDE_COMPOUND_REFERENCE = {"YES" if args.hide_compound_reference else "NO"}
        SHOW_HEADERFILE         = {"YES" if args.disable_show_headerfile else "NO"}
        SHOW_INCLUDE_FILES      = {"YES" if args.disable_show_include_files else "NO"}
        SHOW_GROUPED_MEMB_INC   = {"YES" if args.disable_show_grounded_member_include else "NO"}
        
        # Configuration options related to warning and progress messages
        QUIET                  = NO
        WARNINGS               = {"YES" if args.disable_doxygen_warnings else "NO"}
        WARN_IF_DOC_ERROR      = YES
        WARN_IF_INCOMPLETE_DOC = YES
        WARN_AS_ERROR          = NO
        WARN_LOGFILE           = {str(warning_log_file_path).replace('\\', '\\\\')}
        
        # Configuration options related to the input files
        INPUT                   = {str(project_path).replace('\\', '\\\\') if (args.input is None) else args.input}
        INPUT_ENCODING          = {args.input_encoding}
        INPUT_FILE_ENCODING     = {args.input_file_encoding}
        FILE_PATTERNS           =    *.c \
                                     *.cc \
                                     *.cxx \
                                     *.cxxm \
                                     *.cpp \
                                     *.cppm \
                                     *.ccm \
                                     *.c++ \
                                     *.c++m \
                                     *.java \
                                     *.ii \
                                     *.ixx \
                                     *.ipp \
                                     *.i++ \
                                     *.inl \
                                     *.idl \
                                     *.ddl \
                                     *.odl \
                                     *.h \
                                     *.hh \
                                     *.hxx \
                                     *.hpp \
                                     *.h++ \
                                     *.ixx \
                                     *.l \
                                     *.cs \
                                     *.d \
                                     *.php \
                                     *.php4 \
                                     *.php5 \
                                     *.phtml \
                                     *.inc \
                                     *.m \
                                     *.markdown \
                                     *.md \
                                     *.mm \
                                     *.dox \
                                     *.py \
                                     *.pyw \
                                     *.f90 \
                                     *.f95 \
                                     *.f03 \
                                     *.f08 \
                                     *.f18 \
                                     *.f \
                                     *.for \
                                     *.vhd \
                                     *.vhdl \
                                     *.ucf \
                                     *.qsf \
                                     *.ice \
                                     *.txt
        RECURSIVE               = YES
        EXCLUDE_SYMLINKS        = {"YES" if args.exclude_symlinks else "NO"}
        #IMAGE_PATH             =
        #INPUT_FILTER           =
        #FILTER_PATTERNS        =
        #FILTER_SOURCE_FILES    =
        #FILTER_SOURCE_PATTERNS =
        USE_MDFILE_AS_MAINPAGE  = TODO: locate readme
        
        # Configuration options related to source browsing
        SOURCE_BROWSER          = {"YES" if args.disable_source_browser else "NO"}
        INLINE_SOURCES          = {"YES" if args.inline_sources else "NO"}
        STRIP_CODE_COMMENTS     = {"YES" if args.disable_strip_code_comments else "NO"}
        REFERENCED_BY_RELATION  = {"YES" if args.disable_referenced_by_relation else "NO"}
        REFERENCES_RELATION     = {"YES" if args.disable_references_relation else "NO"}
        #REFERENCES_LINK_SOURCE  =
        #SOURCE_TOOLTIPS         =
        #USE_HTAGS               =
        #VERBATIM_HEADERS        =
        #CLANG_ASSISTED_PARSING  =
        #CLANG_ADD_INC_PATHS     =
        #CLANG_OPTIONS           =
        #CLANG_DATABASE_PATH     =
        
        # Configuration options related to the alphabetical class index
        ALPHABETICAL_INDEX = YES
        
        # Configuration options related to the HTML output
        GENERATE_HTML         = {"YES" if doxygen_html_required else "NO"}
        HTML_OUTPUT           = {"" if doxygen_html_required else "html"}
        HTML_FILE_EXTENSION   = html
        HTML_HEADER           = {str(args.html_header).replace('\\', '\\\\')}
        HTML_FOOTER           = {str(args.html_footer).replace('\\', '\\\\')}
        HTML_STYLESHEET       = {str(stylesheet_path).replace('\\', '\\\\')}
        HTML_EXTRA_STYLESHEET = {str(args.html_extra_stylesheet).replace('\\', '\\\\')}
        
        # Configuration options related to the LaTeX output
        GENERATE_LATEX         = NO
        
        # Configuration options related to the RTF output
        
        # Configuration options related to the man page output
        
        # Configuration options related to the XML output
        GENERATE_XML            = {"YES" if (doxygen_xml_required or args.disable_generate_doxygen_xml) else "NO"}
        XML_OUTPUT              = xml
        XML_PROGRAMLISTING      = YES
        XML_NS_MEMB_FILE_SCOPE  = YES
        
        # Configuration options related to the Perl module output
        
        # Configuration options related to the preprocessor
        ENABLE_PREPROCESSING    = YES
        MACRO_EXPANSION         = {"YES" if args.disable_macro_expansion else "NO"}
        EXPAND_ONLY_PREDEF      = NO
        SKIP_FUNCTION_MACROS    = {"YES" if args.disable_skip_function_macros else "NO"}
        
        # Configuration options related to diagram generator tools

        # OPTIMIZE_OUTPUT_FOR_C  = YES
        SORT_MEMBERS_CTORS_1ST = YES
        GENERATE_AUTOGEN_DEF   = YES # EXPERIMENTAL
        HIDE_UNDOC_RELATIONS   = YES
        GENERATE_TREEVIEW = YES
        HAVE_DOT = YES
        CLASS_GRAPH = YES
        COLLABORATION_GRAPH = YES
        UML_LOOK = YES
        UML_LIMIT_NUM_FIELDS   = 50
        DOT_UML_DETAILS = YES
        TEMPLATE_RELATIONS     = YES
        INCLUDE_GRAPH = YES
        INCLUDED_BY_GRAPH = YES
        CALL_GRAPH = YES
        CALLER_GRAPH = YES
        GRAPHICAL_HIERARCHY = YES
        DIRECTORY_GRAPH = YES
        DOT_IMAGE_FORMAT = svg
        INTERACTIVE_SVG = YES
        DOT_PATH = {str(graphviz_dot_path).replace('\\', '\\\\') if not graphviz_dot_path is None else ""}
        DOT_MULTI_TARGETS      = YES
        HTML_COLORSTYLE = LIGHT  # required with Doxygen >= 1.9.5
    """

    INDEX_RST_CONTENT: str = f"""
    Welcome to {args.project_name}'s documentation!
    ============================{"="*len(args.project_name)}
        
    .. toctree::
        :maxdepth: 2
        :caption: Contents:
    
        {str(exhale_containment_path).replace('\\', '/') + "/" + exhale_root_file_name}
    
    Only to proof that graphs are included and until this is properly handled with exhale
    
    .. doxygenindex::
        :allow-dot-graphs:
    
    Indices and tables
    ==================
    
    * :ref:`genindex`
    * :ref:`search`
    """

    CONF_PY_CONTENT: str = f"""
    # Configuration file for the Sphinx documentation builder.
    
    # For the full list of built-in configuration values, see the documentation:
    # https://www.sphinx-doc.org/en/master/usage/configuration.html
    
    # -- Project information -----------------------------------------------------
    # https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
    from pathlib import Path
    from exhale import utils as exhale_utils
    
    project = "{args.project_name}"
    copyright = "{args.project_year}, {args.project_author}"
    author = "{args.project_author}"
    release = "{args.project_number}"
    
    project_path: Path = Path(r"{str(project_path)}")
    doxygen_path: Path = Path(r"{str(doxygen_path)}")
    sphinx_path: Path = Path(r"{str(sphinx_path)}")
    exhale_path: Path = Path(r"{str(exhale_containment_path)}")
    graphviz_dot_path: Path = Path(r"{str(graphviz_dot_path)}")
            
    graphviz_output_format = "svg"
    # graphviz_dot_args = ["-Gbgcolor=#FF00FF", "-Ncolor=#ffffff", "-Ecolor=#00ff00"]
    graphviz_dot = str(graphviz_dot_path)
    
    # -- General configuration ---------------------------------------------------
    # https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration
    
    templates_path = ["_templates"]
    exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
    
    # -- Options for HTML output -------------------------------------------------
    # https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output
    
    html_theme = "{html_theme}"
    
    extensions = ["sphinx.ext.graphviz", "sphinx.ext.autodoc", "sphinx.ext.autosummary", "myst_parser"]
    """

    CONF_PY_EXHALE_EXTENSION = f"""
    # -- Additional configuration ---------------------------------------------------
    
    extensions += ["breathe", "exhale"]
    
    def specifications_for_kind(kind):
        \"\"\"
        For a given input ``kind``, return the list of reStructuredText specifications
        for the associated Breathe directive.
        \"\"\"
        # Change the defaults for .. doxygenclass:: and .. doxygenstruct::
        if kind == "class" or kind == "struct" or kind == "file":
            print("Doxygenclass or struct encountered and overriting")
            return [
                ":members:",
                ":protected-members:",
                ":private-members:",
                ":undoc-members:",
                ":allow-dot-graphs:"
            ]
        # An empty list signals to Exhale to use the defaults
        else:
            print("Something else encountered")
            return []
            
    # -- Breathe configuration ---------------------------------------------------
    breathe_projects = {{
        "{args.project_name}": str(doxygen_path / Path("xml"))
    }}
    breathe_default_project = "{args.project_name}"
    primary_domain = "cpp"
    highlight_language="cpp"
    
    # -- Exhale configuration ---------------------------------------------------
    exhale_args = {{
        # These arguments are required
        "containmentFolder": str(exhale_path.absolute()),
        "rootFileName": "{exhale_root_file_name}.rst",
        "rootFileTitle": "{args.project_name} API",
        "doxygenStripFromPath": str(sphinx_path.absolute()),
        "fullToctreeMaxDepth": 1,
        # Suggested optional arguments
        "createTreeView": True,
        # TIP: if using the sphinx-bootstrap-theme, you need
        #"treeViewIsBootstrap": True,
        "exhaleExecutesDoxygen": True,
        "exhaleDoxygenStdin": {DOXYFILE_CONTENT},
        "verboseBuild": True, # DEBUG
        "generateBreatheFileDirectives": True, # DEBUG
        "customSpecificationsMapping": exhale_utils.makeCustomSpecificationsMapping(specifications_for_kind)
    }}
    
    """

    # delete artifacts from prior builds and ensure paths exist TODO: move to end as cleenup, when debugging is done
    delete_directory_if_exists(doc_path_abs)
    doc_path_abs.mkdir(parents=True, exist_ok=True)
    doxygen_path.mkdir(parents=True, exist_ok=True)
    if not graphviz_dot_path.exists():
        raise OSError("dot.exe not found at given path")
    chdir(generated_docs_main_path)

    if args.apidoc_toolchain == "doxygen-only":
        # generate config file for Doxygen
        with open(Path("Doxyfile.in"), "w+") as doxyfile:
            doxyfile.write(DOXYFILE_CONTENT)

        # run doxygen
        system("doxygen Doxyfile.in")

    elif args.apidoc_toolchain == "sphinx-based":
        # this path is only here for reference and may be (partially) broken
        print("!!! Disclaimer: Using sphinx-based is currently not recommended and may not work at all.")

        sphinx_path.mkdir(parents=True, exist_ok=True)
        exhale_containment_path_abs.mkdir(parents=True, exist_ok=True)

        # generate config files for sphinx+breathe+exhale+doxygen
        with open(Path("index.rst"), "w+") as index_rst_file:
            index_rst_file.write(INDEX_RST_CONTENT)
        with open(Path("conf.py"), "w+") as conf_py_file:
            conf_py_file.write(CONF_PY_CONTENT + CONF_PY_EXHALE_EXTENSION)

        # run sphinx+breath+exhale+doxygen
        print("\n--------------------")
        print("Generate sphinx...")
        system(f"sphinx-build -b html . {sphinx_path}")

        # exhale output post processings
        # TODO: implement
        #delete_directory_if_exists(exhale_containment_path)  # DEBUG
        #delete_directory_if_exists(sphinx_path / Path("doc"))  # DEBUG
        #system(f"breathe-apidoc -o {exhale_containment_path} -m {str(doxygen_path / Path("xml"))}")  # DEBUG

        # adjust sphinx config for second run
        with open(Path("conf.py"), "w+") as conf_py_file:
            conf_py_file.write(CONF_PY_CONTENT)

        # run sphinx again
        # maybe some cleanup is necessary?
        #system(f"sphinx-build -b html . {sphinx_path}")
