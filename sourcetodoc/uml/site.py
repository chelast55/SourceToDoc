from dataclasses import dataclass
from io import TextIOWrapper
import os
from pathlib import Path
from typing import Iterable


_CSS: str = """\
.links {
    display: flex;
    flex-direction: column;
}"""


_INDEX_START: str = """\
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Index</title>
    <link rel="stylesheet" href="./style.css">
</head>

<body>
    <main class="links">
        <h2>Class, Package and Include Diagrams</h2>
"""


_INDEX_LINK_TO_DIAGRAM_SITE: str = """\
        <a href=\"{link}\">{name}</a>
"""


_INDEX_SEQUENCE_DIAGRAM_LINKS_HEADER: str = """\
        <h2>Sequence Diagrams</h2>
"""


_INDEX_END: str = """\
    </main>
</body>"""


_DIAGRAM_SITE: str = """\
<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{diagram_title}</title>
</head>

<body>
    <nav>
        <a href="{index_link}">Index</a>
    </nav>
    <main>
        <h1>{diagram_title}</h1>
        <img src="{image_link}"" />
    </main>
</body>

</html>"""

_HTML_EXT = ".html"
_SVG_EXT = ".svg"


@dataclass(frozen=True)
class DiagramsInfo:
    diagrams_dir: Path
    diagram_name_diagram_title_pairs: Iterable[tuple[str,str]]


def create_diagrams_site(
        dst_dir: Path,
        default_diagrams_info: DiagramsInfo,
        sequence_diagrams_info: DiagramsInfo | None,
    ) -> None:
    # Create destination dir if it does not exist
    dst_dir.mkdir(parents=True, exist_ok=True)

    # Create CSS file
    css_file = dst_dir / "style.css"
    css_file.write_text(_CSS)

    # Create index.html with links to diagrams
    index_site_filename = "index.html"
    index_site_file = dst_dir / index_site_filename
    with open(index_site_file, "w") as f:
        f.write(_INDEX_START)

        # Create sites and add links to class, package and include diagrams
        _add_diagram_sites(f, dst_dir, default_diagrams_info, index_site_filename)

        if sequence_diagrams_info is not None:
            # Create sites and add links to sequence diagrams
            f.write(_INDEX_SEQUENCE_DIAGRAM_LINKS_HEADER)
            _add_diagram_sites(f, dst_dir, sequence_diagrams_info, index_site_filename)

        f.write(_INDEX_END)


def _add_diagram_sites(
        f_index: TextIOWrapper,
        dst_dir: Path,
        diagrams_info: DiagramsInfo,
        index_site_filename: str
    ) -> None:
    for diagram_name, function_identifier in diagrams_info.diagram_name_diagram_title_pairs:
        # Check if the corresponding .svg file exists
        svg_filename = diagram_name + _SVG_EXT
        svg_file = diagrams_info.diagrams_dir / svg_filename
        if not svg_file.is_file():
            continue

        # Add diagram site link to index site
        seq_diagram_site_filename = diagram_name + _HTML_EXT
        part = _INDEX_LINK_TO_DIAGRAM_SITE.format(link = seq_diagram_site_filename, name = function_identifier)
        f_index.write(part)

        # Create diagram site with link to index site and .svg file
        link_from_dst_dir_to_sequence_diagrams_dir: Path = Path(os.path.relpath(diagrams_info.diagrams_dir, dst_dir))
        link_from_dst_dir_to_svg_file: Path = link_from_dst_dir_to_sequence_diagrams_dir / svg_filename
        diagram_site: str = _DIAGRAM_SITE.format(
                index_link = index_site_filename,
                diagram_title = function_identifier,
                image_link = link_from_dst_dir_to_svg_file)
        diagram_site_file: Path = dst_dir / seq_diagram_site_filename
        diagram_site_file.write_text(diagram_site)
