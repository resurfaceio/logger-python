# coding: utf-8
# © 2016-2022 Resurface Labs Inc.

from usagelogger import UsageLoggers


def test_provides_default_url():
    assert UsageLoggers.url_by_default() is None
