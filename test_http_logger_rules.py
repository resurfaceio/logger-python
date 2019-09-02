# coding: utf-8
# © 2016-2019 Resurface Labs Inc.

from test_helper import *
from usagelogger import HttpLogger, HttpRules


def test_manages_default_rules():
    assert HttpLogger.default_rules() == HttpRules.strict_rules()
    try:
        HttpLogger.set_default_rules('')
        assert HttpLogger.default_rules() == ''
        assert len(HttpRules.parse(HttpLogger.default_rules())) == 0

        HttpLogger.set_default_rules(' include default')
        assert HttpLogger.default_rules() == ''

        HttpLogger.set_default_rules('include default\n')
        assert HttpLogger.default_rules() == ''

        HttpLogger.set_default_rules(' include default\ninclude default\n')
        assert len(HttpRules.parse(HttpLogger.default_rules())) == 0

        HttpLogger.set_default_rules(' include default\ninclude default\nsample 42')
        rules = HttpRules.parse(HttpLogger.default_rules())
        assert len(rules) == 1
        assert len(list(filter(lambda rule: rule.verb == 'sample', rules))) == 1
    finally:
        HttpLogger.set_default_rules(HttpRules.strict_rules())


def test_overrides_default_rules():
    assert HttpLogger.default_rules() == HttpRules.strict_rules()
    try:
        logger = HttpLogger(url="https://mysite.com")
        assert logger.rules == HttpRules.strict_rules()
        logger = HttpLogger(url="https://mysite.com", rules="# 123")
        assert logger.rules == "# 123"

        HttpLogger.set_default_rules("")
        logger = HttpLogger(url="https://mysite.com")
        assert logger.rules == ""
        logger = HttpLogger(url="https://mysite.com", rules="   ")
        assert logger.rules == ""
        logger = HttpLogger(url="https://mysite.com", rules=" sample 42")
        assert logger.rules == " sample 42"

        HttpLogger.set_default_rules("skip_compression")
        logger = HttpLogger(url="https://mysite.com")
        assert logger.rules == "skip_compression"
        logger = HttpLogger(url="https://mysite.com", rules="include default\nskip_submission\n")
        assert logger.rules == "skip_compression\nskip_submission\n"

        HttpLogger.set_default_rules("sample 42\n")
        logger = HttpLogger(url="https://mysite.com")
        assert logger.rules == "sample 42\n"
        logger = HttpLogger(url="https://mysite.com", rules="   ")
        assert logger.rules == "sample 42\n"
        logger = HttpLogger(url="https://mysite.com", rules="include default\nskip_submission\n")
        assert logger.rules == "sample 42\n\nskip_submission\n"
    finally:
        HttpLogger.set_default_rules(HttpRules.strict_rules())


def test_uses_allow_http_url_rules():
    logger = HttpLogger(url="http://mysite.com")
    assert logger.enableable is False
    logger = HttpLogger(url="http://mysite.com", rules="")
    assert logger.enableable is False
    logger = HttpLogger(url="https://mysite.com")
    assert logger.enableable is True
    logger = HttpLogger(url="http://mysite.com", rules="allow_http_url")
    assert logger.enableable is True
    logger = HttpLogger(url="http://mysite.com", rules="allow_http_url\nallow_http_url")
    assert logger.enableable is True


def test_uses_copy_session_field_rules():
    assert None is None  # todo finish


def test_uses_copy_session_field_and_remove_rules():
    assert None is None  # todo finish


def test_uses_copy_session_field_and_stop_rules():
    assert None is None  # todo finish


