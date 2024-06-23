"""
Backend for posting pastes to http://hst.sh.
"""

from typing import List, Union

import httpx

from .base import BaseBackend, BasePasteFile, BasePasteResult

__author__ = "nexy7574 <https://github.com/nexy7574>"


class HstSHBackend(BaseBackend):
    name = "hst.sh"
    base_url = "https://hst.sh"
    post_url = "https://hst.sh/documents"
    html_url = "https://hst.sh/{key}"

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
                        raise ValueError("hst.sh only supports text files.")
                response: httpx.Response = session.post(
                    self.post_url,
                    data=file.content,
                    headers={
                        "Accept": "application/json, text/javascript, */*; q=0.01",
                        "Content-Type": "text/plain; charset=UTF-8",
                    },
                )
                if response.status_code != 301:
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
            response: httpx.Response = session.get(self.base_url + "/raw/" + key)
            response.raise_for_status()
            return BasePasteFile(response.text)
