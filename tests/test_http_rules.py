# coding: utf-8
# © 2016-2021 Resurface Labs Inc.

import re

from usagelogger import HttpRules


def test_changes_default_rules():
    assert HttpRules.default_rules() == HttpRules.strict_rules()
    try:
        HttpRules.set_default_rules("")
        assert HttpRules.default_rules() == ""
        assert len(HttpRules(HttpRules.default_rules())) == 0

        HttpRules.set_default_rules(" include default")
        assert HttpRules.default_rules() == ""

        HttpRules.set_default_rules("include default\n")
        assert HttpRules.default_rules() == ""

        HttpRules.set_default_rules(" include default\ninclude default\n")
        assert len(HttpRules(HttpRules.default_rules())) == 0

        HttpRules.set_default_rules(" include default\ninclude default\nsample 42")
        rules = HttpRules(HttpRules.default_rules())
        assert len(rules) == 1
        assert len(rules.sample) == 1
    finally:
        HttpRules.set_default_rules(HttpRules.strict_rules())


def test_includes_debug_rules():
    rules = HttpRules("include debug")
    assert len(rules) == 2
    assert rules.allow_http_url is True
    assert len(rules.copy_session_field) == 1

    rules = HttpRules("include debug\n")
    assert len(rules) == 2
    rules = HttpRules("include debug\nsample 50")
    assert len(rules) == 3
    assert len(rules.sample) == 1

    rules = HttpRules("include debug\ninclude debug\n")
    assert len(rules) == 4
    rules = HttpRules("include debug\nsample 50\ninclude debug\n")
    assert len(rules) == 5

    assert HttpRules.default_rules() == HttpRules.strict_rules()
    try:
        HttpRules.set_default_rules("include debug")
        rules = HttpRules("")
        assert len(rules) == 2
        assert rules.allow_http_url is True
        assert len(rules.copy_session_field) == 1
    finally:
        HttpRules.set_default_rules(HttpRules.strict_rules())


def test_includes_standard_rules():
    rules = HttpRules("include standard")
    assert len(rules) == 3
    assert len(rules.remove) == 1
    assert len(rules.replace) == 2

    rules = HttpRules("include standard\n")
    assert len(rules) == 3
    rules = HttpRules("include standard\nsample 50")
    assert len(rules) == 4
    assert len(rules.sample) == 1

    rules = HttpRules("include standard\ninclude standard\n")
    assert len(rules) == 6
    rules = HttpRules("include standard\nsample 50\ninclude standard\n")
    assert len(rules) == 7

    assert HttpRules.default_rules() == HttpRules.strict_rules()
    try:
        HttpRules.set_default_rules("include standard")
        rules = HttpRules("")
        assert len(rules) == 3
        assert len(rules.remove) == 1
        assert len(rules.replace) == 2
    finally:
        HttpRules.set_default_rules(HttpRules.strict_rules())


def test_includes_strict_rules():
    rules = HttpRules("include strict")
    assert len(rules) == 2
    assert len(rules.remove) == 1
    assert len(rules.replace) == 1

    rules = HttpRules("include strict\n")
    assert len(rules) == 2
    rules = HttpRules("include strict\nsample 50")
    assert len(rules) == 3
    assert len(rules.sample) == 1

    rules = HttpRules("include strict\ninclude strict\n")
    assert len(rules) == 4
    rules = HttpRules("include strict\nsample 50\ninclude strict\n")
    assert len(rules) == 5

    assert HttpRules.default_rules() == HttpRules.strict_rules()
    try:
        HttpRules.set_default_rules("include strict")
        rules = HttpRules("")
        assert len(rules) == 2
        assert len(rules.remove) == 1
        assert len(rules.replace) == 1
    finally:
        HttpRules.set_default_rules(HttpRules.strict_rules())


def test_load_rules_from_file():
    rules = HttpRules("file://./tests/test_rules1.txt")
    assert len(rules) == 1
    assert len(rules.sample) == 1
    assert rules.sample[0].param1 == 55

    rules = HttpRules("file://./tests/test_rules2.txt")
    assert len(rules) == 3
    assert rules.allow_http_url is True
    assert len(rules.copy_session_field) == 1
    assert len(rules.sample) == 1
    assert rules.sample[0].param1 == 56

    rules = HttpRules("file://./tests/test_rules3.txt")
    assert len(rules.remove) == 1
    assert len(rules.replace) == 1
    assert len(rules.sample) == 1
    assert rules.sample[0].param1 == 57


def parse_fail(line):
    try:
        HttpRules.parse_rule(line)
    except Exception:
        return
    assert False


def parse_ok(line, verb, scope, param1, param2):
    rule = HttpRules.parse_rule(line)
    assert rule.verb == verb

    if rule.scope is None:
        assert scope is None
    else:
        assert rule.scope.pattern == re.compile(scope).pattern

    if param1 is None:
        assert True
    elif hasattr(rule.param1, "match"):
        assert rule.param1.pattern == re.compile(param1).pattern
    else:
        assert rule.param1 == param1

    if param2 is None:
        assert True
    elif hasattr(rule.param2, "match"):
        assert rule.param2.pattern == re.compile(param2).pattern
    else:
        assert rule.param2 == param2


def test_parses_empty_rules():
    assert len(HttpRules(None)) == 2
    assert len(HttpRules("")) == 2
    assert len(HttpRules(" ")) == 2
    assert len(HttpRules("\t")) == 2
    assert len(HttpRules("\n")) == 2

    assert HttpRules.parse_rule(None) is None
    assert HttpRules.parse_rule("") is None
    assert HttpRules.parse_rule(" ") is None
    assert HttpRules.parse_rule("\t") is None
    assert HttpRules.parse_rule("\n") is None


def test_parses_rules_with_bad_verbs():
    for v in ["b", "bozo", "*", ".*"]:
        parse_fail(f"{v}")
        parse_fail(f"!.*! {v}")
        parse_fail(f"/.*/ {v}")
        parse_fail(f"%request_body% {v}")
        parse_fail(f"/^request_header:.*/ {v}")


