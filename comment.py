from argparse import ArgumentParser
from pathlib import Path
from typing import Any, Optional

from openai import OpenAI

from sourcetodoc.docstring.cli import get_converter_by_args
from sourcetodoc.docstring.conversions.llm import LLM
from sourcetodoc.docstring.converter import Converter
from sourcetodoc.docstring.replace import Replace

# Configuration
base_url="http://localhost:11434/v1"
api_key="ollama"
model="phi3"

client = OpenAI(base_url=base_url, api_key=api_key)
llm = LLM(client, model)

def main():
    parser = ArgumentParser()
    subparsers = parser.add_subparsers(dest="subparser")

    comment_subparser = subparsers.add_parser("comment")

    comment_subparser.add_argument("path")

    comment_subparser.add_argument("--converter", required=True)
    comment_subparser.add_argument("--replace", action="store_true", default=False, help="If set, the comments will be replaced")
    comment_subparser.add_argument("--inline", action="store_true", default=False)
    comment_subparser.add_argument("--filter", help="Overrides the default filter of the converter (Only matters if the path is a directory) (Python RegEx)")
    comment_subparser.add_argument("--style")
    comment_subparser.add_argument("--openai_base_url")
    comment_subparser.add_argument("--openai_api_key")
    comment_subparser.add_argument("--llm_model")

    args = parser.parse_args()

    if args.subparser == "comment":

        replace = Replace.REPLACE_OLD_COMMENTS if args.replace else Replace.APPEND_TO_OLD_COMMENTS

        if replace is Replace.APPEND_TO_OLD_COMMENTS and args.inline:
            replace = Replace.APPEND_TO_OLD_COMMENTS_INLINE

        converter: Optional[Converter[Any]] = get_converter_by_args(**vars(args))

        if converter is not None:
            path: Path = Path(args.path)
            if path.is_file():
                converter.convert_file(path, replace)
            elif path.is_dir():
                converter.convert_files(path, replace, args.filter)
            else:
                print(f"{args.path} is not a file or a directory")

if __name__ == "__main__":
    main()