def test_uses_remove_rules():
    queue = []
    logger = HttpLogger(queue=queue, rules='!.*! remove')
    logger.log(request=mock_request_with_json2(), response=mock_response_with_html())
    assert len(queue) == 0

    queue = []
    logger = HttpLogger(queue=queue, rules='!request_body! remove')
    logger.log(request=mock_request_with_json2(), response=mock_response_with_html())
    assert len(queue) == 1
    assert "[\"request_body\"," not in queue[0]
    assert "[\"response_body\"," in queue[0]

    queue = []
    logger = HttpLogger(queue=queue, rules='!response_body! remove')
    logger.log(request=mock_request_with_json2(), response=mock_response_with_html())
    assert len(queue) == 1
    assert "[\"request_body\"," in queue[0]
    assert "[\"response_body\"," not in queue[0]

    queue = []
    logger = HttpLogger(queue=queue, rules='!request_body|response_body! remove')
    logger.log(request=mock_request_with_json2(), response=mock_response_with_html())
    assert len(queue) == 1
    assert "[\"request_body\"," not in queue[0]
    assert "[\"response_body\"," not in queue[0]

    queue = []
    logger = HttpLogger(queue=queue, rules='!request_header:.*! remove')
    logger.log(request=mock_request_with_json2(), response=mock_response_with_html())
    assert len(queue) == 1
    assert "[\"request_body\"," in queue[0]
    assert "[\"request_header:" not in queue[0]
    assert "[\"response_body\"," in queue[0]

    queue = []
    logger = HttpLogger(queue=queue, rules="!request_header:abc! remove\n!response_body! remove")
    logger.log(request=mock_request_with_json2(), response=mock_response_with_html())
    assert len(queue) == 1
    assert "[\"request_body\"," in queue[0]
    assert "[\"request_header:" in queue[0]
    assert "[\"request_header:abc" not in queue[0]
    assert "[\"response_body\"," not in queue[0]


def test_uses_remove_if_rules():
    queue = []
    logger = HttpLogger(queue=queue, rules='!response_header:blahblahblah! remove_if !.*!')
    logger.log(request=mock_request_with_json2(), response=mock_response_with_html())
    assert len(queue) == 1

    queue = []
    logger = HttpLogger(queue=queue, rules='!.*! remove_if !.*!')
    logger.log(request=mock_request_with_json2(), response=mock_response_with_html())
    assert len(queue) == 0

    queue = []
    logger = HttpLogger(queue=queue, rules='!request_body! remove_if !.*!')
    logger.log(request=mock_request_with_json2(), response=mock_response_with_html())
    assert len(queue) == 1
    assert "[\"request_body\"," not in queue[0]
    assert "[\"response_body\"," in queue[0]

    queue = []
    logger = HttpLogger(queue=queue, rules='!response_body! remove_if !.*!')
    logger.log(request=mock_request_with_json2(), response=mock_response_with_html())
    assert len(queue) == 1
    assert "[\"request_body\"," in queue[0]
    assert "[\"response_body\"," not in queue[0]

    queue = []
    logger = HttpLogger(queue=queue, rules='!response_body|request_body! remove_if !.*World.*!')
    logger.log(request=mock_request_with_json2(), response=mock_response_with_html())
    assert len(queue) == 1
    assert "[\"request_body\"," in queue[0]
    assert "[\"response_body\"," not in queue[0]

    queue = []
    logger = HttpLogger(queue=queue, rules='!response_body|request_body! remove_if !.*blahblahblah.*!')
    logger.log(request=mock_request_with_json2(), response=mock_response_with_html())
    assert len(queue) == 1
    assert "[\"request_body\"," in queue[0]
    assert "[\"response_body\"," in queue[0]

    queue = []
    logger = HttpLogger(queue=queue, rules="!request_body! remove_if !.*!\n!response_body! remove_if !.*!")
    logger.log(request=mock_request_with_json2(), response=mock_response_with_html())
    assert len(queue) == 1
    assert "[\"request_body\"," not in queue[0]
    assert "[\"response_body\"," not in queue[0]


