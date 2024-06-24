"""
Backend for posting pastes to http://hastebin.skyra.pw
"""
# Note (2024-06-23): hastebin.skyra.pw uses the same backend as hst.sh
from ._generic import GenericBackend


__all__ = ("HastebinSkyraPWBackend",)


class HastebinSkyraPWBackend(GenericBackend):
    name = "skyra.pw"
    base_url = "https://hastebin.skyra.pw"
