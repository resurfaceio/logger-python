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
        result: List = []
        if rules is not None:
            rules = re.sub(r'(?m)^\s*include debug\s*$', HttpRules.debug_rules(), rules)
            rules = re.sub(r'(?m)^\s*include standard\s*$', HttpRules.standard_rules(), rules)
            rules = re.sub(r'(?m)^\s*include strict\s*$', HttpRules.strict_rules(), rules)
            for rule in rules.split("\n"):
                parsed: HttpRule = HttpRules.parse_rule(rule)
                if parsed is not None: result.append(parsed)
        return result

    @classmethod
    def parse_rule(cls, rule: str) -> HttpRule:
        """Parses rule from single line."""
        if rule is None or HttpRules._REGEX_BLANK_OR_COMMENT.match(rule): return None
        m = HttpRules._REGEX_ALLOW_HTTP_URL.match(rule)
        if m: return HttpRule('allow_http_url')
        m = HttpRules._REGEX_COPY_SESSION_FIELD.match(rule)
        if m: return HttpRule('copy_session_field', None, HttpRules._parse_regex(rule, m.group(1)))
        m = HttpRules._REGEX_REMOVE.match(rule)
        if m: return HttpRule('remove', HttpRules._parse_regex(rule, m.group(1)))
        m = HttpRules._REGEX_REMOVE_IF.match(rule)
        if m: return HttpRule('remove_if', HttpRules._parse_regex(rule, m.group(1)), HttpRules._parse_regex(rule, m.group(2)))
        m = HttpRules._REGEX_REMOVE_IF_FOUND.match(rule)
        if m: return HttpRule('remove_if_found', HttpRules._parse_regex(rule, m.group(1)),
                              HttpRules._parse_regex_find(rule, m.group(2)))
        m = HttpRules._REGEX_REMOVE_UNLESS.match(rule)
        if m: return HttpRule('remove_unless', HttpRules._parse_regex(rule, m.group(1)), HttpRules._parse_regex(rule, m.group(2)))
        m = HttpRules._REGEX_REMOVE_UNLESS_FOUND.match(rule)
        if m: return HttpRule('remove_unless_found', HttpRules._parse_regex(rule, m.group(1)),
                              HttpRules._parse_regex_find(rule, m.group(2)))
        m = HttpRules._REGEX_REPLACE.match(rule)
        if m: return HttpRule('replace', HttpRules._parse_regex(rule, m.group(1)), HttpRules._parse_regex_find(rule, m.group(2)),
                              HttpRules._parse_string(rule, m.group(3)))
        m = HttpRules._REGEX_SAMPLE.match(rule)
        if m:
            m1 = int(m.group(1))
            if m1 < 1 or m1 > 99: raise SyntaxError('Invalid sample percent: ' + m.group(1))
            return HttpRule('sample', None, m1)
        m = HttpRules._REGEX_SKIP_COMPRESSION.match(rule)
        if m: return HttpRule('skip_compression')
        m = HttpRules._REGEX_SKIP_SUBMISSION.match(rule)
        if m: return HttpRule('skip_submission')
        m = HttpRules._REGEX_STOP.match(rule)
        if m: return HttpRule('stop', HttpRules._parse_regex(rule, m.group(1)))
        m = HttpRules._REGEX_STOP_IF.match(rule)
        if m: return HttpRule('stop_if', HttpRules._parse_regex(rule, m.group(1)), HttpRules._parse_regex(rule, m.group(2)))
        m = HttpRules._REGEX_STOP_IF_FOUND.match(rule)
        if m: return HttpRule('stop_if_found', HttpRules._parse_regex(rule, m.group(1)),
                              HttpRules._parse_regex_find(rule, m.group(2)))
        m = HttpRules._REGEX_STOP_UNLESS.match(rule)
        if m: return HttpRule('stop_unless', HttpRules._parse_regex(rule, m.group(1)), HttpRules._parse_regex(rule, m.group(2)))
        m = HttpRules._REGEX_STOP_UNLESS_FOUND.match(rule)
        if m: return HttpRule('stop_unless_found', HttpRules._parse_regex(rule, m.group(1)),
                              HttpRules._parse_regex_find(rule, m.group(2)))
        raise SyntaxError('Invalid rule: ' + rule)

    @classmethod
    def _parse_regex(cls, rule: str, regex: str) -> Pattern:
        """Parses regex for matching."""
        s: str = HttpRules._parse_string(rule, regex)
        if not s.startswith('^'): s = '^' + s
        if not s.endswith('$'): s = s + '$'
        try:
            return re.compile(s)
        except:
            raise SyntaxError(f'Invalid regex ({regex}) in rule: {rule}')

    @classmethod
    def _parse_regex_find(cls, rule: str, regex: str) -> Pattern:
        """Parses regex for finding."""
        try:
            return re.compile(HttpRules._parse_string(rule, regex)) # todo need flags here?
        except:
            raise SyntaxError(f'Invalid regex ({regex}) in rule: {rule}')

    @classmethod
    def _parse_string(cls, rule: str, expr: str) -> str:
        """Parses delimited string expression."""
        for sep in ['~', '!', '%', '|', '/']:
            p: Pattern = re.compile(r'^[{s}](.*)[{s}]$'.format(s=sep))
            m = p.match(expr)
            if m:
                m1: str = m.group(1)
                m1p: Pattern = re.compile(r'^[{s}].*|.*[^\\\\][{s}].*'.format(s=sep))
                if m1p.match(m1): raise SyntaxError(f'Unescaped separator ({sep}) in rule: {rule}')
                return sep.join(m1.split('\\' + sep))
        raise SyntaxError(f'Invalid expression ({expr}) in rule: {rule}')

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
