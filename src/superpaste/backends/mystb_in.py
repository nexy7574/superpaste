"""
Backend for posting pastes to http://mystb.in
"""

import datetime
import os
import pathlib
from dataclasses import dataclass
from typing import Dict, List, Optional, Union, overload, Literal

import httpx

from .base import BaseResult, BaseBackend, as_chunks
from ._generic import GenericFile

__author__ = "nexy7574 <https://github.com/nexy7574>"


class MystbinFile(GenericFile):
    def __init__(
        self,
        content: str,
        filename: str = None,
        *,
        parent_id: str = None,
        loc: int = None,
        charcount: int = None,
        annotation: str = None,
        warning_positions: list = None,
    ):
        if len(content) > 300_000:
            raise ValueError("Mystbin only supports pastes up to 300,000 characters.")
        super().__init__(content)
        self.filename = filename
        self.parent_id = parent_id
        self.loc = loc
        self.charcount = charcount
        self.annotation = annotation
        self.warning_positions = warning_positions

    def as_payload(self) -> Dict[str, str]:
        p = {"content": self.content}
        if self.filename:
            p["filename"] = self.filename
        return p

    @classmethod
    def from_file(cls, file: os.PathLike, mode: Literal["r"] = "r") -> "MystbinFile":
        if not isinstance(file, pathlib.Path):
            file = pathlib.Path(file)
            if not file.exists():
                raise FileNotFoundError(file)

        return cls(content=file.read_text(), filename=file.name)


@dataclass
class MystbinResult(BaseResult):
    created_at: datetime.datetime
    expires: Optional[datetime.datetime]
    safety: str
    views: int = 0


class MystbinBackend(BaseBackend):
    name = "mystb.in"
    base_url = "https://mystb.in/api"
    post_url = "https://mystb.in/api/paste"
    html_url = "https://mystb.in/{key}"
    result_class = MystbinResult
    file_class = MystbinFile

    @overload
    def create_paste(self, files: MystbinFile) -> MystbinResult:
        ...

    @overload
    def create_paste(self, *files: MystbinFile) -> List[MystbinResult]:
        ...

    def create_paste(
        self, *files: MystbinFile, expires: datetime.datetime = None, password: str = None
    ) -> Union[MystbinResult, List[MystbinResult]]:
        """
        Creates a paste on Mystbin

        .. warning::
            Mystbin only supports 5 files per paste. Pasting more than 5 files at once will result in multiple pastes.

        .. warning::
            Mystbin does not utilise end-to-end encryption. Passwords are only used to access the paste.

        :param files: The files to paste
        :param expires: A datetime (in the future) when the pastes should automatically be deleted. Default: never
        :param password: A password to use to protect the paste. Default: None
        :return: The paste result (a list of them if >5 files)
        """
        if expires and expires < datetime.datetime.now(datetime.timezone.utc):
            raise ValueError("expires must be in the future")
        if len(files) > 5:
            self._logger.warning(
                "Posting %d files to Mystbin; Mystbin only supports 5 files per-paste, so this will have to be split"
                " up into multiple pastes."
            )
            results = []
            for chunk in as_chunks(files, 5):
                self._logger.debug("Posting files to mystbin: %r", chunk)
                results.append(self.create_paste(*chunk))
            return results

        files = list(files)
        with self.with_session() as session:
            for file in files.copy():
                if not isinstance(file, MystbinFile):
                    if not isinstance(file, GenericFile):
                        raise TypeError("Unsupported file type %r" % file)
                    self._logger.warning("Got non-native file %r - expected MystbinFile", file)
                    files.remove(file)
                    file = MystbinFile(file.content)
                    files.append(file)

            payload = {
                "files": [f.as_payload() for f in files],
            }
            if expires:
                payload["expires"] = expires.isoformat()
            if password:
                payload["password"] = password
            response: httpx.Response = session.post(self.post_url, json=payload)
            response.raise_for_status()
            data = response.json()
            return MystbinResult(
                data["id"],
                self.html_url.format(data["id"]),
                datetime.datetime.fromisoformat(data["created_at"]),
                datetime.datetime.fromisoformat(data["expires"]) if data["expires"] else None,
                data["safety"],
                data["views"]
            )

    def get_paste(self, key: str, password: Optional[str] = None) -> List[MystbinFile]:
        """
        Fetches a paste from Mystbin

        :param key: The key of the paste to fetch
        :param password: The password to use to access the paste
        :return: A list of files in the paste
        """
        with self.with_session() as session:
            response: httpx.Response = session.get(self.post_url + "/" + key)
            response.raise_for_status()

            data = response.json()
            files = []
            for file in data["files"]:
                files.append(MystbinFile(**file))
            return files
