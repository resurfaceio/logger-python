# coding: utf-8
# © 2016-2021 Resurface Labs Inc.

from typing import Dict, Optional


class HttpResponseImpl(object):

    def __init__(self, status: Optional[int] = None,
                 headers: Optional[Dict[str, str]] = None,
                 body: Optional[str] = None) -> None:
        self.status = status
        self.headers = {} if headers is None else headers
        self.body = body
