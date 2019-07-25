# coding: utf-8
# © 2016-2019 Resurface Labs Inc.

import os


class UsageLoggers(object):

    DISABLED: bool = os.getenv('USAGE_LOGGERS_DISABLE') == 'True'
    _disabled: bool = DISABLED

    @classmethod
    def disable(cls) -> None:
        cls._disabled = True

    @classmethod
    def enable(cls) -> None:
        if cls.DISABLED is False:
            cls._disabled = False

    @classmethod
    def is_enabled(cls) -> bool:
        return not cls._disabled

    @staticmethod
    def url_by_default() -> str:
        return os.getenv('USAGE_LOGGERS_URL')
