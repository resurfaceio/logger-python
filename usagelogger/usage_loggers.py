# coding: utf-8
# © 2016-2021 Resurface Labs Inc.

from os import getenv
from typing import Optional


class UsageLoggers(object):
    __BRICKED: bool = getenv("USAGE_LOGGERS_DISABLE") == "true"

    __disabled: bool = __BRICKED

    @classmethod
    def disable(cls) -> None:
        cls.__disabled = True

    @classmethod
    def enable(cls) -> None:
        if cls.__BRICKED is False:
            cls.__disabled = False

    @classmethod
    def is_enabled(cls) -> bool:
        return not cls.__disabled

    @staticmethod
    def url_by_default() -> Optional[str]:
        return getenv("USAGE_LOGGERS_URL")
