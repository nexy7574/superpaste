"""
Backend for posting pastes to http://hst.sh.
"""

from ._generic import GenericBackend, GenericFile, GenericResult

__author__ = "nexy7574 <https://github.com/nexy7574>"
__all__ = ("HstSHBackend", "HstFile", "HstResult")

HstFile = GenericFile
HstResult = GenericResult


class HstSHBackend(GenericBackend):
    name = "hst.sh"
    base_url = "https://hst.sh"
