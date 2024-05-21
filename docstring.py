from argparse import ArgumentParser
from pathlib import Path

from openai import OpenAI

from sourcetodoc.docstring import Converter, Replace, get_print_converters

# Configuration
client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")


def convert_file(file: Path, parser: Converter, replace: Replace) -> None:
    code = file.read_text()
    result = parser.convert_string(code, replace)
    file.write_text(result)


def main():
    parser = ArgumentParser()
    subparsers = parser.add_subparsers(dest="subparser")

    docstring_parser = subparsers.add_parser("docstring")

    docstring_subparsers = docstring_parser.add_subparsers(dest="docstring_subparser")

    docstring_convert_subparser = docstring_subparsers.add_parser("convert")
    docstring_convert_subparser.add_argument("path")
    docstring_convert_subparser.add_argument("--converter")

    args = parser.parse_args()

    if args.subparser == "docstring":
        if args.docstring_subparser == "convert":
            converters = get_print_converters(client)
            if args.converter in converters:
                converter = converters[args.converter]
                convert_file(Path(args.path), converter, Replace.APPEND_TO_OLD_COMMENTS)
            else:
                print(f"{args.converter} specified by --converter was not found")

main()
