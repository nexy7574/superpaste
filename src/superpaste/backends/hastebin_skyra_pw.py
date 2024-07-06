"""
Backend for posting pastes to http://hastebin.skyra.pw
"""
# Note (2024-06-23): hastebin.skyra.pw uses the same backend as hst.sh
from ._generic import GenericBackend, GenericFile, GenericResult


__all__ = ("HastebinSkyraPWBackend", "HastebinSkyraPWFile", "HastebinSkyraPWResult")

HastebinSkyraPWFile = GenericFile
HastebinSkyraPWResult = GenericResult


class HastebinSkyraPWBackend(GenericBackend):
    name = "skyra.pw"
    base_url = "https://hastebin.skyra.pw"
