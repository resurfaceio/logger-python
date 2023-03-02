# coding: utf-8
# © 2016-2023 Resurface Labs Inc.

from tests.test_helper import DEMO_URL
from usagelogger import HttpLogger, UsageLoggers


def test_creates_instance():
    logger = HttpLogger()
    assert logger is not None
    assert logger.agent == HttpLogger.AGENT
    assert logger.enableable is False
    assert logger.enabled is False
    assert logger.queue is None
    assert logger.url is None


def test_creates_multiple_instances():
    url1 = "https://resurface.io"
    url2 = "https://whatever.com"
    logger1 = HttpLogger(url=url1)
    logger2 = HttpLogger(url=url2)
    logger3 = HttpLogger(url=DEMO_URL)

    assert logger1.agent == HttpLogger.AGENT
    assert logger1.enableable is True
    assert logger1.enabled is True
    assert logger1.url == url1
    assert logger2.agent == HttpLogger.AGENT
    assert logger2.enableable is True
    assert logger2.enabled is True
    assert logger2.url == url2
    assert logger3.agent == HttpLogger.AGENT
    assert logger3.enableable is True
    assert logger3.enabled is True
    assert logger3.url == DEMO_URL

    UsageLoggers.disable()
    assert UsageLoggers.is_enabled() is False
    assert logger1.enabled is False
    assert logger2.enabled is False
    assert logger3.enabled is False
    UsageLoggers.enable()
    assert UsageLoggers.is_enabled() is True
    assert logger1.enabled is True
    assert logger2.enabled is True
    assert logger3.enabled is True


def test_has_valid_agent():
    agent = HttpLogger.AGENT
    assert len(agent) > 0
    assert agent.endswith(".py")
    assert ("\\" in agent) is False
    assert ('"' in agent) is False
    assert ("'" in agent) is False
    assert HttpLogger().agent == agent


def test_silently_ignores_unexpected_option_classes():
    logger = HttpLogger(DEMO_URL)
    assert logger.enableable is False
    assert logger.enabled is False
    assert logger.queue is None
    assert logger.url is None

    logger = HttpLogger(True)
    assert logger.enableable is False
    assert logger.enabled is False
    assert logger.queue is None
    assert logger.url is None

    logger = HttpLogger([])
    assert logger.enableable is False
    assert logger.enabled is False
    assert logger.queue is None
    assert logger.url is None

    logger = HttpLogger(url=[])
    assert logger.enableable is False
    assert logger.enabled is False
    assert logger.queue is None
    assert logger.url is None

    logger = HttpLogger(url=23)
    assert logger.enableable is False
    assert logger.enabled is False
    assert logger.queue is None
    assert logger.url is None

    logger = HttpLogger(queue="asdf")
    assert logger.enableable is False
    assert logger.enabled is False
    assert logger.queue is None
    assert logger.url is None

    logger = HttpLogger(queue=45)
    assert logger.enableable is False
    assert logger.enabled is False
    assert logger.queue is None
    assert logger.url is None

    logger = HttpLogger(enabled=2)
    assert logger.enableable is False
    assert logger.enabled is False
    assert logger.queue is None
    assert logger.url is None
