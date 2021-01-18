# coding: utf-8
# © 2016-2021 Resurface Labs Inc.

import random
import re
from pathlib import Path
from typing import List, Optional, Pattern, Sized

from usagelogger.http_rule import HttpRule


class HttpRules(Sized):
    __DEBUG_RULES: str = (r"allow_http_url" "\n"
                          r"copy_session_field /.*/" "\n")

    __STANDARD_RULES: str = ("/request_header:cookie|response_header:set-cookie/ remove\n"
                             r'/(request|response)_body|request_param/ replace '
                             r'/[a-zA-Z0-9.!#$%&’*+\/=?^_`{|}~-]+@[a-zA-Z0-9-]+'
                             r'(?:\.[a-zA-Z0-9-]+)/, /x@y.com/' "\n"
                             r'/request_body|request_param|response_body/ replace '
                             r'/[0-9\.\-\/]{9,}/, /xyxy/' "\n")

    __STRICT_RULES: str = (r'/request_url/ replace /([^\?;]+).*/, !\\1!' "\n"
                           r'/request_body|response_body|request_param:.*|'
                           r'request_header:(?!user-agent).*|response_header:'
                           r'(?!(content-length)|(content-type)).*/ remove' "\n")

    __default_rules: str = __STRICT_RULES

    @classmethod
    def default_rules(cls) -> str:
        return cls.__default_rules

    @classmethod
    def set_default_rules(cls, rules: str) -> None:
        cls.__default_rules: str = re.sub(r'^\s*include default\s*$', '', rules, flags=re.MULTILINE)

    @classmethod
    def debug_rules(cls) -> str:
        return cls.__DEBUG_RULES

    @classmethod
    def standard_rules(cls) -> str:
        return cls.__STANDARD_RULES

    @classmethod
    def strict_rules(cls) -> str:
        return cls.__STRICT_RULES

    @classmethod
    def parse_rule(cls, rule: str) -> Optional[HttpRule]:
        """Parses rule from single line."""
        if rule is None or HttpRules.__REGEX_BLANK_OR_COMMENT.match(rule): return None
        m = HttpRules.__REGEX_ALLOW_HTTP_URL.match(rule)
        if m: return HttpRule('allow_http_url')
        m = HttpRules.__REGEX_COPY_SESSION_FIELD.match(rule)
        if m: return HttpRule('copy_session_field', None, HttpRules.parse_regex(rule, m.group(1)))
        m = HttpRules.__REGEX_REMOVE.match(rule)
        if m: return HttpRule('remove', HttpRules.parse_regex(rule, m.group(1)))
        m = HttpRules.__REGEX_REMOVE_IF.match(rule)
        if m: return HttpRule('remove_if', HttpRules.parse_regex(rule, m.group(1)), HttpRules.parse_regex(rule, m.group(2)))
        m = HttpRules.__REGEX_REMOVE_IF_FOUND.match(rule)
        if m: return HttpRule('remove_if_found', HttpRules.parse_regex(rule, m.group(1)),
                              HttpRules.parse_regex_find(rule, m.group(2)))
        m = HttpRules.__REGEX_REMOVE_UNLESS.match(rule)
        if m: return HttpRule('remove_unless', HttpRules.parse_regex(rule, m.group(1)), HttpRules.parse_regex(rule, m.group(2)))
        m = HttpRules.__REGEX_REMOVE_UNLESS_FOUND.match(rule)
        if m: return HttpRule('remove_unless_found', HttpRules.parse_regex(rule, m.group(1)),
                              HttpRules.parse_regex_find(rule, m.group(2)))
        m = HttpRules.__REGEX_REPLACE.match(rule)
        if m: return HttpRule('replace', HttpRules.parse_regex(rule, m.group(1)), HttpRules.parse_regex_find(rule, m.group(2)),
                              HttpRules.parse_string(rule, m.group(3)))
        m = HttpRules.__REGEX_SAMPLE.match(rule)
        if m:
            m1 = int(m.group(1))
            if m1 < 1 or m1 > 99: raise SyntaxError('Invalid sample percent: ' + m.group(1))
            return HttpRule('sample', None, m1)
        m = HttpRules.__REGEX_SKIP_COMPRESSION.match(rule)
        if m: return HttpRule('skip_compression')
        m = HttpRules.__REGEX_SKIP_SUBMISSION.match(rule)
        if m: return HttpRule('skip_submission')
        m = HttpRules.__REGEX_STOP.match(rule)
        if m: return HttpRule('stop', HttpRules.parse_regex(rule, m.group(1)))
        m = HttpRules.__REGEX_STOP_IF.match(rule)
        if m: return HttpRule('stop_if', HttpRules.parse_regex(rule, m.group(1)), HttpRules.parse_regex(rule, m.group(2)))
        m = HttpRules.__REGEX_STOP_IF_FOUND.match(rule)
        if m: return HttpRule('stop_if_found', HttpRules.parse_regex(rule, m.group(1)),
                              HttpRules.parse_regex_find(rule, m.group(2)))
        m = HttpRules.__REGEX_STOP_UNLESS.match(rule)
        if m: return HttpRule('stop_unless', HttpRules.parse_regex(rule, m.group(1)), HttpRules.parse_regex(rule, m.group(2)))
        m = HttpRules.__REGEX_STOP_UNLESS_FOUND.match(rule)
        if m: return HttpRule('stop_unless_found', HttpRules.parse_regex(rule, m.group(1)),
                              HttpRules.parse_regex_find(rule, m.group(2)))
        raise SyntaxError('Invalid rule: ' + rule)

    @classmethod
    def parse_regex(cls, rule: str, regex: str) -> Pattern:
        """Parses regex for matching."""
        s: str = HttpRules.parse_string(rule, regex)
        if not s.startswith('^'): s = '^' + s
        if not s.endswith('$'): s = s + '$'
        try:
            return re.compile(s)
        except:
            raise SyntaxError(f'Invalid regex ({regex}) in rule: {rule}')

    @classmethod
    def parse_regex_find(cls, rule: str, regex: str) -> Pattern:
        """Parses regex for finding."""
        try:
            return re.compile(HttpRules.parse_string(rule, regex))
        except:
            raise SyntaxError(f'Invalid regex ({regex}) in rule: {rule}')

    @classmethod
    def parse_string(cls, rule: str, expr: str) -> str:
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

    def __init__(self, rules: str) -> None:
        if rules is None: rules = HttpRules.default_rules()

        # load rules from external files
        if rules.startswith('file://'):
            rfile = rules[7:]
            try:
                rules = Path(rfile).read_text()
            except:
                raise FileNotFoundError(f'Failed to load rules: {rfile}')

        # force default rules if necessary
        rules = re.sub(r'^\s*include default\s*$', str(HttpRules.default_rules()), rules, flags=re.MULTILINE)
        if len(rules.strip()) == 0: rules = HttpRules.default_rules()

        # expand rule includes
        rules = re.sub(r'(?m)^\s*include debug\s*$', HttpRules.debug_rules(), rules)
        rules = re.sub(r'(?m)^\s*include standard\s*$', HttpRules.standard_rules(), rules)
        rules = re.sub(r'(?m)^\s*include strict\s*$', HttpRules.strict_rules(), rules)
        self._text = rules

        # parse all rules
        prs: List = []
        for rule in rules.split("\n"):
            parsed: HttpRule = HttpRules.parse_rule(rule)
            if parsed is not None: prs.append(parsed)
        self._length = len(prs)

        # break out rules by verb
        self._allow_http_url: bool = len([r for r in prs if 'allow_http_url' == r.verb]) > 0
        self._copy_session_field: List[HttpRule] = [r for r in prs if 'copy_session_field' == r.verb]
        self._remove: List[HttpRule] = [r for r in prs if 'remove' == r.verb]
        self._remove_if: List[HttpRule] = [r for r in prs if 'remove_if' == r.verb]
        self._remove_if_found: List[HttpRule] = [r for r in prs if 'remove_if_found' == r.verb]
        self._remove_unless: List[HttpRule] = [r for r in prs if 'remove_unless' == r.verb]
        self._remove_unless_found: List[HttpRule] = [r for r in prs if 'remove_unless_found' == r.verb]
        self._replace: List[HttpRule] = [r for r in prs if 'replace' == r.verb]
        self._sample: List[HttpRule] = [r for r in prs if 'sample' == r.verb]
        self._skip_compression: bool = len([r for r in prs if r.verb == 'skip_compression']) > 0
        self._skip_submission: bool = len([r for r in prs if r.verb == 'skip_submission']) > 0
        self._stop: List[HttpRule] = [r for r in prs if 'stop' == r.verb]
        self._stop_if: List[HttpRule] = [r for r in prs if 'stop_if' == r.verb]
        self._stop_if_found: List[HttpRule] = [r for r in prs if 'stop_if_found' == r.verb]
        self._stop_unless: List[HttpRule] = [r for r in prs if 'stop_unless' == r.verb]
        self._stop_unless_found: List[HttpRule] = [r for r in prs if 'stop_unless_found' == r.verb]

        # validate rules
        if len(self._sample) > 1: raise SyntaxError('Multiple sample rules')

    def __len__(self) -> int:
        return self._length

    @property
    def allow_http_url(self) -> bool:
        return self._allow_http_url

    @property
    def copy_session_field(self) -> List[HttpRule]:
        return self._copy_session_field

    @property
    def remove(self) -> List[HttpRule]:
        return self._remove

    @property
    def remove_if(self) -> List[HttpRule]:
        return self._remove_if

    @property
    def remove_if_found(self) -> List[HttpRule]:
        return self._remove_if_found

    @property
    def remove_unless(self) -> List[HttpRule]:
        return self._remove_unless

    @property
    def remove_unless_found(self) -> List[HttpRule]:
        return self._remove_unless_found

    @property
    def replace(self) -> List[HttpRule]:
        return self._replace

    @property
    def sample(self) -> List[HttpRule]:
        return self._sample

    @property
    def skip_compression(self) -> bool:
        return self._skip_compression

    @property
    def skip_submission(self) -> bool:
        return self._skip_submission

    @property
    def stop(self) -> List[HttpRule]:
        return self._stop

    @property
    def stop_if(self) -> List[HttpRule]:
        return self._stop_if

    @property
    def stop_if_found(self) -> List[HttpRule]:
        return self._stop_if_found

    @property
    def stop_unless(self) -> List[HttpRule]:
        return self._stop_unless

    @property
    def stop_unless_found(self) -> List[HttpRule]:
        return self._stop_unless_found

    @property
    def text(self) -> str:
        return self._text

    def apply(self, details: List[List[str]]) -> Optional[List[List[str]]]:
        # stop rules come first
        for r in self._stop:
            for d in details:
                if r.scope.match(d[0]): return None
        for r in self._stop_if_found:
            for d in details:
                if r.scope.match(d[0]) and r.param1.search(d[1]): return None
        for r in self._stop_if:
            for d in details:
                if r.scope.match(d[0]) and r.param1.match(d[1]): return None
        passed = 0
        for r in self._stop_unless_found:
            for d in details:
                if r.scope.match(d[0]) and r.param1.search(d[1]): passed += 1
        if passed != len(self._stop_unless_found): return None
        passed = 0
        for r in self._stop_unless:
            for d in details:
                if r.scope.match(d[0]) and r.param1.match(d[1]): passed += 1
        if passed != len(self._stop_unless): return None

        # do sampling if configured
        if len(self._sample) == 1 and random.randrange(100) >= int(self._sample[0].param1): return None

        # winnow sensitive details based on remove rules if configured
        for r in self._remove:
            for d in details:
                if r.scope.match(d[0]): d[1] = ''
        for r in self._remove_unless_found:
            for d in details:
                if r.scope.match(d[0]) and not r.param1.search(d[1]): d[1] = ''
        for r in self._remove_if_found:
            for d in details:
                if r.scope.match(d[0]) and r.param1.search(d[1]): d[1] = ''
        for r in self._remove_unless:
            for d in details:
                if r.scope.match(d[0]) and not r.param1.match(d[1]): d[1] = ''
        for r in self._remove_if:
            for d in details:
                if r.scope.match(d[0]) and r.param1.match(d[1]): d[1] = ''

        # remove any details with empty values
        details = [x for x in details if x[1] != '']
        if len(details) == 0: return None

        # mask sensitive details based on replace rules if configured
        for r in self._replace:
            for d in details:
                if r.scope.match(d[0]): d[1] = re.sub(r.param1, r.param2, d[1])

        # remove any details with empty values
        details = [x for x in details if x[1] != '']
        return None if len(details) == 0 else details

    __REGEX_ALLOW_HTTP_URL: Pattern = re.compile(
        r'^\s*allow_http_url\s*(#.*)?$')
    __REGEX_BLANK_OR_COMMENT: Pattern = re.compile(
        r'^\s*([#].*)*$')
    __REGEX_COPY_SESSION_FIELD: Pattern = re.compile(
        r'^\s*copy_session_field\s+([~!%|/].+[~!%|/])\s*(#.*)?$')
    __REGEX_REMOVE: Pattern = re.compile(
        r'^\s*([~!%|/].+[~!%|/])\s*remove\s*(#.*)?$')
    __REGEX_REMOVE_IF: Pattern = re.compile(
        r'^\s*([~!%|/].+[~!%|/])\s*remove_if\s+([~!%|/].+[~!%|/])\s*(#.*)?$')
    __REGEX_REMOVE_IF_FOUND: Pattern = re.compile(
        r'^\s*([~!%|/].+[~!%|/])\s*'
        r'remove_if_found\s+([~!%|/].+[~!%|/])\s*(#.*)?$')
    __REGEX_REMOVE_UNLESS: Pattern = re.compile(
        r'^\s*([~!%|/].+[~!%|/])\s*'
        r'remove_unless\s+([~!%|/].+[~!%|/])\s*(#.*)?$')
    __REGEX_REMOVE_UNLESS_FOUND: Pattern = re.compile(
        r'^\s*([~!%|/].+[~!%|/])\s*'
        r'remove_unless_found\s+([~!%|/].+[~!%|/])\s*(#.*)?$')
    __REGEX_REPLACE: Pattern = re.compile(
        r'^\s*([~!%|/].+[~!%|/])\s*'
        r'replace[\s]+([~!%|/].+[~!%|/]),[\s]+([~!%|/].*[~!%|/])\s*(#.*)?$')
    __REGEX_SAMPLE: Pattern = re.compile(
        r'^\s*sample\s+(\d+)\s*(#.*)?$')
    __REGEX_SKIP_COMPRESSION: Pattern = re.compile(
        r'^\s*skip_compression\s*(#.*)?$')
    __REGEX_SKIP_SUBMISSION: Pattern = re.compile(
        r'^\s*skip_submission\s*(#.*)?$')
    __REGEX_STOP: Pattern = re.compile(
        r'^\s*([~!%|/].+[~!%|/])\s*stop\s*(#.*)?$')
    __REGEX_STOP_IF: Pattern = re.compile(
        r'^\s*([~!%|/].+[~!%|/])\s*stop_if\s+([~!%|/].+[~!%|/])\s*(#.*)?$')
    __REGEX_STOP_IF_FOUND: Pattern = re.compile(
        r'^\s*([~!%|/].+[~!%|/])\s*'
        r'stop_if_found\s+([~!%|/].+[~!%|/])\s*(#.*)?$')
    __REGEX_STOP_UNLESS: Pattern = re.compile(
        r'^\s*([~!%|/].+[~!%|/])\s*stop_unless\s+([~!%|/].+[~!%|/])\s*(#.*)?$')
    __REGEX_STOP_UNLESS_FOUND: Pattern = re.compile(
        r'^\s*([~!%|/].+[~!%|/])\s*'
        r'stop_unless_found\s+([~!%|/].+[~!%|/])\s*(#.*)?$')