def test_uses_remove_if_found_rules():
    queue = []
    logger = HttpLogger(queue=queue, rules='!response_header:blahblahblah! remove_if_found !.*!')
    logger.log(request=mock_request_with_json2(), response=mock_response_with_html())
    assert len(queue) == 1

    queue = []
    logger = HttpLogger(queue=queue, rules='!.*! remove_if_found !.*!')
    logger.log(request=mock_request_with_json2(), response=mock_response_with_html())
    assert len(queue) == 0

    queue = []
    logger = HttpLogger(queue=queue, rules='!request_body! remove_if_found !.*!')
    logger.log(request=mock_request_with_json2(), response=mock_response_with_html())
    assert len(queue) == 1
    assert "[\"request_body\"," not in queue[0]
    assert "[\"response_body\"," in queue[0]

    queue = []
    logger = HttpLogger(queue=queue, rules='!response_body! remove_if_found !.*!')
    logger.log(request=mock_request_with_json2(), response=mock_response_with_html())
    assert len(queue) == 1
    assert "[\"request_body\"," in queue[0]
    assert "[\"response_body\"," not in queue[0]

    queue = []
    logger = HttpLogger(queue=queue, rules='!response_body|request_body! remove_if_found !World!')
    logger.log(request=mock_request_with_json2(), response=mock_response_with_html())
    assert len(queue) == 1
    assert "[\"request_body\"," in queue[0]
    assert "[\"response_body\"," not in queue[0]

    queue = []
    logger = HttpLogger(queue=queue, rules='!response_body|request_body! remove_if_found !.*World.*!')
    logger.log(request=mock_request_with_json2(), response=mock_response_with_html())
    assert len(queue) == 1
    assert "[\"request_body\"," in queue[0]
    assert "[\"response_body\"," not in queue[0]

    queue = []
    logger = HttpLogger(queue=queue, rules='!response_body|request_body! remove_if_found !blahblahblah!')
    logger.log(request=mock_request_with_json2(), response=mock_response_with_html())
    assert len(queue) == 1
    assert "[\"request_body\"," in queue[0]
    assert "[\"response_body\"," in queue[0]


def test_uses_remove_unless_rules():
    queue = []
    logger = HttpLogger(queue=queue, rules='!response_header:blahblahblah! remove_unless !.*!')
    logger.log(request=mock_request_with_json2(), response=mock_response_with_html())
    assert len(queue) == 1

    queue = []
    logger = HttpLogger(queue=queue, rules='!.*! remove_unless !.*blahblahblah.*!')
    logger.log(request=mock_request_with_json2(), response=mock_response_with_html())
    assert len(queue) == 0

    queue = []
    logger = HttpLogger(queue=queue, rules='!request_body! remove_unless !.*blahblahblah.*!')
    logger.log(request=mock_request_with_json2(), response=mock_response_with_html())
    assert len(queue) == 1
    assert "[\"request_body\"," not in queue[0]
    assert "[\"response_body\"," in queue[0]

    queue = []
    logger = HttpLogger(queue=queue, rules='!response_body! remove_unless !.*blahblahblah.*!')
    logger.log(request=mock_request_with_json2(), response=mock_response_with_html())
    assert len(queue) == 1
    assert "[\"request_body\"," in queue[0]
    assert "[\"response_body\"," not in queue[0]

    queue = []
    logger = HttpLogger(queue=queue, rules='!response_body|request_body! remove_unless !.*World.*!')
    logger.log(request=mock_request_with_json2(), response=mock_response_with_html())
    assert len(queue) == 1
    assert "[\"request_body\"," not in queue[0]
    assert "[\"response_body\"," in queue[0]

    queue = []
    logger = HttpLogger(queue=queue, rules='!response_body|request_body! remove_unless !.*!')
    logger.log(request=mock_request_with_json2(), response=mock_response_with_html())
    assert len(queue) == 1
    assert "[\"request_body\"," in queue[0]
    assert "[\"response_body\"," in queue[0]

    queue = []
    logger = HttpLogger(queue=queue, rules="!response_body! remove_unless !.*!\n!request_body! remove_unless !.*!")
    logger.log(request=mock_request_with_json2(), response=mock_response_with_html())
    assert len(queue) == 1
    assert "[\"request_body\"," in queue[0]
    assert "[\"response_body\"," in queue[0]


