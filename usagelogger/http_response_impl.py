# coding: utf-8
# © 2016-2019 Resurface Labs Inc.
from typing import Dict, Optional, Union


class HttpResponseImpl(object):

    def __init__(self, status: Optional[int] = None,
                 headers: Optional[Dict[str, str]] = None,
                 body: Optional[Union[bytes, str]] = None) -> None:

        self.reason: str = ''

        self.status = status
        self.headers = {} if headers is None else headers
        self.body = body

    @property
    def body(self):
        return self._body

    @body.setter
    def body(self, value: Optional[Union[bytes, str]]):
        if isinstance(value, str):
            self._body = bytes(value, 'utf8')
        elif isinstance(value, bytes):
            self._body = value

    def get_headers(self):
        return self.headers.items()
