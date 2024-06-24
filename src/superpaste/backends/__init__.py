from ._generic import GenericBackend, GenericFile, GenericResult
from .base import BaseBackend, BaseFile, BaseResult, as_chunks
from .hastebin_com import HastebinBackend
from .hastebin_skyra_pw import HastebinSkyraPWBackend
from .hst_sh import HstSHBackend
from .mystb_in import MystbinBackend, MystbinFile, MystbinResult
from .paste_ee import PasteEEBackend, PasteEEFile


__backends__ = [
    BaseBackend,
    HastebinBackend,
    HastebinSkyraPWBackend,
    HstSHBackend,
    MystbinBackend,
    PasteEEBackend
]


__all__ = [
    "GenericBackend",
    "BaseBackend",
    "BaseFile",
    "BaseResult",
    "HastebinBackend",
    "HastebinSkyraPWBackend",
    "HstSHBackend",
    "MystbinBackend",
    "MystbinFile",
    "MystbinResult",
    "PasteEEBackend",
    "PasteEEFile",
    "as_chunks"
]
