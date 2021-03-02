import json
import logging
import os
import unittest
from typing import List

from usagelogger import BaseLogger


class TestBaseLogger(unittest.TestCase):
    def setUp(self) -> None:
        import requests

        self.logger = BaseLogger(
            "helper.py", url="https://demo.resurface.io/ping", conn=requests.Session()
        )

    def tearDown(self) -> None:
        logging.shutdown()
        os.remove("test_debug.log")

    def test_requests_keep_alive(self) -> None:
        for _ in range(3):
            message: List[List[str]] = [
                ["agent", self.logger.agent],
                ["version", self.logger.version],
                ["now", "1455908640173"],
                ["prototol", "https"],
            ]
            msg = json.dumps(message, separators=(",", ":"))
            self.logger.submit(msg)

        with open("test_debug.log", "r") as f:
            self.assertEqual(
                sum(
                    [
                        "new https connection (1): demo.resurface.io:443" in x.lower()
                        for x in f.readlines()
                    ]
                ),
                1 + 1,  # One for earlier test's http connection
            )
