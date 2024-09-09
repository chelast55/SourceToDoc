from pathlib import Path

def link_tc_report_and_documentation_main(out_path: Path, project_name: str):
    # Link coverage and documentation.
    # modify tcreport
    # TODO: Path-Änderung
    tc_report_main_file_path: Path = out_path / "testcoveragereport" / "index.html"
    marker_line_in_tc_file: str = f"""<tr><td class="title">LCOV - code coverage report</td></tr>"""
    # TODO: Path-Änderung
    link_to_dg_main_file: str = f"""    <tr><td class="headerItem" style="text-align: center"><a href="../doc/{project_name}/index.html">Go to the documentation.</a></td></tr>\n"""
    # with open(tc_report_main_file_path, "r+") as tc_report_file:
    #     tc_lines: list[str] = tc_report_file.readlines()
    #     for i, line in enumerate(tc_lines):
    #         if tc_marker_line in line:
    #             tc_lines.insert(i + 1, marker_line_in_tc_file)
    #             break
    #     tc_report_file.seek(0)
    #     tc_report_file.writelines(tc_lines)
    _insert_link(tc_report_main_file_path, marker_line_in_tc_file, link_to_dg_main_file)
    # TODO add link in all index files

    # modify docs
    # TODO: Path-Änderung
    dg_main_file_path: Path = out_path / "doc" / Path(project_name) / "index.html"
    marker_line_in_dg_file: str = f"""</div><!--header-->"""
    # TODO: Path-Änderung
    link_to_tc_main_file: str = f"""<div class="contents"><div class="textblock"><h2 class="anchor"><a href="../../testcoveragereport/index.html">Go to the code coverage report.</a></h2></div></div>\n"""
    # with open(dg_main_file_path, "r+") as dg_file:
    #     dg_lines: list[str] = dg_file.readlines()
    #     for i, line in enumerate(dg_lines):
    #         if dg_marker_line in line:
    #             dg_lines.insert(i, marker_line_in_dg_file)
    #             break
    #     dg_file.seek(0)
    #     dg_file.writelines(dg_lines)
    _insert_link(dg_main_file_path, marker_line_in_dg_file, link_to_tc_main_file, 0)

# TODO? Link subfolder index files to somewhere???

def link_all_tc_report_and_documentation_files(out_path: Path, project_name: str):
    """Find and link all test coverage class files with their respective documentation files.

    Assumptions: out_path is a relative path (like "out/" and not "/out/").
    This is so the relative links in the html insertion works (All paths of files here start with "out_path/...").
    The class files of the input project contain only [0-9, a-z, A-Z, ., - and _] as we're only escaping these characters for doxygen.
    There are no subfolders containing class files in the doxygen output (the "doc" folder).
    Contained marker lines are always present in tc and dg outputs.
    
    """
    # TODO: Path-Änderung
    tc_report_path: Path = out_path / "testcoveragereport"
    dg_path: Path = out_path / "doc" / Path(project_name)

    # Find all tc classes/files
    tc_class_files: list[Path] = _find_all_classes(tc_report_path)
    # Iterate tc classes
    for tc_class_file in tc_class_files:
        tc_class_file_trim: Path = tc_class_file
        # Remove '.gcov' and '.html'
        for _ in range(2): tc_class_file_trim = tc_class_file_trim.with_suffix("")
        tc_class_name: str = tc_class_file_trim.name
        dg_class_name: str = tc_class_name.replace("_", "__").replace(".", "_8") + ".html"

        # Find doxygen version of the class
        dg_class_file: Path = next(dg_path.glob(dg_class_name), None)

        # Link .gcov file in the doxygen
        # TODO: Path-Änderung
        marker_line_in_dg_file: str = f"""</div><!--header-->"""
        link_to_tc_class_file: str = f"""<div class="contents"><div class="textblock"><h2 class="anchor"><a href="../../../{tc_class_file}">Go to the code coverage report of this file.</a></h2></div></div>\n"""
        _insert_link(dg_class_file, marker_line_in_dg_file, link_to_tc_class_file, 0)
        
        # Link doxygen in all three tc files
        marker_line_in_tc_files: str = f"""<tr><td class="title">LCOV - code coverage report</td></tr>"""
        # TODO: Path-Änderung
        # Amount of ../ in the relative path of the link is dependant on the depth of the file. Therefore we add ../ till we're above the out folder. 
        relative_depth_correction: str = ""
        # '- 1' cuz '.' is part of the parents if its a relative path and we dont want to be above the SourceToDoc folder.
        for _ in range(len(tc_class_file.parents) - 1): relative_depth_correction += "../"
        link_to_dg_class_file: str = f"""    <tr><td class="headerItem" style="text-align: center"><a href="{relative_depth_correction}{dg_class_file}">Go to the documentation of this file.</a></td></tr>\n"""

        for tc_file in tc_report_path.glob("**/" + tc_class_name + "*"):
            _insert_link(tc_file, marker_line_in_tc_files, link_to_dg_class_file)


def _find_all_classes(search_dir: Path) -> list[Path]:
    """Find all classes in the search directory. 
    In this case classes are html-files that contain the string '.gcov.html'.
    
    Parameters
    ----------
    search_dir: Path
        The directory to search for 'classes' (files that end with '.gcov.html').

    Returns
    -------
    list[Path]
        A list of all found classes as Path objects.
    """
    found_html_classes: list[Path] = []
    for html_file in search_dir.glob("**/*.gcov.html",):
        if html_file.is_file():
            found_html_classes.append(html_file)
    return found_html_classes

def _insert_link(file_path: Path, marker: str, link: str, offset: int = 1) -> None:
    """Given a file path, open the file and insert a link string 
    after finding the marker string with the given offset.
    
    Parameters
    ----------
    file_path: Path
        Path to the file.
    marker: str
        String that's used to position the link string correctly
    link: str
        String (html code) that's linking to the doxygen/testcoverage output.
    offset: int
        0 to insert before the marker line. 1 to insert after the marker line.
        Default is to insert after.
    """
    with open(file_path, "r+") as file:
        lines: list[str] = file.readlines()
        for index, line in enumerate(lines):
            if marker in line:
                lines.insert(index + offset, link)
                break
        file.seek(0)
        file.writelines(lines)