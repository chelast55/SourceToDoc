from pathlib import Path

# Link coverage and documentation.
# modify tcreport
tc_report_path: Path = out_path / "testcoveragereport"
tc_report_main_file_path: Path = tc_report_path / "index.html"
tc_marker_line: str = f"""<tr><td class="title">LCOV - code coverage report</td></tr>"""
# TODO: put variable in f-string for file path (relative)
link_to_dg_main_file: str = f"""    <tr><td class="headerItem" style="text-align: center"><a href="../doc/{args.project_name}/index.html">Go to the documentation.</a></td></tr>\n"""
with open(tc_report_main_file_path, "r+") as tc_report_file:
    tc_lines: list = tc_report_file.readlines()
    for i, line in enumerate(tc_lines):
        if tc_marker_line in line:
            tc_lines.insert(i + 1, link_to_dg_main_file)
            break
    tc_report_file.seek(0)
    tc_report_file.writelines(tc_lines)

# modify docs
dg_path: Path = out_path / "doc" / Path(args.project_name)
dg_main_file_path: Path = dg_path / "index.html"
dg_marker_line: str = f"""</div><!--header-->"""
# TODO: put variable in f-string for file path (relative)
link_to_tc_main_file: str = f"""<div class="contents"><div class="textblock"><h2 class="anchor"><a href="../../testcoveragereport/index.html">Go to the code coverage report.</a></h2></div></div>\n"""
with open(dg_main_file_path, "r+") as dg_file:
    dg_lines: list = dg_file.readlines()
    for i, line in enumerate(dg_lines):
        if dg_marker_line in line:
            dg_lines.insert(i, link_to_tc_main_file)
            break
    dg_file.seek(0)
    dg_file.writelines(dg_lines)