def test_parses_rules_with_invalid_scopes():
    for s in ["request_body", "*", ".*"]:
        parse_fail(f"/{s}")
        parse_fail(f"/{s}# 1")
        parse_fail(f"/{s} # 1")
        parse_fail(f"/{s}/")
        parse_fail(f"/{s}/ # 1")
        parse_fail(f" / {s}")
        parse_fail(f"// {s}")
        parse_fail(f"/// {s}")
        parse_fail(f"/* {s}")
        parse_fail(f"/? {s}")
        parse_fail(f"/+ {s}")
        parse_fail(f"/( {s}")
        parse_fail(f"/(.* {s}")
        parse_fail(f"/(.*)) {s}")

        parse_fail(f"~{s}")
        parse_fail(f"!{s}# 1")
        parse_fail(f"|{s} # 1")
        parse_fail(f"|{s}|")
        parse_fail(f"%{s}% # 1")
        parse_fail(f" % {s}")
        parse_fail(f"%% {s}")
        parse_fail(f"%%% {s}")
        parse_fail(f"%* {s}")
        parse_fail(f"%? {s}")
        parse_fail(f"%+ {s}")
        parse_fail(f"%( {s}")
        parse_fail(f"%(.* {s}")
        parse_fail(f"%(.*)) {s}")

        parse_fail(f"~{s}%")
        parse_fail(f"!{s}%# 1")
        parse_fail(f"|{s}% # 1")
        parse_fail(f"|{s}%")
        parse_fail(f"%{s}| # 1")
        parse_fail(f"~(.*! {s}")
        parse_fail(f"~(.*))! {s}")
        parse_fail(f"/(.*! {s}")
        parse_fail(f"/(.*))! {s}")


def test_parses_allow_http_url_rules():
    parse_fail("allow_http_url whaa")
    parse_ok("allow_http_url", "allow_http_url", None, None, None)
    parse_ok("allow_http_url # be safe bro!", "allow_http_url", None, None, None)


def test_parses_copy_session_field_rules():
    # with extra params
    parse_fail("|.*| copy_session_field %1%, %2%")
    parse_fail("!.*! copy_session_field /1/, 2")
    parse_fail("/.*/ copy_session_field /1/, /2")
    parse_fail("/.*/ copy_session_field /1/, /2/")
    parse_fail("/.*/ copy_session_field /1/, /2/, /3/ # blah")
    parse_fail("!.*! copy_session_field %1%, %2%, %3%")
    parse_fail("/.*/ copy_session_field /1/, /2/, 3")
    parse_fail("/.*/ copy_session_field /1/, /2/, /3")
    parse_fail("/.*/ copy_session_field /1/, /2/, /3/")
    parse_fail("%.*% copy_session_field /1/, /2/, /3/ # blah")

    # with missing params
    parse_fail("!.*! copy_session_field")
    parse_fail("/.*/ copy_session_field")
    parse_fail("/.*/ copy_session_field /")
    parse_fail("/.*/ copy_session_field //")
    parse_fail("/.*/ copy_session_field blah")
    parse_fail("/.*/ copy_session_field # bleep")
    parse_fail("/.*/ copy_session_field blah # bleep")

    # with invalid params
    parse_fail("/.*/ copy_session_field /")
    parse_fail("/.*/ copy_session_field //")
    parse_fail("/.*/ copy_session_field ///")
    parse_fail("/.*/ copy_session_field /*/")
    parse_fail("/.*/ copy_session_field /?/")
    parse_fail("/.*/ copy_session_field /+/")
    parse_fail("/.*/ copy_session_field /(/")
    parse_fail("/.*/ copy_session_field /(.*/")
    parse_fail("/.*/ copy_session_field /(.*))/")

    # with valid regexes
    parse_ok("copy_session_field !.*!", "copy_session_field", None, "^.*$", None)
    parse_ok("copy_session_field /.*/", "copy_session_field", None, "^.*$", None)
    parse_ok("copy_session_field /^.*/", "copy_session_field", None, "^.*$", None)
    parse_ok("copy_session_field /.*$/", "copy_session_field", None, "^.*$", None)
    parse_ok("copy_session_field /^.*$/", "copy_session_field", None, "^.*$", None)

    # with valid regexes and escape sequences
    parse_ok("copy_session_field !A\\!|B!", "copy_session_field", None, "^A!|B$", None)
    parse_ok("copy_session_field |A\\|B|", "copy_session_field", None, "^A|B$", None)
    parse_ok(
        "copy_session_field |A\\|B\\|C|", "copy_session_field", None, "^A|B|C$", None
    )
    parse_ok(
        "copy_session_field /A\\/B\\/C/", "copy_session_field", None, "^A/B/C$", None
    )


def test_parses_remove_rules():
    # with extra params
    parse_fail("|.*| remove %1%")
    parse_fail("~.*~ remove 1")
    parse_fail("/.*/ remove /1/")
    parse_fail("/.*/ remove 1 # bleep")
    parse_fail("|.*| remove %1%, %2%")
    parse_fail("!.*! remove /1/, 2")
    parse_fail("/.*/ remove /1/, /2")
    parse_fail("/.*/ remove /1/, /2/")
    parse_fail("/.*/ remove /1/, /2/, /3/ # blah")
    parse_fail("!.*! remove %1%, %2%, %3%")
    parse_fail("/.*/ remove /1/, /2/, 3")
    parse_fail("/.*/ remove /1/, /2/, /3")
    parse_fail("/.*/ remove /1/, /2/, /3/")
    parse_fail("%.*% remove /1/, /2/, /3/ # blah")

    # with valid regexes
    parse_ok(
        "%request_header:cookie|response_header:set-cookie% remove",
        "remove",
        "^request_header:cookie|response_header:set-cookie$",
        None,
        None,
    )
    parse_ok(
        "/request_header:cookie|response_header:set-cookie/ remove",
        "remove",
        "^request_header:cookie|response_header:set-cookie$",
        None,
        None,
    )

    # with valid regexes and escape sequences
    parse_ok(
        "!request_header\\!|response_header:set-cookie! remove",
        "remove",
        "^request_header!|response_header:set-cookie$",
        None,
        None,
    )
    parse_ok(
        "|request_header:cookie\\|response_header:set-cookie| remove",
        "remove",
        "^request_header:cookie|response_header:set-cookie$",
        None,
        None,
    )
    parse_ok(
        "|request_header:cookie\\|response_header:set-cookie\\|boo| remove",
        "remove",
        "^request_header:cookie|response_header:set-cookie|boo$",
        None,
        None,
    )
    parse_ok(
        "/request_header:cookie\\/response_header:set-cookie\\/boo/ remove",
        "remove",
        "^request_header:cookie/response_header:set-cookie/boo$",
        None,
        None,
    )


