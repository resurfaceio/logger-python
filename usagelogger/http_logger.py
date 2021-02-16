# coding: utf-8
# © 2016-2021 Resurface Labs Inc.

import json
from typing import List, Optional

from usagelogger.base_logger import BaseLogger
from usagelogger.http_rules import HttpRules


class HttpLogger(BaseLogger):
    """Usage logger for HTTP/HTTPS protocol."""

    # Agent string identifying this logger.
    AGENT: str = "http_logger.py"

    def __init__(
        self,
        enabled: bool = True,
        queue: Optional[List[str]] = None,
        url: Optional[str] = None,
        skip_compression: bool = False,
        skip_submission: bool = False,
        rules: Optional[str] = None,
    ) -> None:

        super().__init__(
            self.AGENT,
            enabled=enabled,
            queue=queue,
            url=url,
            skip_compression=skip_compression,
            skip_submission=skip_submission,
        )

        # parse specified rules
        self._rules = HttpRules(rules)  # type: ignore

        # apply configuration rules
        self.skip_compression = self._rules.skip_compression
        self.skip_submission = self._rules.skip_submission
        if (
            self._enabled
            and url is not None
            and url.startswith("http:")
            and not self._rules.allow_http_url
        ):
            self._enableable = False
            self._enabled = False

    @property
    def rules(self) -> HttpRules:
        return self._rules

    def submit_if_passing(self, details: List[List[str]]) -> None:
        # apply active rules
        details = self._rules.apply(details)  # type: ignore
        if details is None:
            return

        # finalize message
        details.append(["host", self.host])

        # let's do this thing
        self.submit(json.dumps(details, separators=(",", ":")))
