# coding: utf-8
# © 2016-2019 Resurface Labs Inc.
import re
from typing import List, Pattern
from usagelogger.http_rule import HttpRule


class HttpRules(object):

    @classmethod
    def debug_rules(cls) -> str:
        return (r"allow_http_url" "\n"
                r"copy_session_field /.*/" "\n")

    @classmethod
    def standard_rules(cls) -> str:
        return ("/request_header:cookie|response_header:set-cookie/ remove\n"
                r'/(request|response)_body|request_param/ replace '
                r'/[a-zA-Z0-9.!#$%&’*+\/=?^_`{|}~-]+@[a-zA-Z0-9-]+'
                r'(?:\.[a-zA-Z0-9-]+)/, /x@y.com/' "\n"
                r'/request_body|request_param|response_body/ replace '
                r'/[0-9\.\-\/]{9,}/, /xyxy/' "\n")

    @classmethod
    def strict_rules(cls) -> str:
        return (r'/request_url/ replace /([^\?;]+).*/, !\\1!' "\n"
                r'/request_body|response_body|request_param:.*|'
                r'request_header:(?!user-agent).*|response_header:'
                r'(?!(content-length)|(content-type)).*/ remove' "\n")

    @classmethod
    def parse(cls, rules: str) -> List[HttpRule]:
        """Parses rules from multi-line string."""
        # TODO: Implement me.
        return []

    @classmethod
    def parse_rule(cls, rule: str) -> HttpRule:
        """Parses rule from single line."""
        # TODO: Implement me.
        pass

    @classmethod
    def _parse_regex(cls, rule: str, regex: str) -> Pattern:
        """Parses regex for matching."""
        # TODO: Implement me.
        pass

    @classmethod
    def _parse_regex_find(cls, rule: str, regex: str) -> Pattern:
        """Parses regex for finding."""
        # TODO: Implement me.
        pass

    @classmethod
    def _parse_string(cls, rule: str, string: str) -> str:
        """Parses delimited string expression."""
        pass

    _REGEX_ALLOW_HTTP_URL: Pattern = re.compile(
        r'^\s*allow_http_url\s*(#.*)?$')
    _REGEX_BLANK_OR_COMMENT: Pattern = re.compile(
        r'^\s*([#].*)*$')
    _REGEX_COPY_SESSION_FIELD: Pattern = re.compile(
        r'^\s*copy_session_field\s+([~!%|/].+[~!%|/])\s*(#.*)?$')
    _REGEX_REMOVE: Pattern = re.compile(
        r'^\s*([~!%|/].+[~!%|/])\s*remove\s*(#.*)?$')
    _REGEX_REMOVE_IF: Pattern = re.compile(
        r'^\s*([~!%|/].+[~!%|/])\s*remove_if\s+([~!%|/].+[~!%|/])\s*(#.*)?$')
    _REGEX_REMOVE_IF_FOUND: Pattern = re.compile(
        r'^\s*([~!%|/].+[~!%|/])\s*'
        r'remove_if_found\s+([~!%|/].+[~!%|/])\s*(#.*)?$')
    _REGEX_REMOVE_UNLESS: Pattern = re.compile(
        r'^\s*([~!%|/].+[~!%|/])\s*'
        r'remove_unless\s+([~!%|/].+[~!%|/])\s*(#.*)?$')
    _REGEX_REMOVE_UNLESS_FOUND: Pattern = re.compile(
        r'^\s*([~!%|/].+[~!%|/])\s*'
        r'remove_unless_found\s+([~!%|/].+[~!%|/])\s*(#.*)?$')
    _REGEX_REPLACE: Pattern = re.compile(
        r'^\s*([~!%|/].+[~!%|/])\s*'
        r'replace[\s]+([~!%|/].+[~!%|/]),[\s]+([~!%|/].*[~!%|/])\s*(#.*)?$')
    _REGEX_SAMPLE: Pattern = re.compile(
        r'^\s*sample\s+(\d+)\s*(#.*)?$')
    _REGEX_SKIP_COMPRESSION: Pattern = re.compile(
        r'^\s*skip_compression\s*(#.*)?$')
    _REGEX_SKIP_SUBMISSION: Pattern = re.compile(
        r'^\s*skip_submission\s*(#.*)?$')
    _REGEX_STOP: Pattern = re.compile(
        r'^\s*([~!%|/].+[~!%|/])\s*stop\s*(#.*)?$')
    _REGEX_STOP_IF: Pattern = re.compile(
        r'^\s*([~!%|/].+[~!%|/])\s*stop_if\s+([~!%|/].+[~!%|/])\s*(#.*)?$')
    _REGEX_STOP_IF_FOUND: Pattern = re.compile(
        r'^\s*([~!%|/].+[~!%|/])\s*'
        r'stop_if_found\s+([~!%|/].+[~!%|/])\s*(#.*)?$')
    _REGEX_STOP_UNLESS: Pattern = re.compile(
        r'^\s*([~!%|/].+[~!%|/])\s*stop_unless\s+([~!%|/].+[~!%|/])\s*(#.*)?$')
    _REGEX_STOP_UNLESS_FOUND: Pattern = re.compile(
        r'^\s*([~!%|/].+[~!%|/])\s*'
        r'stop_unless_found\s+([~!%|/].+[~!%|/])\s*(#.*)?$')