def test_parses_remove_if_rules():
    # with extra params
    parse_fail("|.*| remove_if %1%, %2%")
    parse_fail("!.*! remove_if /1/, 2")
    parse_fail("/.*/ remove_if /1/, /2")
    parse_fail("/.*/ remove_if /1/, /2/")
    parse_fail("/.*/ remove_if /1/, /2/, /3/ # blah")
    parse_fail("!.*! remove_if %1%, %2%, %3%")
    parse_fail("/.*/ remove_if /1/, /2/, 3")
    parse_fail("/.*/ remove_if /1/, /2/, /3")
    parse_fail("/.*/ remove_if /1/, /2/, /3/")
    parse_fail("%.*% remove_if /1/, /2/, /3/ # blah")

    # with missing params
    parse_fail("!.*! remove_if")
    parse_fail("/.*/ remove_if")
    parse_fail("/.*/ remove_if /")
    parse_fail("/.*/ remove_if //")
    parse_fail("/.*/ remove_if blah")
    parse_fail("/.*/ remove_if # bleep")
    parse_fail("/.*/ remove_if blah # bleep")

    # with invalid params
    parse_fail("/.*/ remove_if /")
    parse_fail("/.*/ remove_if //")
    parse_fail("/.*/ remove_if ///")
    parse_fail("/.*/ remove_if /*/")
    parse_fail("/.*/ remove_if /?/")
    parse_fail("/.*/ remove_if /+/")
    parse_fail("/.*/ remove_if /(/")
    parse_fail("/.*/ remove_if /(.*/")
    parse_fail("/.*/ remove_if /(.*))/")

    # with valid regexes
    parse_ok(
        "%response_body% remove_if %<!--SKIP_BODY_LOGGING-->%",
        "remove_if",
        "^response_body$",
        "^<!--SKIP_BODY_LOGGING-->$",
        None,
    )
    parse_ok(
        "/response_body/ remove_if /<!--SKIP_BODY_LOGGING-->/",
        "remove_if",
        "^response_body$",
        "^<!--SKIP_BODY_LOGGING-->$",
        None,
    )

    # with valid regexes and escape sequences
    parse_ok(
        "!request_body|response_body! remove_if |<!--IGNORE_LOGGING-->\\|<!-SKIP-->|",
        "remove_if",
        "^request_body|response_body$",
        "^<!--IGNORE_LOGGING-->|<!-SKIP-->$",
        None,
    )
    parse_ok(
        "|request_body\\|response_body| remove_if |<!--IGNORE_LOGGING-->\\|<!-SKIP-->|",
        "remove_if",
        "^request_body|response_body$",
        "^<!--IGNORE_LOGGING-->|<!-SKIP-->$",
        None,
    )
    parse_ok(
        "|request_body\\|response_body\\|boo| remove_if |<!--IGNORE_LOGGING-->\\|<!-SKIP-->\\|asdf|",
        "remove_if",
        "^request_body|response_body|boo$",
        "^<!--IGNORE_LOGGING-->|<!-SKIP-->|asdf$",
        None,
    )
    parse_ok(
        "/request_body\\/response_body\\/boo/ remove_if |<!--IGNORE_LOGGING-->\\|<!-SKIP-->\\|asdf|",
        "remove_if",
        "^request_body/response_body/boo$",
        "^<!--IGNORE_LOGGING-->|<!-SKIP-->|asdf$",
        None,
    )


def test_parses_remove_if_found_rules():
    # with extra params
    parse_fail("|.*| remove_if_found %1%, %2%")
    parse_fail("!.*! remove_if_found /1/, 2")
    parse_fail("/.*/ remove_if_found /1/, /2")
    parse_fail("/.*/ remove_if_found /1/, /2/")
    parse_fail("/.*/ remove_if_found /1/, /2/, /3/ # blah")
    parse_fail("!.*! remove_if_found %1%, %2%, %3%")
    parse_fail("/.*/ remove_if_found /1/, /2/, 3")
    parse_fail("/.*/ remove_if_found /1/, /2/, /3")
    parse_fail("/.*/ remove_if_found /1/, /2/, /3/")
    parse_fail("%.*% remove_if_found /1/, /2/, /3/ # blah")

    # with missing params
    parse_fail("!.*! remove_if_found")
    parse_fail("/.*/ remove_if_found")
    parse_fail("/.*/ remove_if_found /")
    parse_fail("/.*/ remove_if_found //")
    parse_fail("/.*/ remove_if_found blah")
    parse_fail("/.*/ remove_if_found # bleep")
    parse_fail("/.*/ remove_if_found blah # bleep")

    # with invalid params
    parse_fail("/.*/ remove_if_found /")
    parse_fail("/.*/ remove_if_found //")
    parse_fail("/.*/ remove_if_found ///")
    parse_fail("/.*/ remove_if_found /*/")
    parse_fail("/.*/ remove_if_found /?/")
    parse_fail("/.*/ remove_if_found /+/")
    parse_fail("/.*/ remove_if_found /(/")
    parse_fail("/.*/ remove_if_found /(.*/")
    parse_fail("/.*/ remove_if_found /(.*))/")

    # with valid regexes
    parse_ok(
        "%response_body% remove_if_found %<!--SKIP_BODY_LOGGING-->%",
        "remove_if_found",
        "^response_body$",
        "<!--SKIP_BODY_LOGGING-->",
        None,
    )
    parse_ok(
        "/response_body/ remove_if_found /<!--SKIP_BODY_LOGGING-->/",
        "remove_if_found",
        "^response_body$",
        "<!--SKIP_BODY_LOGGING-->",
        None,
    )

    # with valid regexes and escape sequences
    parse_ok(
        "!request_body|response_body! remove_if_found |<!--IGNORE_LOGGING-->\\|<!-SKIP-->|",
        "remove_if_found",
        "^request_body|response_body$",
        "<!--IGNORE_LOGGING-->|<!-SKIP-->",
        None,
    )
    parse_ok(
        "|request_body\\|response_body| remove_if_found |<!--IGNORE_LOGGING-->\\|<!-SKIP-->|",
        "remove_if_found",
        "^request_body|response_body$",
        "<!--IGNORE_LOGGING-->|<!-SKIP-->",
        None,
    )
    parse_ok(
        "|request_body\\|response_body\\|boo| remove_if_found |<!--IGNORE_LOGGING-->\\|<!-SKIP-->\\|asdf|",
        "remove_if_found",
        "^request_body|response_body|boo$",
        "<!--IGNORE_LOGGING-->|<!-SKIP-->|asdf",
        None,
    )
    parse_ok(
        "/request_body\\/response_body\\/boo/ remove_if_found |<!--IGNORE_LOGGING-->\\|<!-SKIP-->\\|asdf|",
        "remove_if_found",
        "^request_body/response_body/boo$",
        "<!--IGNORE_LOGGING-->|<!-SKIP-->|asdf",
        None,
    )


