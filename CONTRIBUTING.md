# Contributing

Contributions are welcome! Please do the following to implementing your changes:

1. Fork this repository to your account
2. Clone your repository locally
3. Create a new branch, named after the feature you're implementing,
for example, `feature/backends/pastebin`, or `fix/backends/pastebin`.
4. Implement your changes
5. Make sure you've run linting (`ruff format` & `ruff check --fix`) before committing (you can amend if you forgot)
6. Push your changes to your fork
7. Open a pull request to this repository, with a detailed description of your changes

If you're unsure about anything, feel free to open an issue, or ask in the pull request.

## Package format

You should add new backends as `superpaste/backends/{domain}.py`. `{domain}` should be the domain that will be contacted
but with periods (`.`) separated by underscores (`_`). For example, `mystb.in` would be `mystb_in.py`.

You should then utilise this template:

```python

"""
Backend for posting pastes to <target site>
"""

from typing import List, Union

import httpx

from .base import BaseBackend, BasePasteFile, BasePasteResult

__author__ = "your_username <https://github.com/your_username>"


class MyBackend(BaseBackend):
    name = "mybackend"  # this is recommended to just be the domain, but can be anything.
    base_url = "https://<domain_base>"  # e.g.: "https://paste.example"
    post_url = "https://<domain_base>/<api_endpoint>"  # e.g.: "https://paste.example/api/paste"
    html_url = "https://<domain_base>/<view_endpoint>"  
    # `view_endpoint` must consume the formatting `{key}`. e.g: "https://paste.example/view/{key}"
    file_class = BasePasteFile  # can be omitted if your backend supports the base file class
    result_class = BasePasteResult  # can be omitted if your backend supports the base result class

    def __init__(self, session: httpx.Client = None):
        self._session = session

    def create_paste(self, *files: BasePasteFile) -> Union[BasePasteResult, List[BasePasteResult]]:
        with self.with_session(self._session) as session:
            results = []
            for file in files:
                if isinstance(file.content, bytes):
                    try:
                        file.content = file.content.decode("utf-8")
                    except UnicodeDecodeError:
                        raise ValueError(f"{self.name} only supports text files.")
                
                # Replace as appropriate vv
                response: httpx.Response = session.post(
                    self.post_url,
                    data=file.content,
                    headers={
                        "Accept": "application/json, text/javascript, */*; q=0.01",
                        "Content-Type": "text/plain; charset=UTF-8",
                    },
                )
                if response.status_code != 301:  # replace as appropriate. If the status code is meant to be 2XX omit if
                    response.raise_for_status()

                data = response.json()
                results.append(
                    BasePasteResult.from_response(data)
                )
            if len(files) == 1:
                if len(results) != len(files):
                    raise ValueError("Only one file was posted, but multiple results were returned.")
                # Only return multiple results if multiple files were posted
                return results[0]
            return results
    
    # If you need to change the async post function, or want to make a more efficient one than just wrapping the sync
    # one in a thread, you can override this function:
    # async def async_create_paste(self, *files: BasePasteFile) -> Union[BasePasteResult, List[BasePasteResult]]:
    #     """
    #     Creates a paste asynchronously.
    # 
    #     internally, this function just calls `create_paste` in a thread, to make it non-blocking.
    # 
    #     :param files: The files to upload
    #     :return: The paste result. Can be multiple if multiple files were uploaded.
    #     """
    #     import asyncio
    #     return await asyncio.to_thread(self.create_paste, *files)

    def get_paste(self, key: str) -> BasePasteFile:
        # If you change this function's signature (i.e. add more parameters), they MUST be optional.
        # You can, however, raise errors in the even they're required and can't have a default.
        with self.with_session(self._session) as session:
            response: httpx.Response = session.get(self.base_url + "/" + key)
            response.raise_for_status()
            return BasePasteFile(response.text)
```

Then, replace everything that needs replacing.

Note that you are allowed to implement more methods, however you MUST implement at least what the ABC specifies.
If your service provides more data, you should subclass the dataclass `BasePasteResult` and add additional fields.
Keep in mind that `BasePasteFile` is actually an instance of `BasePasteFileProtocol`, which is a `Protocol` - you
do not directly subclass it, but must implement its methods and variables.

**Make sure you add your new classes to `superpaste/backends/__init__.py`! Otherwise, the CLI cannot use it.**

## Testing

You should also test your changes before pushing.
Right now, there are no ci tests, however after adding your backend, you should try and test it with the CLI.
For example:

```bash
$ superpaste --backend mybackend path/to/file.txt  # test that pasting one file works
$ superpaste --backend mybackend path/to/file1.txt path/to/another/file1.txt  # test that pasting multiple files works
$ echo "content here" | superpaste --backend mybackend -  # test that pasting from stdin works
```

After testing, you can push your changes and open a pull request.
