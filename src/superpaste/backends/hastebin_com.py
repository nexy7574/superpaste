"""
Backend for posting pastes to http://hastebin.com
"""

# NOTE: Hastebin.com has moved to toptal.com/developers/hastebin.

from typing import List, Union

import httpx

from .base import BaseBackend, BasePasteFile, BasePasteResult, overload, BasePasteFileProtocol

__author__ = "nexy7574 <https://github.com/nexy7574>"


class HastebinBackend(BaseBackend):
    name = "toptal-hastebin"
    base_url = "https://hastebin.com"
    post_url = "https://hastebin.com/documents"
    html_url = "https://hastebin.com/{key}"

    def __init__(self, session: httpx.Client = None, *, token: str):
        """
        :param session: An optional pre-existing session to use. Will be auto-generated if not provided.
        :param token: The API token from toptal: https://www.toptal.com/developers/hastebin/documentation
        """
        self.token = token
        self._session = session

    def headers(self):
        h = {"Accept": "application/json, text/javascript, */*; q=0.01", "Content-Type": "text/plain; charset=UTF-8"}
        if self.token:
            h["Authorization"] = f"Bearer {self.token}"
        return h

    @overload
    def create_paste(self, files: BasePasteFileProtocol) -> BasePasteResult:
        ...

    @overload
    def create_paste(self, *files: BasePasteFileProtocol) -> List[BasePasteResult]:
        ...

    def create_paste(self, *files: BasePasteFileProtocol) -> Union[BasePasteResult, List[BasePasteResult]]:
        if len(files) > 1:
            self._logger.warning(
                "Posting %d files to hastebin.com; hastebin.com only supports 1 file per paste, "
                "so multiple pastes will be made.",
                len(files),
            )
            r = []
            for file in files:
                r.append(self.create_paste(file))
            return r

        with self.with_session(self._session) as session:
            for file in files:
                if isinstance(file.content, bytes):
                    try:
                        file.content = file.content.decode("utf-8")
                    except UnicodeDecodeError:
                        raise ValueError("hastebin.com only supports text files.")

            response: httpx.Response = session.post(
                self.post_url,
                data=file.content,
                headers=self.headers(),
            )
            response.raise_for_status()
            key = response.json()["key"]
            return BasePasteResult(
                self.html_url.format(key=key),
                key,
            )

    def get_paste(self, key: str) -> BasePasteFile:
        with self.with_session(self._session) as session:
            response: httpx.Response = session.get(self.base_url + "/raw/" + key, headers={self.headers()})
            response.raise_for_status()
            return BasePasteFile(response.text)
