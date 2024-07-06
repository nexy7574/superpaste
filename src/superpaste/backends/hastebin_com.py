"""
Backend for posting pastes to http://hastebin.com
"""

# NOTE: Hastebin.com has moved to toptal.com/developers/hastebin.
# As of 2024-06-24, hastebin.com still works.

from typing import List, Union, overload

import httpx

from .base import BaseResult
from ._generic import GenericBackend, GenericFile

__author__ = "nexy7574 <https://github.com/nexy7574>"
__all__ = (
    "HastebinBackend",
    "HastebinFile",
    "HastebinResult"
)

HastebinFile = GenericFile
HastebinResult = BaseResult


class HastebinBackend(GenericBackend):
    name = "toptal"
    base_url = "https://hastebin.com"

    def __init__(self, token: str):
        """
        :param token: The API token from toptal: https://www.toptal.com/developers/hastebin/documentation
        """
        super().__init__()
        self.token = token

    def get_headers(self):
        h = {"Accept": "application/json", "Content-Type": "text/plain; charset=UTF-8"}
        h.update(super().get_headers())
        if self.token:
            h["Authorization"] = f"Bearer {self.token}"
        return h

    @overload
    def create_paste(self, files: GenericFile) -> BaseResult:
        ...

    @overload
    def create_paste(self, *files: GenericFile) -> List[BaseResult]:
        ...

    def create_paste(self, *files: GenericFile) -> Union[BaseResult, List[BaseResult]]:
        """
        Create a paste on hastebin.com

        .. warning::
            hastebin.com only supports 1 file per paste. If more than one file is provided, multiple pastes will be made.

        :param files: The files to post.
        :return: The paste, or multiple if multiple files were provided.
        """
        if len(files) > 1:
            r = []
            for file in files:
                r.append(self.create_paste(file))
            return r

        with self.with_session() as session:
            for file in files:
                if isinstance(file.content, bytes):
                    try:
                        file.content = file.content.decode("utf-8")
                    except UnicodeDecodeError:
                        raise ValueError("hastebin.com only supports text files.")

            response: httpx.Response = session.post(
                self.post_url,
                data=file.content,
            )
            response.raise_for_status()
            key = response.json()["key"]
            return BaseResult(
                key,
                self.html_url.format(key=key)
            )

    def get_paste(self, key: str) -> GenericFile:
        """
        Gets a paste from hastebin.com

        :param key: The paste key to get.
        :return: The file that was in the paste.
        """
        with self.with_session() as session:
            response: httpx.Response = session.get(self.base_url + "/raw/" + key)
            response.raise_for_status()
            return GenericFile(response.text)