def test_parses_remove_unless_rules():
    # with extra params
    parse_fail("|.*| remove_unless %1%, %2%")
    parse_fail("!.*! remove_unless /1/, 2")
    parse_fail("/.*/ remove_unless /1/, /2")
    parse_fail("/.*/ remove_unless /1/, /2/")
    parse_fail("/.*/ remove_unless /1/, /2/, /3/ # blah")
    parse_fail("!.*! remove_unless %1%, %2%, %3%")
    parse_fail("/.*/ remove_unless /1/, /2/, 3")
    parse_fail("/.*/ remove_unless /1/, /2/, /3")
    parse_fail("/.*/ remove_unless /1/, /2/, /3/")
    parse_fail("%.*% remove_unless /1/, /2/, /3/ # blah")

    # with missing params
    parse_fail("!.*! remove_unless")
    parse_fail("/.*/ remove_unless")
    parse_fail("/.*/ remove_unless /")
    parse_fail("/.*/ remove_unless //")
    parse_fail("/.*/ remove_unless blah")
    parse_fail("/.*/ remove_unless # bleep")
    parse_fail("/.*/ remove_unless blah # bleep")

    # with invalid params
    parse_fail("/.*/ remove_unless /")
    parse_fail("/.*/ remove_unless //")
    parse_fail("/.*/ remove_unless ///")
    parse_fail("/.*/ remove_unless /*/")
    parse_fail("/.*/ remove_unless /?/")
    parse_fail("/.*/ remove_unless /+/")
    parse_fail("/.*/ remove_unless /(/")
    parse_fail("/.*/ remove_unless /(.*/")
    parse_fail("/.*/ remove_unless /(.*))/")

    # with valid regexes
    parse_ok(
        "%response_body% remove_unless %<!--PERFORM_BODY_LOGGING-->%",
        "remove_unless",
        "^response_body$",
        "^<!--PERFORM_BODY_LOGGING-->$",
        None,
    )
    parse_ok(
        "/response_body/ remove_unless /<!--PERFORM_BODY_LOGGING-->/",
        "remove_unless",
        "^response_body$",
        "^<!--PERFORM_BODY_LOGGING-->$",
        None,
    )

    # with valid regexes and escape sequences
    parse_ok(
        "!request_body|response_body! remove_unless |<!--PERFORM_LOGGING-->\\|<!-SKIP-->|",
        "remove_unless",
        "^request_body|response_body$",
        "^<!--PERFORM_LOGGING-->|<!-SKIP-->$",
        None,
    )
    parse_ok(
        "|request_body\\|response_body| remove_unless |<!--PERFORM_LOGGING-->\\|<!-SKIP-->|",
        "remove_unless",
        "^request_body|response_body$",
        "^<!--PERFORM_LOGGING-->|<!-SKIP-->$",
        None,
    )
    parse_ok(
        "|request_body\\|response_body\\|boo| remove_unless |<!--PERFORM_LOGGING-->\\|<!-SKIP-->\\|skipit|",
        "remove_unless",
        "^request_body|response_body|boo$",
        "^<!--PERFORM_LOGGING-->|<!-SKIP-->|skipit$",
        None,
    )
    parse_ok(
        "/request_body\\/response_body\\/boo/ remove_unless |<!--PERFORM_LOGGING-->\\|<!-SKIP-->\\|skipit|",
        "remove_unless",
        "^request_body/response_body/boo$",
        "^<!--PERFORM_LOGGING-->|<!-SKIP-->|skipit$",
        None,
    )


