# SuperPaste

Have you ever found yourself in code, needing to send a large chunk of text, such as a log file, but didn't want to
clog up the chat with a wall of text? SuperPaste is here to help! SuperPaste is a simple, easy-to-use tool that allows
you to paste large chunks of text into a file, and then send a link to that file to your friends or coworkers. They can
then view the file in their browser, without having to download it.

This works by taking your desired files, such as a log string, and posting them to a chosen server, such as hst.sh
and mystb.in. The server will then return a link to the file, which you can then send to your friends.

---

This is a continuation of the [PostBin](https://github.com/dragdev-studios/PostBin) project, which was discontinued as
it fell into disrepair, and had an ugly API.

## Installing:

You can install from git:

```bash
pip install git+https://github.com/nexy7574/superpaste.git
```

## Usage:

you can use it in your code like so:

```pycon
>>> from superpaste.backends import HstSHBackend, BasePasteResult
# See: /src/superpaste/backends/__init__.py for more backends


# Create a backend
>>> backend = HstSHBackend()

# Post a file
>>> result = backend.create_paste(backend.file_class.from_file("path/to/file.txt"))
>>> print(result.url)
BasePasteResult(url='https://hst.sh/2', key="2")

# Post a string
>>> result = backend.create_paste(backend.file_class("content here"))
>>> print(result.url)
BasePasteResult(url='https://hst.sh/2', key="2")

# You can also post bytes, assuming they're actually just UTF-8 text.
r>>> esult = backend.create_paste(backend.file_class(b"bytes here"))
>>> print(result.url)
BasePasteResult(url='https://hst.sh/3', key="3")

# You can post multiple files, too
>>> results = backend.create_paste(
    backend.file_class("content here"),
    backend.file_class.from_file("path/to/file.txt"),
)
[
    BasePasteResult(url='https://hst.sh/4', key="4"),
    BasePasteResult(url='https://hst.sh/5', key="5"),
]

# There is also an async API, which just wraps the sync API in an async function, pushing it to a thread:
# To use this part of the example, you either need to be in an async function, or use iPython.
>>> await backend..async_create_paste(backend.file_class("content here"))
BasePasteResult(url='https://hst.sh/6', key="6")
```

or use it in your console:

```bash
$ superpaste --backend mystb.in path/to/file.txt
...
$ echo "content here" | superpaste --backend hst.sh -
...
$ superpaste --backend hst.sh path/to/file1.txt path/to/another/file1.txt
file file1.txt: https://hst.sh/2
file file2.txt: https://hst.sh/3
```