def test_uses_remove_unless_found_rules():
    queue = []
    logger = HttpLogger(queue=queue, rules='!response_header:blahblahblah! remove_unless_found !.*!')
    logger.log(request=mock_request_with_json2(), response=mock_response_with_html())
    assert len(queue) == 1

    queue = []
    logger = HttpLogger(queue=queue, rules='!.*! remove_unless_found !blahblahblah!')
    logger.log(request=mock_request_with_json2(), response=mock_response_with_html())
    assert len(queue) == 0

    queue = []
    logger = HttpLogger(queue=queue, rules='!request_body! remove_unless_found !blahblahblah!')
    logger.log(request=mock_request_with_json2(), response=mock_response_with_html())
    assert len(queue) == 1
    assert "[\"request_body\"," not in queue[0]
    assert "[\"response_body\"," in queue[0]

    queue = []
    logger = HttpLogger(queue=queue, rules='!response_body! remove_unless_found !blahblahblah!')
    logger.log(request=mock_request_with_json2(), response=mock_response_with_html())
    assert len(queue) == 1
    assert "[\"request_body\"," in queue[0]
    assert "[\"response_body\"," not in queue[0]

    queue = []
    logger = HttpLogger(queue=queue, rules='!response_body|request_body! remove_unless_found !World!')
    logger.log(request=mock_request_with_json2(), response=mock_response_with_html())
    assert len(queue) == 1
    assert "[\"request_body\"," not in queue[0]
    assert "[\"response_body\"," in queue[0]

    queue = []
    logger = HttpLogger(queue=queue, rules='!response_body|request_body! remove_unless_found !.*World.*!')
    logger.log(request=mock_request_with_json2(), response=mock_response_with_html())
    assert len(queue) == 1
    assert "[\"request_body\"," not in queue[0]
    assert "[\"response_body\"," in queue[0]

    queue = []
    logger = HttpLogger(queue=queue, rules='!response_body|request_body! remove_unless_found !.*!')
    logger.log(request=mock_request_with_json2(), response=mock_response_with_html())
    assert len(queue) == 1
    assert "[\"request_body\"," in queue[0]
    assert "[\"response_body\"," in queue[0]


def test_uses_replace_rules():
    queue = []
    logger = HttpLogger(queue=queue, rules='!response_body! replace !blahblahblah!, !ZZZZZ!')
    logger.log(request=mock_request_with_json2(), response=mock_response_with_html())
    assert len(queue) == 1
    assert 'World' in queue[0]
    assert 'ZZZZZ' not in queue[0]

    queue = []
    logger = HttpLogger(queue=queue, rules='!response_body! replace !World!, !Mundo!')
    logger.log(request=mock_request_with_json2(), response=mock_response_with_html())
    assert len(queue) == 1
    assert "[\"response_body\",\"<html>Hello Mundo!</html>\"]," in queue[0]

    queue = []
    logger = HttpLogger(queue=queue, rules='!request_body|response_body! replace !^.*!, !ZZZZZ!')
    logger.log(request=mock_request_with_json2(), response=mock_response_with_html())
    assert len(queue) == 1
    assert "[\"request_body\",\"ZZZZZ\"" in queue[0]
    assert "[\"response_body\",\"ZZZZZ\"" in queue[0]

    queue = []
    logger = HttpLogger(queue=queue, rules="!request_body! replace !^.*!, !QQ!\n!response_body! replace !^.*!, !SS!")
    logger.log(request=mock_request_with_json2(), response=mock_response_with_html())
    assert len(queue) == 1
    assert "[\"request_body\",\"QQ\"" in queue[0]
    assert "[\"response_body\",\"SS\"" in queue[0]

    queue = []
    logger = HttpLogger(queue=queue, rules='!response_body! replace !World!, !!')
    logger.log(request=mock_request_with_json2(), response=mock_response_with_html())
    assert len(queue) == 1
    assert "[\"response_body\",\"<html>Hello !</html>\"]," in queue[0]

    queue = []
    logger = HttpLogger(queue=queue, rules='!response_body! replace !.*!, !!')
    logger.log(request=mock_request_with_json2(), response=mock_response_with_html())
    assert len(queue) == 1
    assert "[\"response_body\"," not in queue[0]

    queue = []
    logger = HttpLogger(queue=queue, rules='!response_body! replace !World!, !Z!')
    logger.log(request=mock_request_with_json2(), response=mock_response_with_html(), response_body=MOCK_HTML3)
    assert len(queue) == 1
    assert "[\"response_body\",\"<html>1 Z 2 Z Red Z Blue Z!</html>\"]," in queue[0]

    queue = []
    logger = HttpLogger(queue=queue, rules='!response_body! replace !World!, !Z!')
    logger.log(request=mock_request_with_json2(), response=mock_response_with_html(), response_body=MOCK_HTML4)
    assert len(queue) == 1
    assert "[\"response_body\",\"<html>1 Z\\n2 Z\\nRed Z \\nBlue Z!\\n</html>\"]," in queue[0]


