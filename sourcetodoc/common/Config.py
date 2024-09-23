from argparse import Namespace
from pathlib import Path
from typing import Optional

from sourcetodoc.common.wizard import run_wizard


class Config:
    
    def __init__(self, args: Namespace):
        self.args: Namespace = args

        self.out_path_relative: Path = Path()
        self.out_path: Path = Path()
        self.root_path: Path = Path()
        self.project_path: Path = Path()
        self.doxygen_awesome_submodule_path: Path = Path()
        self.doc_path: Path = Path()
        self.doc_path_abs: Path = Path()
        self.doc_source_path: Path = Path()
        self.doc_source_path_abs: Path = Path()
        self.doxygen_path: Path = Path()
        self.doxygen_warning_log_file_path: Path = Path()
        self.doxygen_stylesheet_path: Path | None = Path()
        self.sphinx_path: Path = Path()
        self.exhale_containment_path: Path = Path()
        self.exhale_containment_path_abs: Path = Path()
        self.exhale_include_path: Path = Path()
        self.testcoveragereport_path: Path = Path()

        self.readme_file_path: Optional[Path] = None

        self.DOXYFILE_CONTENT: str = ""
        self.INDEX_RST_CONTENT: str = ""
        self.CONF_PY_CONTENT: str = ""
        self.CONF_PY_EXHALE_EXTENSION: str = ""

        # wizard
        if self.args.wizard:
            run_wizard(self.args)

        # Non-trivial argument requirements
        if self.args.converter is not None:
            if self.args.project_name is None:
                raise ValueError(
                    f"Missing argument: --project_name\n"
                    f"When using the documentation generation or test coverage evaluation parts of the toolchain, "
                    f"a project name must be provided!"
                )
        elif self.args.project_name is None and self.args.project_path is None:
            raise ValueError(
                f"Missing argument: --project_path OR --project_name\n"
                f"Path to project source files must be either provided explicitly (--project_path) or indirectly via "
                f"the project name (--project_name) "
            )
    
        # region paths
        self.root_path = Path(__file__).parent.parent.parent
        self.out_path_relative = Path("out")
        self.out_path = self.root_path / self.out_path_relative  # Path conf.py will be placed, everything Doxygen/Sphinx related is rel. to it
        self.project_path = self.root_path / Path(self.args.project_name) if (self.args.project_path is None) else Path(self.args.project_path)
        self.doxygen_awesome_submodule_path = self.root_path / Path("submodules") / Path("doxygen-awesome-css")
    
        self.doc_path = Path(self.args.project_name) / Path("doc")
        self.doc_path_abs = self.out_path / self.doc_path
        self.doc_source_path = self.doc_path / Path("src")
        self.doc_source_path_abs = self.doc_path_abs / Path("src")
        if self.args.apidoc_toolchain == "doxygen-only":
            self.doxygen_path = self.doc_path_abs
        elif self.args.apidoc_toolchain == "sphinx-based":
            self.doxygen_path = self.doc_source_path_abs / Path("doxygen")
        else:
            raise Exception(f"self.args.apidoc_toolchain == {self.args.apidoc_toolchain} should not happen")
        self.doxygen_warning_log_file_path = self.doxygen_path / Path("doxygen_warnings.txt")
        self.doxygen_stylesheet_path = self.doxygen_awesome_submodule_path / Path("doxygen-awesome.css") \
            if (self.args.dg_html_theme == "doxygen-awesome") else None
        self.sphinx_path = self.doc_path_abs  # Sphinx (or rather its index.html) is the "main artifact"
        self.exhale_containment_path = self.doc_source_path / Path("exhale")
        self.exhale_containment_path_abs = self.doc_source_path_abs / Path("exhale")
        self.exhale_include_path = self.doc_path / self.exhale_containment_path

        self.testcoveragereport_path = self.out_path / Path(self.args.project_name) / Path("testcoveragereport")
        # endregion paths
    
        # conditions
        doxygen_xml_required: bool = not self.args.apidoc_toolchain == "doxygen-only"
        doxygen_html_required: bool = self.args.apidoc_toolchain == "doxygen-only"
    
        # locate README
        potential_readme_files: list[Path] = [file for file in self.project_path.glob("**/*") if file.is_file()]
        for potential_readme_file in potential_readme_files:  # search for specific "generic" README, in case there are multiple readme files
            if potential_readme_file.is_file() and (
                    "README.MD" in str(potential_readme_file).upper()[-9:] or
                    "README" in str(potential_readme_file).upper()[-6:] or
                    "README.TXT" in str(potential_readme_file).upper()[-10:]
            ):
                self.readme_file_path = potential_readme_file
                break
        if self.readme_file_path is None:  # broader search if no README is found in first step
            for potential_readme_file in potential_readme_files:
                if potential_readme_file.is_file() \
                        and "READ" in str(potential_readme_file).upper() and "ME" in str(potential_readme_file).upper():
                    self.readme_file_path = potential_readme_file
                    break
    
        # additional doxygen
        match self.args.dg_dot_uml_details:
            case "ALL":
                dot_uml_details_translated: str = "YES"
            case "SIMPLIFIED":
                dot_uml_details_translated: str = "NO"
            case "NONE":
                dot_uml_details_translated: str = "NONE"
            case _:
                raise Exception(f"self.args.dot_uml_details_translated == {self.args.dot_uml_details_translated} should not happen")
    
        # additional sphinx-specific
        sphinx_html_theme: str = "sphinx_rtd_theme"
        exhale_root_file_name: str = f"root_{self.args.project_name}"
    
        # region file contents
        self.DOXYFILE_CONTENT = f"""
                # Project related configuration options
                DOXYFILE_ENCODING      = UTF-8
                PROJECT_NAME           = {self.args.project_name}
                PROJECT_NUMBER         = {self.args.project_number}
                PROJECT_BRIEF          = {self.args.project_brief}
                PROJECT_LOGO           = {self.args.project_logo if (self.args.project_logo is not None and Path(self.args.project_logo).is_file()) else ""}
                PROJECT_ICON           = {self.args.project_icon if (self.args.project_icon is not None and Path(self.args.project_icon).is_file()) else ""}
                OUTPUT_DIRECTORY       = {str(self.doxygen_path).replace('\\', '\\\\')}
                CREATE_SUBDIRS         = NO
                ALLOW_UNICODE_NAMES    = NO
                OUTPUT_LANGUAGE        = {self.args.dg_output_language}
                BRIEF_MEMBER_DESC      = {"YES" if self.args.dg_no_brief_member_desc else "NO"}
                REPEAT_BRIEF           = {"YES" if self.args.dg_no_repeat_brief else "NO"}
                ABBREVIATE_BRIEF       = "The $name class" \\
                                         "The $name widget" \\
                                         "The $name file" \\
                                         is \\
                                         provides \\
                                         specifies \\
                                         contains \\
                                         represents \\
                                         a \\
                                         an \\
                                         the
                ALWAYS_DETAILED_SEC    = {"YES" if self.args.dg_always_detailed_sec else "NO"}
                INLINE_INHERITED_MEMB  = {"YES" if self.args.dg_inline_inherited_memb else "NO"}
                FULL_PATH_NAMES        = {"YES" if self.args.dg_disable_full_path_names else "NO"}
                FULL_PATH_NAMES        = {"YES" if self.args.dg_disable_full_path_names else "NO"}
                STRIP_FROM_PATH        = {str(self.project_path).replace('\\', '\\\\')}
                STRIP_FROM_INC_PATH    = 
                SHORT_NAMES            = NO
                JAVADOC_AUTOBRIEF      = NO
                JAVADOC_BANNER         = YES
                QT_AUTOBRIEF           = NO
                MULTILINE_CPP_IS_BRIEF = NO
                PYTHON_DOCSTRING       = YES
                INHERIT_DOCS           = YES
                SEPARATE_MEMBER_PAGES  = {"YES" if self.args.dg_separate_member_pages else "NO"}
                TAB_SIZE               = {self.args.dg_tab_size}
                ALIASES                =
                OPTIMIZE_OUTPUT_FOR_C  = {"YES" if self.args.dg_optimize_output_for_c else "NO"}
                OPTIMIZE_OUTPUT_JAVA   = NO
                OPTIMIZE_FOR_FORTRAN   = NO
                OPTIMIZE_OUTPUT_VHDL   = NO
                OPTIMIZE_OUTPUT_SLICE  = NO
                EXTENSION_MAPPING      = 
                MARKDOWN_SUPPORT       = YES
                TOC_INCLUDE_HEADINGS   = {self.args.dg_toc_include_headings}
                MARKDOWN_ID_STYLE      = {self.args.dg_markdown_id_style}
                AUTOLINK_SUPPORT       = YES
                BUILTIN_STL_SUPPORT    = YES
                CPP_CLI_SUPPORT        = NO
                SIP_SUPPORT            = {"YES" if self.args.dg_sip_support else "NO"}
                IDL_PROPERTY_SUPPORT   = {"YES" if self.args.dg_disable_idl_property_support else "NO"}
                DISTRIBUTE_GROUP_DOC   = NO
                GROUP_NESTED_COMPOUNDS = {"YES" if self.args.dg_group_nested_compounds else "NO"}
                SUBGROUPING            = {"YES" if self.args.dg_disable_subgrouping else "NO"}
                INLINE_GROUPED_CLASSES = {"YES" if self.args.dg_inline_grouped_classes else "NO"}
                INLINE_SIMPLE_STRUCTS  = {"YES" if self.args.dg_inline_simple_structs else "NO"}
                TYPEDEF_HIDES_STRUCT   = {"YES" if self.args.dg_typedef_hides_struct else "NO"}
                LOOKUP_CACHE_SIZE      = {2 if self.args.dg_small_lookup_cache else 9}
                NUM_PROC_THREADS       = 0
                TIMESTAMP              = {self.args.dg_timestamp}
        
                # Build related configuration options
                EXTRACT_ALL             = YES
                EXTRACT_PRIVATE         = {"YES" if self.args.dg_disable_extract_private else "NO"}
                EXTRACT_PRIV_VIRTUAL    = {"YES" if self.args.dg_disable_extract_private_virtual else "NO"}
                EXTRACT_PACKAGE         = {"YES" if self.args.dg_disable_extract_package else "NO"}
                EXTRACT_STATIC          = {"YES" if self.args.dg_disable_extract_static else "NO"}
                EXTRACT_LOCAL_CLASSES   = {"YES" if self.args.dg_disable_extract_local_classes else "NO"}
                EXTRACT_LOCAL_METHODS   = NO
                EXTRACT_ANON_NSPACES    = {"YES" if self.args.dg_disable_extract_anon_namespaces else "NO"}
                RESOLVE_UNNAMED_PARAMS  = YES
                HIDE_FRIEND_COMPOUNDS   = YES
                HIDE_IN_BODY_DOCS       = NO
                INTERNAL_DOCS           = YES
                CASE_SENSE_NAMES        = SYSTEM
                HIDE_SCOPE_NAMES        = {"YES" if self.args.dg_hide_scope_names else "NO"}
                HIDE_COMPOUND_REFERENCE = {"YES" if self.args.dg_hide_compound_reference else "NO"}
                SHOW_HEADERFILE         = {"YES" if self.args.dg_disable_show_headerfile else "NO"}
                SHOW_INCLUDE_FILES      = {"YES" if self.args.dg_disable_show_include_files else "NO"}
                SHOW_GROUPED_MEMB_INC   = {"YES" if self.args.dg_disable_show_grouped_member_include else "NO"}
        
                # Configuration options related to warning and progress messages
                QUIET                  = NO
                WARNINGS               = {"YES" if self.args.dg_disable_warnings else "NO"}
                WARN_IF_DOC_ERROR      = YES
                WARN_IF_INCOMPLETE_DOC = YES
                WARN_AS_ERROR          = NO
                WARN_LOGFILE           = {str(self.doxygen_warning_log_file_path).replace('\\', '\\\\')}
        
                # Configuration options related to the input files
                INPUT                   = {str(self.project_path).replace('\\', '\\\\')}
                INPUT_ENCODING          = {self.args.dg_input_encoding}
                INPUT_FILE_ENCODING     = {"" if (self.args.dg_input_file_encoding is None) else self.args.dg_input_file_encoding}
                FILE_PATTERNS           =    *.c \\
                                             *.cc \\
                                             *.cxx \\
                                             *.cxxm \\
                                             *.cpp \\
                                             *.cppm \\
                                             *.ccm \\
                                             *.c++ \\
                                             *.c++m \\
                                             *.java \\
                                             *.ii \\
                                             *.ixx \\
                                             *.ipp \\
                                             *.i++ \\
                                             *.inl \\
                                             *.idl \\
                                             *.ddl \\
                                             *.odl \\
                                             *.h \\
                                             *.hh \\
                                             *.hxx \\
                                             *.hpp \\
                                             *.h++ \\
                                             *.ixx \\
                                             *.l \\
                                             *.cs \\
                                             *.d \\
                                             *.php \\
                                             *.php4 \\
                                             *.php5 \\
                                             *.phtml \\
                                             *.inc \\
                                             *.m \\
                                             *.markdown \\
                                             *.md \\
                                             *.mm \\
                                             *.dox \\
                                             *.py \\
                                             *.pyw \\
                                             *.f90 \\
                                             *.f95 \\
                                             *.f03 \\
                                             *.f08 \\
                                             *.f18 \\
                                             *.f \\
                                             *.for \\
                                             *.vhd \\
                                             *.vhdl \\
                                             *.ucf \\
                                             *.qsf \\
                                             *.ice \\
                                             *.txt
                RECURSIVE               = YES
                EXCLUDE_SYMLINKS        = {"YES" if self.args.dg_exclude_symlinks else "NO"}
                #IMAGE_PATH             =
                #INPUT_FILTER           =
                #FILTER_PATTERNS        =
                #FILTER_SOURCE_FILES    =
                #FILTER_SOURCE_PATTERNS =
                USE_MDFILE_AS_MAINPAGE  = {"" if (self.readme_file_path is None) else str(self.readme_file_path).replace('\\', '\\\\')}
        
                # Configuration options related to source browsing
                SOURCE_BROWSER          = {"YES" if self.args.dg_disable_source_browser else "NO"}
                INLINE_SOURCES          = {"YES" if self.args.dg_inline_sources else "NO"}
                STRIP_CODE_COMMENTS     = {"YES" if self.args.dg_disable_strip_code_comments else "NO"}
                REFERENCED_BY_RELATION  = {"YES" if self.args.dg_disable_referenced_by_relation else "NO"}
                REFERENCES_RELATION     = {"YES" if self.args.dg_disable_references_relation else "NO"}
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
                HTML_OUTPUT           = {str(Path("")) if (self.args.apidoc_toolchain == "doxygen-only") else "html"}
                HTML_FILE_EXTENSION   = .html
                HTML_HEADER           = {"" if (self.args.dg_html_header is None) else str(self.args.dg_html_header).replace('\\', '\\\\')}
                HTML_FOOTER           = {"" if (self.args.dg_html_footer is None) else str(self.args.dg_html_footer).replace('\\', '\\\\')}
                HTML_STYLESHEET       = {str(self.doxygen_stylesheet_path).replace('\\', '\\\\') if (self.doxygen_stylesheet_path is not None) else ""}
                HTML_EXTRA_STYLESHEET = {"" if (self.args.dg_html_extra_stylesheet is None) else str(self.args.dg_html_extra_stylesheet).replace('\\', '\\\\')}
        
                # Configuration options related to the LaTeX output
                GENERATE_LATEX         = NO
        
                # Configuration options related to the RTF output
        
                # Configuration options related to the man page output
        
                # Configuration options related to the XML output
                GENERATE_XML            = {"YES" if (doxygen_xml_required or self.args.dg_disable_generate_xml) else "NO"}
                XML_OUTPUT              = xml
                XML_PROGRAMLISTING      = YES
                XML_NS_MEMB_FILE_SCOPE  = YES
        
                # Configuration options related to the Perl module output
        
                # Configuration options related to the preprocessor
                ENABLE_PREPROCESSING    = YES
                MACRO_EXPANSION         = {"YES" if self.args.dg_disable_macro_expansion else "NO"}
                EXPAND_ONLY_PREDEF      = NO
                SKIP_FUNCTION_MACROS    = {"YES" if self.args.dg_disable_skip_function_macros else "NO"}
        
                # Configuration options related to diagram generator tools
                HIDE_UNDOC_RELATIONS    = NO
                HAVE_DOT                = {"YES" if self.args.dg_disable_dot_graphs else "NO"}
                DOT_NUM_THREADS         = 0
                #DOT_COMMON_ATTR         =
                #DOT_EDGE_ATTR           = 
                #DOT_NODE_ATTR           = 
                #DOT_FONTPATH            =
                CLASS_GRAPH             = {"YES" if self.args.dg_disable_dot_graphs else "NO"}
                COLLABORATION_GRAPH     = {"YES" if self.args.dg_disable_dot_graphs else "NO"}
                GROUP_GRAPHS            = {"YES" if self.args.dg_disable_dot_graphs else "NO"}
                UML_LOOK                = {"YES" if self.args.dg_disable_uml_look else "NO"}
                UML_LIMIT_NUM_FIELDS    = {self.args.dg_uml_limit_num_fields if not self.args.dg_uml_limit_num_fields == 0 else 100}
                DOT_UML_DETAILS         = {dot_uml_details_translated}
                DOT_WRAP_THRESHOLD      = 20
                TEMPLATE_RELATIONS      = {"YES" if self.args.dg_disable_template_relations else "NO"}
                INCLUDE_GRAPH           = {"YES" if self.args.dg_disable_dot_graphs else "NO"}
                INCLUDED_BY_GRAPH       = {"YES" if self.args.dg_disable_dot_graphs else "NO"}
                CALL_GRAPH              = {"YES" if self.args.dg_disable_dot_graphs else "NO"}
                CALLER_GRAPH            = {"YES" if self.args.dg_disable_dot_graphs else "NO"}
                GRAPHICAL_HIERARCHY     = {"YES" if self.args.dg_disable_dot_graphs else "NO"}
                DIRECTORY_GRAPH         = {"YES" if self.args.dg_disable_dot_graphs else "NO"}
                DIR_GRAPH_MAX_DEPTH     = 25
                DOT_IMAGE_FORMAT        = {self.args.dg_dot_image_format}
                INTERACTIVE_SVG         = YES
                DOT_PATH                = 
                DOTFILE_DIRS            = 
                DIA_PATH                = 
                DIAFILE_DIRS            = 
                PLANTUML_JAR_PATH       = {self.args.uml_plantuml_jar_path if self.args.uml_plantuml_jar_path is not None else ""}
                PLANTUML_CFG_FILE       = 
                PLANTUML_INCLUDE_PATH   = 
                DOT_GRAPH_MAX_NODES     = 1000
                MAX_DOT_GRAPH_DEPTH     = 0
                DOT_MULTI_TARGETS       = YES
                GENERATE_LEGEND         = YES
                DOT_CLEANUP             = {"YES" if self.args.dg_disable_dot_cleanup else "NO"}
                MSCGEN_TOOL             = 
                MSCFILE_DIRS            =
        
                # not properly inplemented but still set:
                # OPTIMIZE_OUTPUT_FOR_C  = YES
                SORT_MEMBERS_CTORS_1ST = YES
                GENERATE_AUTOGEN_DEF   = YES # EXPERIMENTAL
                HIDE_UNDOC_RELATIONS   = YES
                GENERATE_TREEVIEW = YES
                HTML_COLORSTYLE = {"DARK" if not (self.args.dg_html_theme == "doxygen_awesome") else "LIGHT"}  # required with Doxygen >= 1.9.5
            """
    
        self.INDEX_RST_CONTENT = f"""
            Welcome to {self.args.project_name}'s documentation!
            ============================{"=" * len(self.args.project_name)}
        
            .. toctree::
                :maxdepth: 2
                :caption: Contents:
        
                {str(self.exhale_containment_path).replace('\\', '/') + "/" + exhale_root_file_name}
        
            Only to proof that graphs are included and until this is properly handled with exhale
        
            .. doxygenindex::
                :allow-dot-graphs:
        
            Indices and tables
            ==================
        
            * :ref:`genindex`
            * :ref:`search`
            """
    
        self.CONF_PY_CONTENT = f"""
            # Configuration file for the Sphinx documentation builder.
        
            # For the full list of built-in configuration values, see the documentation:
            # https://www.sphinx-doc.org/en/master/usage/configuration.html
        
            # -- Project information -----------------------------------------------------
            # https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
            from pathlib import Path
            from exhale import utils as exhale_utils
        
            project = "{self.args.project_name}"
            copyright = "{self.args.project_year}, {self.args.project_author}"
            author = "{self.args.project_author}"
            release = "{self.args.project_number}"
        
            project_path: Path = Path(r"{str(self.project_path)}")
            doxygen_path: Path = Path(r"{str(self.doxygen_path)}")
            sphinx_path: Path = Path(r"{str(self.sphinx_path)}")
            exhale_path: Path = Path(r"{str(self.exhale_containment_path)}")
        
            graphviz_output_format = "svg"
            # graphviz_dot_self.args.= ["-Gbgcolor=#FF00FF", "-Ncolor=#ffffff", "-Ecolor=#00ff00"]
            graphviz_dot = str(graphviz_dot_path)
        
            # -- General configuration ---------------------------------------------------
            # https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration
        
            templates_path = ["_templates"]
            exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
        
            # -- Options for HTML output -------------------------------------------------
            # https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output
        
            html_theme = "{sphinx_html_theme}"
        
            extensions = ["sphinx.ext.graphviz", "sphinx.ext.autodoc", "sphinx.ext.autosummary", "myst_parser"]
            """
    
        self.CONF_PY_EXHALE_EXTENSION = f"""
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
                "{self.args.project_name}": str(doxygen_path / Path("xml"))
            }}
            breathe_default_project = "{self.args.project_name}"
            primary_domain = "cpp"
            highlight_language="cpp"
        
            # -- Exhale configuration ---------------------------------------------------
            exhale_self.args.= {{
                # These arguments are required
                "containmentFolder": str(exhale_path.absolute()),
                "rootFileName": "{exhale_root_file_name}.rst",
                "rootFileTitle": "{self.args.project_name} API",
                "doxygenStripFromPath": str(sphinx_path.absolute()),
                "fullToctreeMaxDepth": 1,
                # Suggested optional arguments
                "createTreeView": True,
                # TIP: if using the sphinx-bootstrap-theme, you need
                #"treeViewIsBootstrap": True,
                "exhaleExecutesDoxygen": True,
                "exhaleDoxygenStdin": {self.DOXYFILE_CONTENT},
                "verboseBuild": True, # DEBUG
                "generateBreatheFileDirectives": True, # DEBUG
                "customSpecificationsMapping": exhale_utils.makeCustomSpecificationsMapping(specifications_for_kind)
            }}
        
            """
        # endregion file contents
