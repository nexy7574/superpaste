import argparse
import pathlib
import sys
from typing import Dict, Type


def main():
    from . import backends

    backend_list: Dict[str, Type[backends.BaseBackend]] = {
        x.name: x
        for x in backends.__dict__.values()
        if isinstance(x, type) and issubclass(x, backends.BaseBackend) and x != backends.BaseBackend
    }
    # This is so ugly. I love it.

    parser = argparse.ArgumentParser(description="SuperPaste - paste anywhere")
    parser.add_argument("--backend", "-b", type=str, choices=list(backend_list.keys()), help="Backend to use")
    parser.add_argument(
        "files",
        metavar="FILE",
        type=str,
        nargs="+",
        help="Files to paste. `-` reads from stdin, everything else resolves to file paths.",
    )
    args = parser.parse_args()
    if not args.files:
        parser.error("No files specified")

    backend = backend_list[args.backend]()
    parsed_files = []
    for file in args.files:
        if file == "-":
            content = sys.stdin.buffer.read().decode("utf-8")
            parsed_files.append(backend.file_class(content=content))
        else:
            pf = pathlib.Path(file)
            if not pf.exists():
                parser.error(f"File {file} does not exist")
            parsed_files.append(backend.file_class.from_file(pf))

    print("Posting %d file(s)..." % len(parsed_files), end="\r")
    result = backend.create_paste(*parsed_files)
    if isinstance(result, list):
        for i, x in enumerate(result):
            print(f"File {args.files[i]}: {x.url}")
    else:
        print(result.url)


if __name__ == "__main__":
    main()
