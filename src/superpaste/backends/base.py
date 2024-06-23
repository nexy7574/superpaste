import abc
import asyncio
import logging
import os
import pathlib
from contextlib import contextmanager
from dataclasses import dataclass
from importlib.metadata import version
from typing import Generator, Iterable, List, Optional, Protocol, TypeVar, Union

import httpx

__all__ = (
    "BasePasteFileProtocol",
    "BasePasteFile",
    "BasePasteResult",
    "BaseBackend",
    "__author__",
    "__user_agent__",
    "as_chunks",
)

T = TypeVar("T")

__user_agent__ = "SuperPaste/%s (+https://github.com/nexy7574/superpaste)" % version("superpaste")
__author__ = "nexy7574 <https://github.com/nexy7574>"


def as_chunks(iterable: Iterable[T], size: int) -> Generator[List[T], None, None]:
    """
    Splits the given iterable into chunks of N size.

    Example:
    >>> list(as_chunks(range(10), 3))
    [[0, 1, 2], [3, 4, 5], [6, 7, 8], [9]]

    :param iterable: The iterable to chunk
    :param size: The size of each chunk
    :return: The new chunks
    """
    if size <= 0:
        raise ValueError("size must be greater than 0")

    ret_chunk = []
    for item in iterable:
        ret_chunk.append(item)
        if len(ret_chunk) == size:
            yield ret_chunk
            ret_chunk = []
    if ret_chunk:
        yield ret_chunk


class BasePasteFileProtocol(Protocol):
    content: Union[str, bytes]

    def __hash__(self) -> int: ...

    @classmethod
    def from_file(cls: T, file: pathlib.Path) -> T: ...


class BasePasteFile:
    def __init__(self, content: Union[str, bytes]):
        self.content = content

    def __repr__(self):
        return f"BasePasteFile(content={self.content!r})"

    def __hash__(self):
        return hash((self.content,))

    @classmethod
    def from_file(cls, file: os.PathLike) -> "BasePasteFile":
        if not isinstance(file, pathlib.Path):
            file = pathlib.Path(file)
        try:
            return cls(file.read_text())
        except UnicodeDecodeError:
            return cls(file.read_bytes())


@dataclass
class BasePasteResult:
    """The result of creating a paste"""

    url: str
    key: str

    def __repr__(self):
        return f"BasePasteResult(url={self.url!r}, key={self.key!r})"

    @classmethod
    def from_response(cls, backend: "BaseBackend", data: dict) -> "BasePasteResult":
        return cls(url=backend.html_url.format(key=data["key"]), key=data.pop("key"))


class BaseBackend(abc.ABC):
    name = "base"
    base_url = "http://base.invalid"
    post_url = "http://post.invalid"
    html_url = "http://base.invalid/{key}"
    result_class = BasePasteResult
    file_class = BasePasteFile

    @property
    def _logger(self) -> logging.Logger:
        """Gets the logger for this backend"""
        return logging.getLogger(f"superpaste.backends.{self.name.lower()}")

    @contextmanager
    def with_session(self, session: Optional[httpx.Client]) -> "httpx.Client":
        """
        Return a client session, closing it properly if it was created by this method.
        """
        if not session:
            with httpx.Client(headers={"User-Agent": __user_agent__}) as session:
                yield session
        else:
            yield session

    @abc.abstractmethod
    def create_paste(self, *files: BasePasteFile) -> Union[BasePasteResult, List[BasePasteResult]]:
        """
        Creates a paste.

        :param files: The files to upload
        :return: The paste result. Can be multiple if multiple files were uploaded.
        """
        raise NotImplementedError

    async def async_create_paste(self, *files: BasePasteFile) -> Union[BasePasteResult, List[BasePasteResult]]:
        """
        Creates a paste asynchronously.

        internally, this function just calls `create_paste` in a thread, to make it non-blocking.

        :param files: The files to upload
        :return: The paste result. Can be multiple if multiple files were uploaded.
        """
        return await asyncio.to_thread(self.create_paste, *files)

    @abc.abstractmethod
    def get_paste(self, key: str) -> BasePasteFile:
        """
        Gets a paste.

        :param key: The paste key
        :return: The paste file
        """
        raise NotImplementedError
