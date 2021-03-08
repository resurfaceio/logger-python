# coding: utf-8
# © 2016-2021 Resurface Labs Inc.

import random
import time
from typing import List

from tests.test_helper import *
from usagelogger import BaseLogger


def test_background_workers() -> None:
    logger = BaseLogger(MOCK_AGENT, url=DEMO_URL)
    for _ in range(10):
        logger.submit("{}")
        time.sleep(random.random() * 2)
    logger.wait_for_response()
    assert logger.submit_successes == 10


def test_multiple_loggers() -> None:
    loggers: List = [BaseLogger(MOCK_AGENT, url=DEMO_URL) for _ in range(4)]
    for logger in loggers:
        for _ in range(5):
            logger.submit("{}")
        logger.wait_for_response()
    assert logger.submit_successes == 5


def test_bounded_queue() -> None:
    logger = BaseLogger(MOCK_AGENT, url=DEMO_URL, max_concurrent=2)
    for _ in range(10):
        logger.submit("{}")
    logger.wait_for_response()
    assert logger.submit_successes == 10
