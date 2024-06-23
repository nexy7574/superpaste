"""
Backend for posting pastes to http://hastebin.com
"""

# NOTE: Hastebin.com has moved to toptal.com/developers/hastebin.

from typing import List, Union

import httpx

from .base import BaseBackend, BasePasteFile, BasePasteResult

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
        h = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Content-Type": "text/plain; charset=UTF-8"
        }
        if self.token:
            h["Authorization"] = f"Bearer {self.token}"
        return h

    def create_paste(self, *files: BasePasteFile) -> Union[BasePasteResult, List[BasePasteResult]]:
        with self.with_session(self._session) as session:
            results = []
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
                results.append(
                    BasePasteResult(
                        self.base_url + "/" + key,
                        key,
                    )
                )
            return results if len(results) > 1 else results[0]

    def get_paste(self, key: str) -> BasePasteFile:
        with self.with_session(self._session) as session:
            response: httpx.Response = session.get(
                self.base_url + "/raw/" + key,
                headers={
                    self.headers()
                }
            )
            response.raise_for_status()
            return BasePasteFile(response.text)
