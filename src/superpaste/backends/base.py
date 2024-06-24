import abc
import asyncio
import logging
import os
from contextlib import contextmanager
from dataclasses import dataclass
from importlib.metadata import version
from typing import Generator, Iterable, List, Optional, TypeVar, Union, overload, Literal, Dict

import httpx

__all__ = (
    "BaseFile",
    "BaseResult",
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


class BaseFile(abc.ABC, metaclass=abc.ABCMeta):
    @property
    @abc.abstractmethod
    def content(self) -> Union[str, bytes]:
        ...

    @classmethod
    @abc.abstractmethod
    def from_file(cls: T, file: Union[str, os.PathLike], mode: Literal["r", "rb"] = "r") -> T:
        """
        Loads a disk file, converting it into a file ready for pasting
        """
        raise NotImplementedError

    def __hash__(self):
        return hash(self.content)


@dataclass
class BaseResult(abc.ABC):
    key: str
    url: str


class BaseBackend(abc.ABC):
    name: str = "base"
    base_url = "http://base.invalid"
    result_class = BaseResult
    file_class = BaseFile

    @property
    def _logger(self) -> logging.Logger:
        """Gets the logger for this backend"""
        return logging.getLogger(f"superpaste.backends.{self.name.lower().replace('.', '_')}")

    def get_headers(self) -> Dict[str, str]:
        """
        Gets headers for the request.
        """
        return {
            "User-Agent": __user_agent__,
            "Accept": "application/json"
        }

    @contextmanager
    def with_session(self, session: Optional[httpx.Client] = None) -> "httpx.Client":
        """
        Return a client session, closing it properly if it was created by this method.
        """
        if not session:
            with httpx.Client(headers=self.get_headers()) as session:
                yield session
        else:
            yield session

    @overload
    def create_paste(self, files: BaseFile) -> BaseResult:
        ...

    @overload
    def create_paste(self, *files: BaseFile) -> List[BaseResult]:
        ...

    @abc.abstractmethod
    def create_paste(
            self,
            *files: BaseFile
    ) -> Union[BaseResult, List[BaseResult]]:
        """
        Creates a paste.

        :param files: The files to upload
        :return: The paste result. Can be multiple if multiple files were uploaded.
        """
        raise NotImplementedError

    @overload
    async def async_create_paste(self, files: BaseFile) -> BaseResult:
        ...

    @overload
    async def async_create_paste(self, *files: BaseFile) -> List[BaseResult]:
        ...

    async def async_create_paste(self, *files: BaseFile) -> Union[BaseResult, List[BaseResult]]:
        """
        Creates a paste asynchronously.

        internally, this function just calls `create_paste` in a thread, to make it non-blocking.

        :param files: The files to upload
        :return: The paste result. Can be multiple if multiple files were uploaded.
        """
        return await asyncio.to_thread(self.create_paste, *files)

    @abc.abstractmethod
    def get_paste(self, key: str) -> BaseFile:
        """
        Gets a paste.

        :param key: The paste key
        :return: The paste file
        """
        raise NotImplementedError
