import os
from typing import Dict, List, Literal, Union, overload

import httpx

from .base import BaseBackend, BaseFile, BaseResult

__all__ = ("GenericBackend", "GenericFile", "GenericResult")


class GenericFile(BaseFile):
    def __init__(self, content: Union[str, bytes]):
        self._content = content

    @property
    def content(self):
        return self._content

    @classmethod
    def from_file(cls, file: Union[str, os.PathLike], mode: Literal["r", "rb"] = "r") -> "GenericFile":
        with open(file, mode) as fd:
            return cls(fd.read())


GenericResult = BaseResult


class GenericBackend(BaseBackend):
    """
    A generic backend for servers running hastebin-compatible servers.
    """

    name: str
    file_class = GenericFile
    result_class = GenericResult

    def __init__(self, base_url: str = None):
        if base_url:
            self.base_url = base_url  # override class var
        self.post_url = self.base_url + "/documents"
        self.html_url = self.base_url + "/{key}"

    def get_headers(self) -> Dict[str, str]:
        return super().get_headers()

    @overload
    def create_paste(self, files: GenericFile) -> GenericResult: ...

    @overload
    def create_paste(self, *files: GenericFile) -> List[GenericResult]: ...

    def create_paste(self, *files: Union[GenericFile, str]) -> Union[GenericResult, List[GenericResult]]:
        """
        Creates a paste.

        :param files: The files to upload
        :return: The paste result. Can be multiple if multiple files were uploaded.
        """
        files = list(files)
        for n, file in enumerate(files):
            if isinstance(file, str):
                files[n] = BaseFile()
        if len(files) > 1:
            results = []
            for file in files:
                results.append(self.create_paste(file))
            return results

        file = files[0]
        with self.with_session() as session:
            response: httpx.Response = session.post(self.post_url, data=file.content)
            response.raise_for_status()
            data = response.json()
            return GenericResult(data["key"], self.html_url.format(key=data["key"]))

    def get_paste(self, key: str) -> GenericFile:
        """
        Gets a paste

        :param key: The paste's key
        :return: The file
        """
        with self.with_session() as session:
            response: httpx.Response = session.get(self.base_url + "/raw/" + key)
            response.raise_for_status()
            return GenericFile(response.text)
