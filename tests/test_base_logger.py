# coding: utf-8
# © 2016-2021 Resurface Labs Inc.

from typing import List

from tests.test_helper import *
from usagelogger import BaseLogger, UsageLoggers


def test_creates_instance():
    logger = BaseLogger(MOCK_AGENT)
    assert logger is not None
    assert logger.agent == MOCK_AGENT
    assert logger.enableable is False
    assert logger.enabled is False
    assert logger.queue is None
    assert logger.url is None


def test_creates_multiple_instances():
    agent1 = "agent1"
    agent2 = "AGENT2"
    agent3 = "aGeNt3"
    url1 = "http://resurface.io"
    url2 = "http://whatever.com"
    logger1 = BaseLogger(agent1, url=url1)
    logger2 = BaseLogger(agent2, url=url2)
    logger3 = BaseLogger(agent3, url=DEMO_URL)

    assert logger1.agent == agent1
    assert logger1.enableable is True
    assert logger1.enabled is True
    assert logger1.url == url1
    assert logger2.agent == agent2
    assert logger2.enableable is True
    assert logger2.enabled is True
    assert logger2.url == url2
    assert logger3.agent == agent3
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


def test_has_valid_host():
    host = BaseLogger.host_lookup()
    assert host is not None
    assert len(host) > 0
    assert host != "unknown"
    assert host == BaseLogger(MOCK_AGENT).host


def test_has_valid_version():
    version = BaseLogger.version_lookup()
    assert version is not None
    assert len(version) > 0
    assert version.startswith("2.2.")
    assert ("\\" in version) is False
    assert ('"' in version) is False
    assert ("'" in version) is False
    assert version == BaseLogger(MOCK_AGENT).version


def test_performs_enabling_when_expected():
    logger = BaseLogger(MOCK_AGENT, url=DEMO_URL, enabled=False)
    assert logger.enableable is True
    assert logger.enabled is False
    assert logger.url == DEMO_URL
    logger.enable()
    assert logger.enabled is True

    logger = BaseLogger(MOCK_AGENT, queue=[], enabled=False)
    assert logger.enableable is True
    assert logger.enabled is False
    assert logger.url is None
    logger.enable().disable().enable()
    assert logger.enabled is True


def test_skips_enabling_for_invalid_urls():
    for invalid_url in MOCK_URLS_INVALID:
        logger = BaseLogger(MOCK_AGENT, url=invalid_url)
        assert logger.enableable is False
        assert logger.enabled is False
        assert logger.url is None
        logger.enable()
        assert logger.enabled is False


def test_skips_enabling_for_missing_url():
    logger = BaseLogger(MOCK_AGENT)
    assert logger.enableable is False
    assert logger.enabled is False
    assert logger.url is None
    logger.enable()
    assert logger.enabled is False


def test_skips_enabling_for_undefined_url():
    logger = BaseLogger(MOCK_AGENT, url=None)
    assert logger.enableable is False
    assert logger.enabled is False
    assert logger.url is None
    logger.enable()
    assert logger.enabled is False


def test_submits_to_demo_url():
    logger = BaseLogger(MOCK_AGENT, url=DEMO_URL)
    assert logger.url == DEMO_URL
    message: List[List[str]] = [
        ["agent", logger.agent],
        ["version", logger.version],
        ["now", str(MOCK_NOW)],
        ["prototol", "https"],
    ]
    msg = json.dumps(message, separators=(",", ":"))
    assert parseable(msg) is True
    logger.submit(msg)
    assert logger.submit_failures == 0
    assert logger.submit_successes == 1


def test_submits_to_demo_url_via_http():
    logger = BaseLogger(MOCK_AGENT, url=DEMO_URL.replace("https", "http", 1))
    assert logger.url.startswith("http://") is True
    message: List[List[str]] = [
        ["agent", logger.agent],
        ["version", logger.version],
        ["now", str(MOCK_NOW)],
        ["prototol", "http"],
    ]
    msg = json.dumps(message, separators=(",", ":"))
    assert parseable(msg) is True
    logger.submit(msg)
    assert logger.submit_failures == 0
    assert logger.submit_successes == 1


def test_submits_to_demo_url_without_compression():
    logger = BaseLogger(MOCK_AGENT, url=DEMO_URL)
    logger.skip_compression = True
    assert logger.skip_compression is True
    message: List[List[str]] = [
        ["agent", logger.agent],
        ["version", logger.version],
        ["now", str(MOCK_NOW)],
        ["prototol", "https"],
        ["skip_compression", "true"],
    ]
    msg = json.dumps(message, separators=(",", ":"))
    assert parseable(msg) is True
    logger.submit(msg)
    assert logger.submit_failures == 0
    assert logger.submit_successes == 1


def test_submits_to_denied_url():
    for denied_url in MOCK_URLS_DENIED:
        logger = BaseLogger(MOCK_AGENT, url=denied_url)
        assert logger.enableable is True
        assert logger.enabled is True
        logger.submit("{}")
        assert logger.submit_failures == 1
        assert logger.submit_successes == 0


def test_submits_to_queue():
    queue = []
    logger = BaseLogger(MOCK_AGENT, queue=queue, url=MOCK_URLS_DENIED[0])
    assert logger.queue == queue
    assert logger.url is None
    assert logger.enableable is True
    assert logger.enabled is True
    assert len(queue) == 0
    logger.submit("{}")
    assert len(queue) == 1
    logger.submit("{}")
    assert len(queue) == 2
    assert logger.submit_failures == 0
    assert logger.submit_successes == 2


def test_silently_ignores_unexpected_option_classes():
    logger = BaseLogger(MOCK_AGENT, DEMO_URL)
    assert logger.enableable is False
    assert logger.enabled is False
    assert logger.queue is None
    assert logger.url is None

    logger = BaseLogger(MOCK_AGENT, True)
    assert logger.enableable is False
    assert logger.enabled is False
    assert logger.queue is None
    assert logger.url is None

    logger = BaseLogger(MOCK_AGENT, [])
    assert logger.enableable is False
    assert logger.enabled is False
    assert logger.queue is None
    assert logger.url is None

    logger = BaseLogger(MOCK_AGENT, url=[])
    assert logger.enableable is False
    assert logger.enabled is False
    assert logger.queue is None
    assert logger.url is None

    logger = BaseLogger(MOCK_AGENT, url=23)
    assert logger.enableable is False
    assert logger.enabled is False
    assert logger.queue is None
    assert logger.url is None

    logger = BaseLogger(MOCK_AGENT, queue="asdf")
    assert logger.enableable is False
    assert logger.enabled is False
    assert logger.queue is None
    assert logger.url is None

    logger = BaseLogger(MOCK_AGENT, queue=45)
    assert logger.enableable is False
    assert logger.enabled is False
    assert logger.queue is None
    assert logger.url is None

    logger = BaseLogger(MOCK_AGENT, enabled=2)
    assert logger.enableable is False
    assert logger.enabled is False
    assert logger.queue is None
    assert logger.url is None


def test_uses_skip_options():
    logger = BaseLogger(MOCK_AGENT, url=DEMO_URL)
    assert logger.skip_compression is False
    assert logger.skip_submission is False

    logger.skip_compression = True
    assert logger.skip_compression is True
    assert logger.skip_submission is False

    logger.skip_compression = False
    logger.skip_submission = True
    assert logger.skip_compression is False
    assert logger.skip_submission is True
