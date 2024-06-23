from .base import BaseBackend, BasePasteFile, BasePasteResult
from .hastebin_com import HastebinBackend
from .hst_sh import HstSHBackend
from .mystb_in import MystbinBackend, MystbinFile, MystbinResult
from .paste_ee import PasteEEBackend, PasteEEFile
from .hastebin_skyra_pw import HastebinSkyraPWBackend

__all__ = [
    "BaseBackend",
    "BasePasteFile",
    "BasePasteResult",
    "HstSHBackend",
    "MystbinBackend",
    "MystbinFile",
    "MystbinResult",
    "HastebinBackend",
    "PasteEEBackend",
    "PasteEEFile",
    "HastebinSkyraPWBackend",
]
