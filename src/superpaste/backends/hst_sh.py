"""
Backend for posting pastes to http://hst.sh.
"""
from ._generic import GenericBackend

__author__ = "nexy7574 <https://github.com/nexy7574>"


class HstSHBackend(GenericBackend):
    name = "hst.sh"
    base_url = "https://hst.sh"
