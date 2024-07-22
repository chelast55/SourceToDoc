import re
from pathlib import Path
from typing import Iterator


def get_files(dir: Path, regex: str) -> Iterator[Path]:
    matcher = re.compile(regex)
    for (dirpath, _, filenames) in dir.walk():
        for filename in filenames:
            if matcher.fullmatch(filename) is not None:
                file = (dirpath / filename)
                yield file