def test_parses_remove_unless_found_rules():
    # with extra params
    parse_fail("|.*| remove_unless_found %1%, %2%")
    parse_fail("!.*! remove_unless_found /1/, 2")
    parse_fail("/.*/ remove_unless_found /1/, /2")
    parse_fail("/.*/ remove_unless_found /1/, /2/")
    parse_fail("/.*/ remove_unless_found /1/, /2/, /3/ # blah")
    parse_fail("!.*! remove_unless_found %1%, %2%, %3%")
    parse_fail("/.*/ remove_unless_found /1/, /2/, 3")
    parse_fail("/.*/ remove_unless_found /1/, /2/, /3")
    parse_fail("/.*/ remove_unless_found /1/, /2/, /3/")
    parse_fail("%.*% remove_unless_found /1/, /2/, /3/ # blah")

    # with missing params
    parse_fail("!.*! remove_unless_found")
    parse_fail("/.*/ remove_unless_found")
    parse_fail("/.*/ remove_unless_found /")
    parse_fail("/.*/ remove_unless_found //")
    parse_fail("/.*/ remove_unless_found blah")
    parse_fail("/.*/ remove_unless_found # bleep")
    parse_fail("/.*/ remove_unless_found blah # bleep")

    # with invalid params
    parse_fail("/.*/ remove_unless_found /")
    parse_fail("/.*/ remove_unless_found //")
    parse_fail("/.*/ remove_unless_found ///")
    parse_fail("/.*/ remove_unless_found /*/")
    parse_fail("/.*/ remove_unless_found /?/")
    parse_fail("/.*/ remove_unless_found /+/")
    parse_fail("/.*/ remove_unless_found /(/")
    parse_fail("/.*/ remove_unless_found /(.*/")
    parse_fail("/.*/ remove_unless_found /(.*))/")

    # with valid regexes
    parse_ok(
        "%response_body% remove_unless_found %<!--PERFORM_BODY_LOGGING-->%",
        "remove_unless_found",
        "^response_body$",
        "<!--PERFORM_BODY_LOGGING-->",
        None,
    )
    parse_ok(
        "/response_body/ remove_unless_found /<!--PERFORM_BODY_LOGGING-->/",
        "remove_unless_found",
        "^response_body$",
        "<!--PERFORM_BODY_LOGGING-->",
        None,
    )

    # with valid regexes and escape sequences
    parse_ok(
        "!request_body|response_body! remove_unless_found |<!--PERFORM_LOGGING-->\\|<!-SKIP-->|",
        "remove_unless_found",
        "^request_body|response_body$",
        "<!--PERFORM_LOGGING-->|<!-SKIP-->",
        None,
    )
    parse_ok(
        "|request_body\\|response_body| remove_unless_found |<!--PERFORM_LOGGING-->\\|<!-SKIP-->|",
        "remove_unless_found",
        "^request_body|response_body$",
        "<!--PERFORM_LOGGING-->|<!-SKIP-->",
        None,
    )
    parse_ok(
        "|request_body\\|response_body\\|boo| remove_unless_found |<!--PERFORM_LOGGING-->\\|<!-SKIP-->\\|skipit|",
        "remove_unless_found",
        "^request_body|response_body|boo$",
        "<!--PERFORM_LOGGING-->|<!-SKIP-->|skipit",
        None,
    )
    parse_ok(
        "/request_body\\/response_body\\/boo/ remove_unless_found |<!--PERFORM_LOGGING-->\\|<!-SKIP-->\\|skipit|",
        "remove_unless_found",
        "^request_body/response_body/boo$",
        "<!--PERFORM_LOGGING-->|<!-SKIP-->|skipit",
        None,
    )


def test_parses_replace_rules():
    # with extra params
    parse_fail("!.*! replace %1%, %2%, %3%")
    parse_fail("/.*/ replace /1/, /2/, 3")
    parse_fail("/.*/ replace /1/, /2/, /3")
    parse_fail("/.*/ replace /1/, /2/, /3/")
    parse_fail("%.*% replace /1/, /2/, /3/ # blah")

    # with missing params
    parse_fail("!.*! replace")
    parse_fail("/.*/ replace")
    parse_fail("/.*/ replace /")
    parse_fail("/.*/ replace //")
    parse_fail("/.*/ replace blah")
    parse_fail("/.*/ replace # bleep")
    parse_fail("/.*/ replace blah # bleep")
    parse_fail("!.*! replace boo yah")
    parse_fail("/.*/ replace boo yah")
    parse_fail("/.*/ replace boo yah # bro")
    parse_fail("/.*/ replace /.*/ # bleep")
    parse_fail("/.*/ replace /.*/, # bleep")
    parse_fail("/.*/ replace /.*/, /# bleep")
    parse_fail("/.*/ replace // # bleep")
    parse_fail("/.*/ replace // // # bleep")

    # with invalid params
    parse_fail("/.*/ replace /")
    parse_fail("/.*/ replace //")
    parse_fail("/.*/ replace ///")
    parse_fail("/.*/ replace /*/")
    parse_fail("/.*/ replace /?/")
    parse_fail("/.*/ replace /+/")
    parse_fail("/.*/ replace /(/")
    parse_fail("/.*/ replace /(.*/")
    parse_fail("/.*/ replace /(.*))/")
    parse_fail("/.*/ replace /1/, ~")
    parse_fail("/.*/ replace /1/, !")
    parse_fail("/.*/ replace /1/, %")
    parse_fail("/.*/ replace /1/, |")
    parse_fail("/.*/ replace /1/, /")

    # with valid regexes
    parse_ok(
        "%response_body% replace %kurt%, %vagner%",
        "replace",
        "^response_body$",
        "kurt",
        "vagner",
    )
    parse_ok(
        "/response_body/ replace /kurt/, /vagner/",
        "replace",
        "^response_body$",
        "kurt",
        "vagner",
    )
    parse_ok(
        "%response_body|.+_header:.+% replace %kurt%, %vagner%",
        "replace",
        "^response_body|.+_header:.+$",
        "kurt",
        "vagner",
    )
    parse_ok(
        "|response_body\\|.+_header:.+| replace |kurt|, |vagner\\|frazier|",
        "replace",
        "^response_body|.+_header:.+$",
        "kurt",
        "vagner|frazier",
    )

    # with valid regexes and escape sequences
    parse_ok(
        "|response_body\\|.+_header:.+| replace |kurt|, |vagner|",
        "replace",
        "^response_body|.+_header:.+$",
        "kurt",
        "vagner",
    )
    parse_ok(
        "|response_body\\|.+_header:.+\\|boo| replace |kurt|, |vagner|",
        "replace",
        "^response_body|.+_header:.+|boo$",
        "kurt",
        "vagner",
    )
    parse_ok(
        "|response_body| replace |kurt\\|bruce|, |vagner|",
        "replace",
        "^response_body$",
        "kurt|bruce",
        "vagner",
    )
    parse_ok(
        "|response_body| replace |kurt\\|bruce\\|kevin|, |vagner|",
        "replace",
        "^response_body$",
        "kurt|bruce|kevin",
        "vagner",
    )
    parse_ok(
        "|response_body| replace /kurt\\/bruce\\/kevin/, |vagner|",
        "replace",
        "^response_body$",
        "kurt/bruce/kevin",
        "vagner",
    )