def test_uses_replace_rules_with_complex_expressions():
    queue = []
    logger = HttpLogger(queue=queue,
                        rules="/response_body/ replace /[a-zA-Z0-9.!#$%&’*+\\/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\\.[a-zA-Z0-9-]+)/, /x@y.com/")
    logger.log(request=mock_request_with_json2(), response=mock_response_with_html(),
               response_body=MOCK_HTML.replace('World', 'rob@resurface.io'))
    assert len(queue) == 1
    assert "[\"response_body\",\"<html>Hello x@y.com!</html>\"]," in queue[0]

    queue = []
    logger = HttpLogger(queue=queue, rules="/response_body/ replace /[0-9\\.\\-\\/]{9,}/, /xyxy/")
    logger.log(request=mock_request_with_json2(), response=mock_response_with_html(),
               response_body=MOCK_HTML.replace('World', '123-45-1343'))
    assert len(queue) == 1
    assert "[\"response_body\",\"<html>Hello xyxy!</html>\"]," in queue[0]

    # todo this specific case not working...
    # queue = []
    # logger = HttpLogger(queue=queue, rules="!response_body! replace !World!, !<b>\\0</b>!")
    # logger.log(request=mock_request_with_json2(), response=mock_response_with_html())
    # assert len(queue) == 1
    # assert "[\"response_body\",\"<html>Hello <b>World</b>!</html>\"]," in queue[0]

    queue = []
    logger = HttpLogger(queue=queue, rules="!response_body! replace !(World)!, !<b>\\1</b>!")
    logger.log(request=mock_request_with_json2(), response=mock_response_with_html())
    assert len(queue) == 1
    assert "[\"response_body\",\"<html>Hello <b>World</b>!</html>\"]," in queue[0]

    queue = []
    logger = HttpLogger(queue=queue, rules="!response_body! replace !<input([^>]*)>([^<]*)</input>!, !<input\\1></input>!")
    logger.log(request=mock_request_with_json2(), response=mock_response_with_html(), response_body=MOCK_HTML5)
    assert len(queue) == 1
    assert "[\"response_body\",\"<html>\\n<input type=\\\"hidden\\\"></input>\\n<input class='foo' type=\\\"hidden\\\"></input>\\n</html>\"]," in queue[0]


def test_uses_sample_rules():
    queue = []

    try:
        HttpLogger(queue=queue, rules="sample 10\nsample 99")
        assert False is True
    except Exception as e:
        assert str(e) == 'Multiple sample rules'

    logger = HttpLogger(queue=queue, rules="sample 10")
    for i in range(1, 101): logger.log(request=mock_request_with_json2(), response=mock_response_with_html())
    assert 2 <= len(queue) <= 20


def test_uses_skip_compression_rules():
    logger = HttpLogger(url="http://mysite.com")
    assert logger.skip_compression is False
    logger = HttpLogger(url="http://mysite.com", rules="")
    assert logger.skip_compression is False
    logger = HttpLogger(url="http://mysite.com", rules="skip_compression")
    assert logger.skip_compression is True


def test_uses_skip_submission_rules():
    logger = HttpLogger(url="http://mysite.com")
    assert logger.skip_submission is False
    logger = HttpLogger(url="http://mysite.com", rules="")
    assert logger.skip_submission is False
    logger = HttpLogger(url="http://mysite.com", rules="skip_submission")
    assert logger.skip_submission is True


def test_uses_stop_rules():
    queue = []
    logger = HttpLogger(queue=queue, rules='!response_header:blahblahblah! stop')
    logger.log(request=mock_request_with_json2(), response=mock_response_with_html())
    assert len(queue) == 1

    queue = []
    logger = HttpLogger(queue=queue, rules='!.*! stop')
    logger.log(request=mock_request_with_json2(), response=mock_response_with_html())
    assert len(queue) == 0

    queue = []
    logger = HttpLogger(queue=queue, rules='!request_body! stop')
    logger.log(request=mock_request_with_json2(), response=mock_response_with_html())
    assert len(queue) == 0

    queue = []
    logger = HttpLogger(queue=queue, rules='!response_body! stop')
    logger.log(request=mock_request_with_json2(), response=mock_response_with_html())
    assert len(queue) == 0

    queue = []
    logger = HttpLogger(queue=queue, rules="!request_body! stop\n!response_body! stop")
    logger.log(request=mock_request_with_json2(), response=mock_response_with_html())
    assert len(queue) == 0


