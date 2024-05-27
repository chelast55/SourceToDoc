from argparse import ArgumentParser
from pathlib import Path

from openai import OpenAI

from sourcetodoc.docstring import Replace, get_print_converters, LLM

# Configuration
base_url="http://localhost:11434/v1"
api_key="ollama"
model="phi3"

llm = LLM(OpenAI(base_url=base_url, api_key=api_key), model)

def main():
    parser = ArgumentParser()
    subparsers = parser.add_subparsers(dest="subparser")

    comment_subparser = subparsers.add_parser("comment")

    comment_subparser.add_argument("path")

    converters = get_print_converters(llm)
    comment_subparser.add_argument("--converter", choices=converters.keys())
    comment_subparser.add_argument("--replace", action="store_true", default=False, help="If set, the comments will be replaced")
    comment_subparser.add_argument("--filter", help="Overrides the default filter of the converter (Only matters if the path is a directory) (Python RegEx)")

    args = parser.parse_args()

    if args.subparser == "comment":
        converter = converters[args.converter]

        replace = Replace.REPLACE_OLD_COMMENTS if args.replace else Replace.APPEND_TO_OLD_COMMENTS

        path: Path = Path(args.path)
        if path.is_file():
            converter.convert_file(path, replace)
        elif path.is_dir():
            converter.convert_files(path, replace, args.filter)


main()
