# © 2016-2019 Resurface Labs Inc.

import os


class UsageLoggers(object):

    DISABLED = os.getenv('USAGE_LOGGERS_DISABLE') == 'True'
    _disabled = DISABLED

    @classmethod
    def disable(cls):
        cls._disabled = True

    @classmethod
    def enable(cls):
        if cls.DISABLED is False:
            cls._disabled = False

    @classmethod
    def is_enabled(cls):
        return not cls._disabled

    @staticmethod
    def url_by_default():
        return os.getenv('USAGE_LOGGERS_URL')
