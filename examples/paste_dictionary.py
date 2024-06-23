"""
This example will post the file /usr/share/dict/words to a paste service
"""

from superpaste.backends import HstSHBackend


def main():
    backend = HstSHBackend()
    with open("/usr/share/dict/words") as file:
        sb_file = backend.file_class.from_file(file)

    result = backend.create_paste(sb_file)
    print(result.url)


if __name__ == "__main__":
    main()
