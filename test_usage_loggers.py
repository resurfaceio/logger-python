# © 2016-2019 Resurface Labs Inc.

from usagelogger import UsageLoggers


def test_provides_default_url():
    assert UsageLoggers.url_by_default() is None
