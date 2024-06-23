"""
Backend for posting pastes to http://hst.sh.
"""

from typing import List, Union, overload

import httpx

from .base import BaseBackend, BasePasteFile, BasePasteResult, BasePasteFileProtocol

__author__ = "nexy7574 <https://github.com/nexy7574>"


class HstSHBackend(BaseBackend):
    name = "hst.sh"
    base_url = "https://hst.sh"
    post_url = "https://hst.sh/documents"
    html_url = "https://hst.sh/{key}"

    def __init__(self, session: httpx.Client = None):
        self._session = session

    @overload
    def create_paste(self, files: BasePasteFileProtocol) -> BasePasteResult:
        ...

    @overload
    def create_paste(self, *files: BasePasteFileProtocol) -> List[BasePasteResult]:
        ...

    def create_paste(self, *files: BasePasteFileProtocol) -> Union[BasePasteResult, List[BasePasteResult]]:
        """
        Create a paste on hst.sh

        .. warning::
            hst.sh only supports 1 file per paste. If more than one file is provided, multiple pastes will be made.

        :param files: The files to post
        :return: The paste, or multiple if multiple files were provided.
        """
        if len(files) > 1:
            self._logger.warning(
                "Posting %d files to hst.sh; hst.sh only supports 1 file per paste, "
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
                        raise ValueError("hst.sh only supports text files.")
            response: httpx.Response = session.post(
                self.post_url,
                data=file.content,
                headers={
                    "Accept": "application/json, text/javascript, */*; q=0.01",
                    "Content-Type": "text/plain; charset=UTF-8",
                },
            )
            response.raise_for_status()
            key = response.json()["key"]
            return BasePasteResult(
                self.html_url.format(key=key),
                key,
            )

    def get_paste(self, key: str) -> BasePasteFile:
        with self.with_session(self._session) as session:
            response: httpx.Response = session.get(self.base_url + "/raw/" + key)
            response.raise_for_status()
            return BasePasteFile(response.text)
