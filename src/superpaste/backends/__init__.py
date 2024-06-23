from typing import Type
from .base import BaseBackend, BasePasteFile, BasePasteResult, BasePasteFileProtocol, as_chunks
from .hastebin_com import HastebinBackend
from .hst_sh import HstSHBackend
from .mystb_in import MystbinBackend, MystbinFile, MystbinResult
from .paste_ee import PasteEEBackend, PasteEEFile
from .hastebin_skyra_pw import HastebinSkyraPWBackend


__backends__ = [
    "HstSHBackend",
    "MystbinBackend",
    "HastebinBackend",
    "PasteEEBackend",
    "HastebinSkyraPWBackend",
]


__all__ = [
    "BasePasteFile",
    "BasePasteResult",
    "BasePasteFileProtocol",
    "as_chunks",
    "MystbinFile",
    "MystbinResult",
    "PasteEEFile",
    "__backends__",
    *__backends__,
]
