"""
Backend for posting pastes to http://mystb.in
"""

import datetime
import os
import pathlib
from dataclasses import dataclass
from typing import Dict, List, Optional, Union, overload

import httpx

from .base import BaseBackend, BasePasteResult, as_chunks, BasePasteFileProtocol

__author__ = "nexy7574 <https://github.com/nexy7574>"


class MystbinFile:
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
        self.content = content
        self.filename = filename
        self.parent_id = parent_id
        self.loc = loc
        self.charcount = charcount
        self.annotation = annotation
        self.warning_positions = warning_positions

    @classmethod
    def from_file(cls, file: os.PathLike) -> "MystbinFile":
        if not isinstance(file, pathlib.Path):
            file = pathlib.Path(file)
        return cls(content=file.read_text(), filename=file.name)

    def as_payload(self: "MystbinFile") -> Dict[str, str]:
        """
        Returns the file as a JSON-serializable dictionary.
        :return: the payload
        """
        x = {"filename": self.filename, "content": self.content}
        if not self.filename:
            del x["filename"]
        return x


@dataclass
class MystbinResult(BasePasteResult):
    created_at: datetime.datetime
    expires: Optional[datetime.datetime]
    safety: str
    views: int = 0

    @classmethod
    def from_response(cls, backend: "MystbinBackend", data: dict) -> "MystbinResult":
        return cls(url=backend.html_url.format(key=data["id"]), key=data.pop("id"), **data)


class MystbinBackend(BaseBackend):
    name = "mystb.in"
    base_url = "https://mystb.in/api/paste"
    post_url = "https://mystb.in/api/paste"
    html_url = "https://mystb.in/{key}"
    result_class = MystbinResult
    file_class = MystbinFile

    def __init__(self, session: httpx.Client = None):
        self._session = session

    @overload
    def create_paste(self, files: MystbinFile) -> MystbinResult:
        ...

    @overload
    def create_paste(self, *files: MystbinFile) -> List[MystbinResult]:
        ...

    def create_paste(
        self, *files: MystbinFile, expires: datetime.datetime = None, password: str = None
    ) -> Union[MystbinResult, List[MystbinResult]]:
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

        with self.with_session(self._session) as session:
            payload = {
                "files": [file.as_payload() for file in files],
            }
            if expires:
                payload["expires"] = expires.isoformat()
            if password:
                payload["password"] = password
            response: httpx.Response = session.post(self.post_url, json=payload)
            response.raise_for_status()
            data = response.json()
            return MystbinResult.from_response(self, data)

    def get_paste(self, key: str, password: Optional[str] = None) -> List[MystbinFile]:
        with self.with_session(self._session) as session:
            response: httpx.Response = session.get(self.base_url + "/" + key)
            response.raise_for_status()

            data = response.json()
            files = []
            for file in data["files"]:
                files.append(MystbinFile(**file))
            return files
