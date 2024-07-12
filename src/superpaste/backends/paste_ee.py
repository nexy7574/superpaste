"""
Backend for posting pastes to http://paste.ee
"""

from typing import List, Union

import httpx

from .base import BaseBackend, BaseResult, as_chunks
from .mystb_in import MystbinFile

__author__ = "nexy7574 <https://github.com/nexy7574>"

__all__ = ["PasteEEFile", "PasteEEBackend", "PasteEEResult"]
PasteEEResult = BaseResult


class PasteEEFile(MystbinFile):
    # noinspection PyShadowingBuiltins
    def __init__(self, content: str, filename: str = None, syntax: str = "autodetect", *, id: int = None):
        super().__init__(content)
        self.filename = filename
        self.syntax = syntax
        self.id = id

    def __hash__(self):
        return hash((self.content, self.filename))

    def as_payload(self):
        x = super().as_payload()
        if self.syntax:
            x["syntax"] = self.syntax
        return x


class PasteEEBackend(BaseBackend):
    name = "paste.ee"
    base_url = post_url = "https://api.paste.ee/v1/pastes"
    html_url = "https://hst.sh/{key}"

    def __init__(self, token: str):
        """
        :param token: The API token to use for authentication
        """
        self.token = token

    def create_paste(
        self, *files: Union[PasteEEFile, MystbinFile], paste_description: str = None, encrypted: bool = False
    ) -> Union[BaseResult, List[BaseResult]]:
        """
        Creates a paste on paste.ee

        .. warning::
            Paste.ee only supports 5 files per paste, and up to 6MB
            See [their wiki/acceptable use policy](https://paste.ee/wiki/AUP) for more information.

        :param files: A list of files to post
        :param paste_description: A description of the overall paste. Can be omitted.
        :param encrypted: Whether this paste is already encrypted. Defaults to False.
        :return: A single `BasePasteResult` if less than 5 files were posted, or a list of `BasePasteResult`s if more.
        :raises ValueError: If any of the files are not text files.
        """
        if len(files) > 5:
            results = []
            for chunk in as_chunks(files, 5):
                self._logger.debug("Posting files to paste.ee: %r", chunk)
                results.append(self.create_paste(*chunk))
            return results

        with self.with_session() as session:
            for file in files:
                if isinstance(file.content, bytes):
                    try:
                        file.content = file.content.decode("utf-8")
                    except UnicodeDecodeError:
                        raise ValueError("paste.ee only supports text files.")

            payload = {"sections": [x.as_payload() for x in files]}
            if paste_description:
                payload["description"] = paste_description
            if encrypted:
                payload["encrypted"] = True
            response: httpx.Response = session.post(
                self.post_url,
                json={
                    "encrypted": False,
                    "description": "SuperPaste",
                },
                auth=(self.token, ""),
            )
            response.raise_for_status()

            data = response.json()
            return BaseResult(data["id"], data["link"])

    def get_paste(self, key: str) -> List[PasteEEFile]:
        """
        Gets a paste from paste.ee

        :param key: The key of the paste to get
        :return: A list of files that were in the paste
        """
        r = []
        with self.with_session() as session:
            response: httpx.Response = session.get(self.post_url + "/" + key)
            response.raise_for_status()
            data = response.json()
            for section in data["paste"]["sections"]:
                r.append(PasteEEFile(section["content"], section["name"], section["syntax"], id=section["id"]))
        return r
