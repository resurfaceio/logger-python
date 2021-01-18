# coding: utf-8
# © 2016-2021 Resurface Labs Inc.

from typing import Dict, Optional


class HttpRequestImpl(object):

    def __init__(self, method: Optional[str] = None,
                 url: Optional[str] = None,
                 headers: Optional[Dict[str, str]] = None,
                 params: Optional[Dict[str, str]] = None,
                 body: Optional[str] = None) -> None:
        self.method = method
        self.url = url
        self.headers = {} if headers is None else headers
        self.params = {} if params is None else params
        self.body = body