def test_parses_sample_rules():
    parse_fail("sample")
    parse_fail("sample 50 50")
    parse_fail("sample 0")
    parse_fail("sample 100")
    parse_fail("sample 105")
    parse_fail("sample 10.5")
    parse_fail("sample blue")
    parse_fail("sample # bleep")
    parse_fail("sample blue # bleep")
    parse_fail("sample //")
    parse_fail("sample /42/")
    parse_ok("sample 50", "sample", None, 50, None)
    parse_ok("sample 72 # comment", "sample", None, 72, None)


def test_parses_skip_compression_rules():
    parse_fail("skip_compression whaa")
    parse_ok("skip_compression", "skip_compression", None, None, None)
    parse_ok(
        "skip_compression # slightly faster!", "skip_compression", None, None, None
    )


def test_parses_skip_submission_rules():
    parse_fail("skip_submission whaa")
    parse_ok("skip_submission", "skip_submission", None, None, None)
    parse_ok("skip_submission # slightly faster!", "skip_submission", None, None, None)


def test_parses_stop_rules():
    # with extra params
    parse_fail("|.*| stop %1%")
    parse_fail("~.*~ stop 1")
    parse_fail("/.*/ stop /1/")
    parse_fail("/.*/ stop 1 # bleep")
    parse_fail("|.*| stop %1%, %2%")
    parse_fail("!.*! stop /1/, 2")
    parse_fail("/.*/ stop /1/, /2")
    parse_fail("/.*/ stop /1/, /2/")
    parse_fail("/.*/ stop /1/, /2/, /3/ # blah")
    parse_fail("!.*! stop %1%, %2%, %3%")
    parse_fail("/.*/ stop /1/, /2/, 3")
    parse_fail("/.*/ stop /1/, /2/, /3")
    parse_fail("/.*/ stop /1/, /2/, /3/")
    parse_fail("%.*% stop /1/, /2/, /3/ # blah")

    # with valid regexes
    parse_ok(
        "%request_header:skip_usage_logging% stop",
        "stop",
        "^request_header:skip_usage_logging$",
        None,
        None,
    )
    parse_ok(
        "|request_header:skip_usage_logging| stop",
        "stop",
        "^request_header:skip_usage_logging$",
        None,
        None,
    )
    parse_ok(
        "/request_header:skip_usage_logging/ stop",
        "stop",
        "^request_header:skip_usage_logging$",
        None,
        None,
    )

    # with valid regexes and escape sequences
    parse_ok("!request_header\\!! stop", "stop", "^request_header!$", None, None)
    parse_ok(
        "|request_header\\|response_header| stop",
        "stop",
        "^request_header|response_header$",
        None,
        None,
    )
    parse_ok(
        "|request_header\\|response_header\\|boo| stop",
        "stop",
        "^request_header|response_header|boo$",
        None,
        None,
    )
    parse_ok(
        "/request_header\\/response_header\\/boo/ stop",
        "stop",
        "^request_header/response_header/boo$",
        None,
        None,
    )


def test_parses_stop_if_rules():
    # with extra params
    parse_fail("|.*| stop_if %1%, %2%")
    parse_fail("!.*! stop_if /1/, 2")
    parse_fail("/.*/ stop_if /1/, /2")
    parse_fail("/.*/ stop_if /1/, /2/")
    parse_fail("/.*/ stop_if /1/, /2/, /3/ # blah")
    parse_fail("!.*! stop_if %1%, %2%, %3%")
    parse_fail("/.*/ stop_if /1/, /2/, 3")
    parse_fail("/.*/ stop_if /1/, /2/, /3")
    parse_fail("/.*/ stop_if /1/, /2/, /3/")
    parse_fail("%.*% stop_if /1/, /2/, /3/ # blah")

    # with missing params
    parse_fail("!.*! stop_if")
    parse_fail("/.*/ stop_if")
    parse_fail("/.*/ stop_if /")
    parse_fail("/.*/ stop_if //")
    parse_fail("/.*/ stop_if blah")
    parse_fail("/.*/ stop_if # bleep")
    parse_fail("/.*/ stop_if blah # bleep")

    # with invalid params
    parse_fail("/.*/ stop_if /")
    parse_fail("/.*/ stop_if //")
    parse_fail("/.*/ stop_if ///")
    parse_fail("/.*/ stop_if /*/")
    parse_fail("/.*/ stop_if /?/")
    parse_fail("/.*/ stop_if /+/")
    parse_fail("/.*/ stop_if /(/")
    parse_fail("/.*/ stop_if /(.*/")
    parse_fail("/.*/ stop_if /(.*))/")

    # with valid regexes
    parse_ok(
        "%response_body% stop_if %<!--IGNORE_LOGGING-->%",
        "stop_if",
        "^response_body$",
        "^<!--IGNORE_LOGGING-->$",
        None,
    )
    parse_ok(
        "/response_body/ stop_if /<!--IGNORE_LOGGING-->/",
        "stop_if",
        "^response_body$",
        "^<!--IGNORE_LOGGING-->$",
        None,
    )

    # with valid regexes and escape sequences
    parse_ok(
        "!request_body|response_body! stop_if |<!--IGNORE_LOGGING-->\\|<!-SKIP-->|",
        "stop_if",
        "^request_body|response_body$",
        "^<!--IGNORE_LOGGING-->|<!-SKIP-->$",
        None,
    )
    parse_ok(
        "!request_body|response_body|boo\\!! stop_if |<!--IGNORE_LOGGING-->\\|<!-SKIP-->|",
        "stop_if",
        "^request_body|response_body|boo!$",
        "^<!--IGNORE_LOGGING-->|<!-SKIP-->$",
        None,
    )
    parse_ok(
        "|request_body\\|response_body| stop_if |<!--IGNORE_LOGGING-->\\|<!-SKIP-->|",
        "stop_if",
        "^request_body|response_body$",
        "^<!--IGNORE_LOGGING-->|<!-SKIP-->$",
        None,
    )
    parse_ok(
        "/request_body\\/response_body/ stop_if |<!--IGNORE_LOGGING-->\\|<!-SKIP-->\\|pipe\\||",
        "stop_if",
        "^request_body/response_body$",
        "^<!--IGNORE_LOGGING-->|<!-SKIP-->|pipe|$",
        None,
    )


