from pathlib import Path

def link_report_and_docs_main(out_path: Path, project_name):
    # Link coverage and documentation.
    # modify tcreport
    tc_report_path: Path = out_path / "testcoveragereport"
    tc_report_main_file_path: Path = tc_report_path / "index.html"
    tc_marker_line: str = f"""<tr><td class="title">LCOV - code coverage report</td></tr>"""
    link_to_dg_main_file: str = f"""    <tr><td class="headerItem" style="text-align: center"><a href="../doc/{project_name}/index.html">Go to the documentation.</a></td></tr>\n"""
    with open(tc_report_main_file_path, "r+") as tc_report_file:
        tc_lines: list = tc_report_file.readlines()
        for i, line in enumerate(tc_lines):
            if tc_marker_line in line:
                tc_lines.insert(i + 1, link_to_dg_main_file)
                break
        tc_report_file.seek(0)
        tc_report_file.writelines(tc_lines)

    # modify docs
    dg_path: Path = out_path / "doc" / Path(project_name)
    dg_main_file_path: Path = dg_path / "index.html"
    dg_marker_line: str = f"""</div><!--header-->"""
    link_to_tc_main_file: str = f"""<div class="contents"><div class="textblock"><h2 class="anchor"><a href="../../testcoveragereport/index.html">Go to the code coverage report.</a></h2></div></div>\n"""
    with open(dg_main_file_path, "r+") as dg_file:
        dg_lines: list = dg_file.readlines()
        for i, line in enumerate(dg_lines):
            if dg_marker_line in line:
                dg_lines.insert(i, link_to_tc_main_file)
                break
        dg_file.seek(0)
        dg_file.writelines(dg_lines)