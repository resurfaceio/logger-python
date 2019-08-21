# coding: utf-8
# © 2016-2019 Resurface Labs Inc.

import json
import re
from time import time
from typing import List, Optional, Pattern
import usagelogger
from usagelogger.http_rule import HttpRule


class MetaHttpLogger(type):
    """
    Implement a proper getter/setter for default_rules class variable
    using a metaclass since Python properties only work for instance
    variables by default.
    """
    _default_rules: str = ''

    @property
    def default_rules(cls) -> str:
        return cls._default_rules

    @default_rules.setter
    def default_rules(cls, rules: str) -> None:
        cls._default_rules: str = re.sub(r'^\s*include default\s*$', '',
                                         rules, flags=re.MULTILINE)


class HttpLogger(usagelogger.BaseLogger, metaclass=MetaHttpLogger):
    """Usage logger for HTTP/HTTPS protocol."""

    # Agent string identifying this logger.
    AGENT: str = 'http_logger.py'

    _default_rules: str = usagelogger.HttpRules.strict_rules()

    # To avoid mistakes ensure self.default_rules == HttpLogger.default_rules
    # because... Python
    @property
    def default_rules(self) -> str:
        return str(HttpLogger.default_rules)

    @default_rules.setter
    def default_rules(self, value: str) -> None:
        HttpLogger.default_rules = value

    @staticmethod
    def is_string_content_type(content: str) -> bool:
        string_types: str = (
            r'^(text/(html|plain|xml))|'
            r'(application/(json|soap|xml|x-www-form-urlencoded))')
        pattern: Pattern = re.compile(string_types, flags=re.IGNORECASE)
        return content is not None and pattern.match(content) is not None

    def __init__(self, _agent_unused=None,
                 enabled: Optional[bool] = True,
                 queue: Optional[List[str]] = None,
                 url: Optional[str] = usagelogger.UsageLoggers.url_by_default(),
                 skip_compression: Optional[bool] = False,
                 skip_submission: Optional[bool] = False,
                 rules: Optional[str] = None) -> None:
        """
        Initialize enabled/disabled logger
        using specified url and default rules.
        """

        super().__init__(self.AGENT, enabled=enabled, queue=queue, url=url,
                         skip_compression=skip_compression,
                         skip_submission=skip_submission)

        if rules is not None:
            self.rules: str = re.sub(r'^\s*include default\s*$',
                                     str(self.default_rules),
                                     rules, flags=re.MULTILINE)
            if len(self.rules.strip()) == 0:
                self.rules: str = self.default_rules
        else:
            self.rules: str = self.default_rules

        # parse and break rules out by verb
        prs: List[HttpRule] = usagelogger.HttpRules.parse(self.rules)
        self.rules_allow_http_url: bool = len([
            r for r in prs if 'allow_http_url' == r.verb]) > 0
        self.rules_copy_session_field: List[HttpRule] = [
            r for r in prs if 'rs_copy_session_field' == r.verb]
        self.rules_remove: List[HttpRule] = [
            r for r in prs if 'rules_remove' == r.verb]
        self.rules_remove_if: List[HttpRule] = [
            r for r in prs if 'rules_remove_if' == r.verb]
        self.rules_remove_if_found: List[HttpRule] = [
            r for r in prs if 'rules_remove_if_found' == r.verb]
        self.rules_remove_unless: List[HttpRule] = [
            r for r in prs if 'rules_remove_unless' == r.verb]
        self.rules_remove_unless_found: List[HttpRule] = [
            r for r in prs if 'rules_remove_unless_found' == r.verb]
        self.rules_replace: List[HttpRule] = [
            r for r in prs if 'rules_replace' == r.verb]
        self.rules_sample: List[HttpRule] = [
            r for r in prs if 'rules_sample' == r.verb]
        self.rules_stop: List[HttpRule] = [
            r for r in prs if 'rules_stop' == r.verb]
        self.rules_stop_if: List[HttpRule] = [
            r for r in prs if 'rules_stop_if' == r.verb]
        self.rules_stop_if_found: List[HttpRule] = [
            r for r in prs if 'rules_stop_if_found' == r.verb]
        self.rules_stop_unless: List[HttpRule] = [
            r for r in prs if 'rules_stop_unless' == r.verb]
        self.rules_stop_unless_found: List[HttpRule] = [
            r for r in prs if 'rules_stop_unless_found' == r.verb]
        self.skip_compression: bool = len([
            r for r in prs if r.verb == 'skip_compression']) > 0
        self.skip_submission: bool = len([
            r for r in prs if r.verb == 'skip_submission']) > 0

        # finish validating rules
        if len(self.rules_sample) > 1:
            raise SyntaxError('Multiple sample rules')
        if self._enabled and url is not None \
                and url.startswith('http:') \
                and not self.rules_allow_http_url:
            self._enableable = False
            self._enabled = False

    def log(self, request: usagelogger.HttpRequestImpl,
            response: usagelogger.HttpResponseImpl,
            response_body: Optional[str] = None,
            request_body: Optional[str] = None) -> bool:
        """Logs HTTP request and response to intended destination."""

        if self.enabled:
            return self.submit(
                self.format(request, response, response_body, request_body))
        return True

    def format(self, request: usagelogger.HttpRequestImpl,
               response: usagelogger.HttpResponseImpl,
               response_body: Optional[str] = None,
               request_body: Optional[str] = None,
               now: Optional[int] = None) -> str:
        """Formats HTTP request and response as JSON message."""

        details: List[List[str]] = usagelogger.HttpMessage.build(
            request, response, response_body, request_body)

        # TODO: copy data from session if configured
        # TODO: quit early based on stop rules if configured
        # TODO: do sampling if configured
        # TODO: winnow sensitive details based on remove rules if configured
        # TODO: mask sensitive details based on replace rules if configured
        # TODO: remove any details with empty values

        details.append(['now', str(now)if now is not None else str(
            round(time() * 1000))])
        details.append(['agent', self.AGENT])
        details.append(['version', self.version])
        return json.dumps(details, separators=(',', ':'))