def test_parses_stop_if_found_rules():
    # with extra params
    parse_fail("|.*| stop_if_found %1%, %2%")
    parse_fail("!.*! stop_if_found /1/, 2")
    parse_fail("/.*/ stop_if_found /1/, /2")
    parse_fail("/.*/ stop_if_found /1/, /2/")
    parse_fail("/.*/ stop_if_found /1/, /2/, /3/ # blah")
    parse_fail("!.*! stop_if_found %1%, %2%, %3%")
    parse_fail("/.*/ stop_if_found /1/, /2/, 3")
    parse_fail("/.*/ stop_if_found /1/, /2/, /3")
    parse_fail("/.*/ stop_if_found /1/, /2/, /3/")
    parse_fail("%.*% stop_if_found /1/, /2/, /3/ # blah")

    # with missing params
    parse_fail("!.*! stop_if_found")
    parse_fail("/.*/ stop_if_found")
    parse_fail("/.*/ stop_if_found /")
    parse_fail("/.*/ stop_if_found //")
    parse_fail("/.*/ stop_if_found blah")
    parse_fail("/.*/ stop_if_found # bleep")
    parse_fail("/.*/ stop_if_found blah # bleep")

    # with invalid params
    parse_fail("/.*/ stop_if_found /")
    parse_fail("/.*/ stop_if_found //")
    parse_fail("/.*/ stop_if_found ///")
    parse_fail("/.*/ stop_if_found /*/")
    parse_fail("/.*/ stop_if_found /?/")
    parse_fail("/.*/ stop_if_found /+/")
    parse_fail("/.*/ stop_if_found /(/")
    parse_fail("/.*/ stop_if_found /(.*/")
    parse_fail("/.*/ stop_if_found /(.*))/")

    # with valid regexes
    parse_ok(
        "%response_body% stop_if_found %<!--IGNORE_LOGGING-->%",
        "stop_if_found",
        "^response_body$",
        "<!--IGNORE_LOGGING-->",
        None,
    )
    parse_ok(
        "/response_body/ stop_if_found /<!--IGNORE_LOGGING-->/",
        "stop_if_found",
        "^response_body$",
        "<!--IGNORE_LOGGING-->",
        None,
    )

    # with valid regexes and escape sequences
    parse_ok(
        "!request_body|response_body! stop_if_found |<!--IGNORE_LOGGING-->\\|<!-SKIP-->|",
        "stop_if_found",
        "^request_body|response_body$",
        "<!--IGNORE_LOGGING-->|<!-SKIP-->",
        None,
    )
    parse_ok(
        "!request_body|response_body|boo\\!! stop_if_found |<!--IGNORE_LOGGING-->\\|<!-SKIP-->|",
        "stop_if_found",
        "^request_body|response_body|boo!$",
        "<!--IGNORE_LOGGING-->|<!-SKIP-->",
        None,
    )
    parse_ok(
        "|request_body\\|response_body| stop_if_found |<!--IGNORE_LOGGING-->\\|<!-SKIP-->|",
        "stop_if_found",
        "^request_body|response_body$",
        "<!--IGNORE_LOGGING-->|<!-SKIP-->",
        None,
    )
    parse_ok(
        "/request_body\\/response_body/ stop_if_found |<!--IGNORE_LOGGING-->\\|<!-SKIP-->\\|pipe\\||",
        "stop_if_found",
        "^request_body/response_body$",
        "<!--IGNORE_LOGGING-->|<!-SKIP-->|pipe|",
        None,
    )


def test_parses_stop_unless_rules():
    # with extra params
    parse_fail("|.*| stop_unless %1%, %2%")
    parse_fail("!.*! stop_unless /1/, 2")
    parse_fail("/.*/ stop_unless /1/, /2")
    parse_fail("/.*/ stop_unless /1/, /2/")
    parse_fail("/.*/ stop_unless /1/, /2/, /3/ # blah")
    parse_fail("!.*! stop_unless %1%, %2%, %3%")
    parse_fail("/.*/ stop_unless /1/, /2/, 3")
    parse_fail("/.*/ stop_unless /1/, /2/, /3")
    parse_fail("/.*/ stop_unless /1/, /2/, /3/")
    parse_fail("%.*% stop_unless /1/, /2/, /3/ # blah")

    # with missing params
    parse_fail("!.*! stop_unless")
    parse_fail("/.*/ stop_unless")
    parse_fail("/.*/ stop_unless /")
    parse_fail("/.*/ stop_unless //")
    parse_fail("/.*/ stop_unless blah")
    parse_fail("/.*/ stop_unless # bleep")
    parse_fail("/.*/ stop_unless blah # bleep")

    # with invalid params
    parse_fail("/.*/ stop_unless /")
    parse_fail("/.*/ stop_unless //")
    parse_fail("/.*/ stop_unless ///")
    parse_fail("/.*/ stop_unless /*/")
    parse_fail("/.*/ stop_unless /?/")
    parse_fail("/.*/ stop_unless /+/")
    parse_fail("/.*/ stop_unless /(/")
    parse_fail("/.*/ stop_unless /(.*/")
    parse_fail("/.*/ stop_unless /(.*))/")

    # with valid regexes
    parse_ok(
        "%response_body% stop_unless %<!--DO_LOGGING-->%",
        "stop_unless",
        "^response_body$",
        "^<!--DO_LOGGING-->$",
        None,
    )
    parse_ok(
        "/response_body/ stop_unless /<!--DO_LOGGING-->/",
        "stop_unless",
        "^response_body$",
        "^<!--DO_LOGGING-->$",
        None,
    )

    # with valid regexes and escape sequences
    parse_ok(
        "!request_body|response_body! stop_unless |<!--DO_LOGGING-->\\|<!-NOSKIP-->|",
        "stop_unless",
        "^request_body|response_body$",
        "^<!--DO_LOGGING-->|<!-NOSKIP-->$",
        None,
    )
    parse_ok(
        "!request_body|response_body|boo\\!! stop_unless |<!--DO_LOGGING-->\\|<!-NOSKIP-->|",
        "stop_unless",
        "^request_body|response_body|boo!$",
        "^<!--DO_LOGGING-->|<!-NOSKIP-->$",
        None,
    )
    parse_ok(
        "|request_body\\|response_body| stop_unless |<!--DO_LOGGING-->\\|<!-NOSKIP-->|",
        "stop_unless",
        "^request_body|response_body$",
        "^<!--DO_LOGGING-->|<!-NOSKIP-->$",
        None,
    )
    parse_ok(
        "|request_body\\|response_body| stop_unless |<!--DO_LOGGING-->\\|<!-NOSKIP-->\\|pipe\\||",
        "stop_unless",
        "^request_body|response_body$",
        "^<!--DO_LOGGING-->|<!-NOSKIP-->|pipe|$",
        None,
    )
    parse_ok(
        "/request_body\\/response_body/ stop_unless |<!--DO_LOGGING-->\\|<!-NOSKIP-->\\|pipe\\||",
        "stop_unless",
        "^request_body/response_body$",
        "^<!--DO_LOGGING-->|<!-NOSKIP-->|pipe|$",
        None,
    )