def test_uses_stop_if_rules():
    queue = []
    logger = HttpLogger(queue=queue, rules='!response_header:blahblahblah! stop_if !.*!')
    logger.log(request=mock_request_with_json2(), response=mock_response_with_html())
    assert len(queue) == 1

    queue = []
    logger = HttpLogger(queue=queue, rules='!response_body! stop_if !.*!')
    logger.log(request=mock_request_with_json2(), response=mock_response_with_html())
    assert len(queue) == 0

    queue = []
    logger = HttpLogger(queue=queue, rules='!response_body! stop_if !.*World.*!')
    logger.log(request=mock_request_with_json2(), response=mock_response_with_html())
    assert len(queue) == 0

    queue = []
    logger = HttpLogger(queue=queue, rules='!response_body! stop_if !.*blahblahblah.*!')
    logger.log(request=mock_request_with_json2(), response=mock_response_with_html())
    assert len(queue) == 1


def test_uses_stop_if_found_rules():
    queue = []
    logger = HttpLogger(queue=queue, rules='!response_header:blahblahblah! stop_if_found !.*!')
    logger.log(request=mock_request_with_json2(), response=mock_response_with_html())
    assert len(queue) == 1

    queue = []
    logger = HttpLogger(queue=queue, rules='!response_body! stop_if_found !.*!')
    logger.log(request=mock_request_with_json2(), response=mock_response_with_html())
    assert len(queue) == 0

    queue = []
    logger = HttpLogger(queue=queue, rules='!response_body! stop_if_found !World!')
    logger.log(request=mock_request_with_json2(), response=mock_response_with_html())
    assert len(queue) == 0

    queue = []
    logger = HttpLogger(queue=queue, rules='!response_body! stop_if_found !.*World.*!')
    logger.log(request=mock_request_with_json2(), response=mock_response_with_html())
    assert len(queue) == 0

    queue = []
    logger = HttpLogger(queue=queue, rules='!response_body! stop_if_found !blahblahblah!')
    logger.log(request=mock_request_with_json2(), response=mock_response_with_html())
    assert len(queue) == 1


def test_uses_stop_unless_rules():
    queue = []
    logger = HttpLogger(queue=queue, rules='!response_header:blahblahblah! stop_unless !.*!')
    logger.log(request=mock_request_with_json2(), response=mock_response_with_html())
    assert len(queue) == 0

    queue = []
    logger = HttpLogger(queue=queue, rules='!response_body! stop_unless !.*!')
    logger.log(request=mock_request_with_json2(), response=mock_response_with_html())
    assert len(queue) == 1

    queue = []
    logger = HttpLogger(queue=queue, rules='!response_body! stop_unless !.*World.*!')
    logger.log(request=mock_request_with_json2(), response=mock_response_with_html())
    assert len(queue) == 1

    queue = []
    logger = HttpLogger(queue=queue, rules='!response_body! stop_unless !.*blahblahblah.*!')
    logger.log(request=mock_request_with_json2(), response=mock_response_with_html())
    assert len(queue) == 0


def test_uses_stop_unless_found_rules():
    queue = []
    logger = HttpLogger(queue=queue, rules='!response_header:blahblahblah! stop_unless_found !.*!')
    logger.log(request=mock_request_with_json2(), response=mock_response_with_html())
    assert len(queue) == 0

    queue = []
    logger = HttpLogger(queue=queue, rules='!response_body! stop_unless_found !.*!')
    logger.log(request=mock_request_with_json2(), response=mock_response_with_html())
    assert len(queue) == 1

    queue = []
    logger = HttpLogger(queue=queue, rules='!response_body! stop_unless_found !World!')
    logger.log(request=mock_request_with_json2(), response=mock_response_with_html())
    assert len(queue) == 1

    queue = []
    logger = HttpLogger(queue=queue, rules='!response_body! stop_unless_found !.*World.*!')
    logger.log(request=mock_request_with_json2(), response=mock_response_with_html())
    assert len(queue) == 1

    queue = []
    logger = HttpLogger(queue=queue, rules='!response_body! stop_unless_found !blahblahblah!')
    logger.log(request=mock_request_with_json2(), response=mock_response_with_html())
    assert len(queue) == 0
