# coding: utf-8
# © 2016-2021 Resurface Labs Inc.
from typing import Optional, Pattern, Union


class HttpRule(object):
    def __init__(
        self,
        verb: str,
        scope: Optional[Pattern] = None,
        param1: Optional[Union[Pattern, str, int]] = None,
        param2: Optional[Union[Pattern, str]] = None,
    ) -> None:
        self._verb = verb
        self._scope = scope
        self._param1 = param1
        self._param2 = param2

    @property
    def verb(self):
        return self._verb

    @property
    def scope(self):
        return self._scope

    @property
    def param1(self):
        return self._param1

    @property
    def param2(self):
        return self._param2
