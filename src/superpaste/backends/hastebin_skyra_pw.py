"""
Backend for posting pastes to http://hastebin.skyra.pw
"""
# Note (2024-06-23): hastebin.skyra.pw uses the same backend as hst.sh
from .hst_sh import *


class HastebinSkyraPWBackend(HstSHBackend):
    name = "hastebin.skyra.pw"
    base_url = "https://hastebin.skyra.pw"
    post_url = "https://hastebin.skyra.pw/documents"
    html_url = "https://hastebin.skyra.pw/{key}"

    def __init__(self, session: httpx.Client = None):
        super().__init__(session=session)