def test_parses_stop_unless_found_rules():
    # with extra params
    parse_fail("|.*| stop_unless_found %1%, %2%")
    parse_fail("!.*! stop_unless_found /1/, 2")
    parse_fail("/.*/ stop_unless_found /1/, /2")
    parse_fail("/.*/ stop_unless_found /1/, /2/")
    parse_fail("/.*/ stop_unless_found /1/, /2/, /3/ # blah")
    parse_fail("!.*! stop_unless_found %1%, %2%, %3%")
    parse_fail("/.*/ stop_unless_found /1/, /2/, 3")
    parse_fail("/.*/ stop_unless_found /1/, /2/, /3")
    parse_fail("/.*/ stop_unless_found /1/, /2/, /3/")
    parse_fail("%.*% stop_unless_found /1/, /2/, /3/ # blah")

    # with missing params
    parse_fail("!.*! stop_unless_found")
    parse_fail("/.*/ stop_unless_found")
    parse_fail("/.*/ stop_unless_found /")
    parse_fail("/.*/ stop_unless_found //")
    parse_fail("/.*/ stop_unless_found blah")
    parse_fail("/.*/ stop_unless_found # bleep")
    parse_fail("/.*/ stop_unless_found blah # bleep")

    # with invalid params
    parse_fail("/.*/ stop_unless_found /")
    parse_fail("/.*/ stop_unless_found //")
    parse_fail("/.*/ stop_unless_found ///")
    parse_fail("/.*/ stop_unless_found /*/")
    parse_fail("/.*/ stop_unless_found /?/")
    parse_fail("/.*/ stop_unless_found /+/")
    parse_fail("/.*/ stop_unless_found /(/")
    parse_fail("/.*/ stop_unless_found /(.*/")
    parse_fail("/.*/ stop_unless_found /(.*))/")

    # with valid regexes
    parse_ok(
        "%response_body% stop_unless_found %<!--DO_LOGGING-->%",
        "stop_unless_found",
        "^response_body$",
        "<!--DO_LOGGING-->",
        None,
    )
    parse_ok(
        "/response_body/ stop_unless_found /<!--DO_LOGGING-->/",
        "stop_unless_found",
        "^response_body$",
        "<!--DO_LOGGING-->",
        None,
    )

    # with valid regexes and escape sequences
    parse_ok(
        "!request_body|response_body! stop_unless_found |<!--DO_LOGGING-->\\|<!-NOSKIP-->|",
        "stop_unless_found",
        "^request_body|response_body$",
        "<!--DO_LOGGING-->|<!-NOSKIP-->",
        None,
    )
    parse_ok(
        "!request_body|response_body|boo\\!! stop_unless_found |<!--DO_LOGGING-->\\|<!-NOSKIP-->|",
        "stop_unless_found",
        "^request_body|response_body|boo!$",
        "<!--DO_LOGGING-->|<!-NOSKIP-->",
        None,
    )
    parse_ok(
        "|request_body\\|response_body| stop_unless_found |<!--DO_LOGGING-->\\|<!-NOSKIP-->|",
        "stop_unless_found",
        "^request_body|response_body$",
        "<!--DO_LOGGING-->|<!-NOSKIP-->",
        None,
    )
    parse_ok(
        "|request_body\\|response_body| stop_unless_found |<!--DO_LOGGING-->\\|<!-NOSKIP-->\\|pipe\\||",
        "stop_unless_found",
        "^request_body|response_body$",
        "<!--DO_LOGGING-->|<!-NOSKIP-->|pipe|",
        None,
    )
    parse_ok(
        "/request_body\\/response_body/ stop_unless_found |<!--DO_LOGGING-->\\|<!-NOSKIP-->\\|pipe\\||",
        "stop_unless_found",
        "^request_body/response_body$",
        "<!--DO_LOGGING-->|<!-NOSKIP-->|pipe|",
        None,
    )


def test_raises_expected_errors():
    try:
        HttpRules("file://~/bleepblorpbleepblorp12345")
        assert False
    except FileNotFoundError as e:
        assert str(e) == "Failed to load rules: ~/bleepblorpbleepblorp12345"

    try:
        HttpRules("/*! stop")
        assert False
    except SyntaxError as e:
        assert str(e) == "Invalid expression (/*!) in rule: /*! stop"

    try:
        HttpRules("/*/ stop")
        assert False
    except SyntaxError as e:
        assert str(e) == "Invalid regex (/*/) in rule: /*/ stop"

    try:
        HttpRules("/boo")
        assert False
    except SyntaxError as e:
        assert str(e) == "Invalid rule: /boo"

    try:
        HttpRules("sample 123")
        assert False
    except SyntaxError as e:
        assert str(e) == "Invalid sample percent: 123"

    try:
        HttpRules("!!! stop")
        assert False
    except SyntaxError as e:
        assert str(e) == "Unescaped separator (!) in rule: !!! stop"
