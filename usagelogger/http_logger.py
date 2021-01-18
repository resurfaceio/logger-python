# coding: utf-8
# © 2016-2021 Resurface Labs Inc.

import json
import re
from typing import List, Optional, Pattern

from usagelogger.base_logger import BaseLogger
from usagelogger.http_rules import HttpRules


class HttpLogger(BaseLogger):
    """Usage logger for HTTP/HTTPS protocol."""

    # Agent string identifying this logger.
    AGENT: str = 'http_logger.py'

    def __init__(self, enabled: Optional[bool] = True,
                 queue: Optional[List[str]] = None,
                 url: Optional[str] = None,
                 skip_compression: Optional[bool] = False,
                 skip_submission: Optional[bool] = False,
                 rules: Optional[str] = None) -> None:

        super().__init__(self.AGENT, enabled=enabled, queue=queue, url=url,
                         skip_compression=skip_compression, skip_submission=skip_submission)

        # parse specified rules
        self._rules = HttpRules(rules)

        # apply configuration rules
        self.skip_compression = self._rules.skip_compression
        self.skip_submission = self._rules.skip_submission
        if self._enabled and url is not None and url.startswith('http:') and not self._rules.allow_http_url:
            self._enableable = False
            self._enabled = False

    @property
    def rules(self) -> HttpRules:
        return self._rules

    def submit_if_passing(self, details: List[List[str]]) -> None:
        # apply active rules
        details = self._rules.apply(details)
        if details is None: return

        # finalize message
        details.append(['agent', self.AGENT])
        details.append(['host', self.host])
        details.append(['version', self.version])

        # let's do this thing
        self.submit(json.dumps(details, separators=(',', ':')))

    @classmethod
    def is_string_content_type(cls, s: str) -> bool:
        return s is not None and cls.__STRING_TYPES_REGEX.match(s) is not None

    __STRING_TYPES: str = (r'^(text/(html|plain|xml))|'
                           r'(application/(json|soap|xml|x-www-form-urlencoded))')
    __STRING_TYPES_REGEX: Pattern = re.compile(__STRING_TYPES, flags=re.IGNORECASE)
