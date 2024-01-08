# coding: utf-8
# © 2016-2024 Graylog, Inc.

from tests.test_helper import (
    MOCK_HTML,
    MOCK_HTML3,
    MOCK_HTML4,
    MOCK_HTML5,
    mock_request_with_json2,
    mock_response_with_html,
)
from usagelogger import HttpLogger, HttpMessage, HttpRules


def test_overrides_default_rules():
    assert HttpRules.default_rules() == HttpRules.strict_rules()
    try:
        logger = HttpLogger(url="https://mysite.com")
        assert logger.rules.text == HttpRules.strict_rules()
        logger = HttpLogger(url="https://mysite.com", rules="# 123")
        assert logger.rules.text == "# 123"

        HttpRules.set_default_rules("")
        logger = HttpLogger(url="https://mysite.com")
        assert logger.rules.text == ""
        logger = HttpLogger(url="https://mysite.com", rules="   ")
        assert logger.rules.text == ""
        logger = HttpLogger(url="https://mysite.com", rules=" sample 42")
        assert logger.rules.text == " sample 42"

        HttpRules.set_default_rules("skip_compression")
        logger = HttpLogger(url="https://mysite.com")
        assert logger.rules.text == "skip_compression"
        logger = HttpLogger(
            url="https://mysite.com", rules="include default\nskip_submission\n"
        )
        assert logger.rules.text == "skip_compression\nskip_submission\n"

        HttpRules.set_default_rules("sample 42\n")
        logger = HttpLogger(url="https://mysite.com")
        assert logger.rules.text == "sample 42\n"
        logger = HttpLogger(url="https://mysite.com", rules="   ")
        assert logger.rules.text == "sample 42\n"
        logger = HttpLogger(
            url="https://mysite.com", rules="include default\nskip_submission\n"
        )
        assert logger.rules.text == "sample 42\n\nskip_submission\n"

        HttpRules.set_default_rules("include debug")
        logger = HttpLogger(url="https://mysite.com", rules=HttpRules.strict_rules())
        assert logger.rules.text == HttpRules.strict_rules()
    finally:
        HttpRules.set_default_rules(HttpRules.strict_rules())


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


# Todo: Finish this test
def test_uses_copy_session_field_rules():
    assert None is None


# Todo: Finish this test
def test_uses_copy_session_field_and_remove_rules():
    assert None is None


# Todo: Finish this test
def test_uses_copy_session_field_and_stop_rules():
    assert None is None


def test_uses_remove_rules():
    queue = []
    logger = HttpLogger(queue=queue, rules="!.*! remove")
    HttpMessage.send(
        logger, request=mock_request_with_json2(), response=mock_response_with_html()
    )
    assert len(queue) == 0

    queue = []
    logger = HttpLogger(queue=queue, rules="!request_body! remove")
    HttpMessage.send(
        logger, request=mock_request_with_json2(), response=mock_response_with_html()
    )
    assert len(queue) == 1
    assert '["request_body",' not in queue[0]
    assert '["response_body",' in queue[0]

    queue = []
    logger = HttpLogger(queue=queue, rules="!response_body! remove")
    HttpMessage.send(
        logger, request=mock_request_with_json2(), response=mock_response_with_html()
    )
    assert len(queue) == 1
    assert '["request_body",' in queue[0]
    assert '["response_body",' not in queue[0]

    queue = []
    logger = HttpLogger(queue=queue, rules="!request_body|response_body! remove")
    HttpMessage.send(
        logger, request=mock_request_with_json2(), response=mock_response_with_html()
    )
    assert len(queue) == 1
    assert '["request_body",' not in queue[0]
    assert '["response_body",' not in queue[0]

    queue = []
    logger = HttpLogger(queue=queue, rules="!request_header:.*! remove")
    HttpMessage.send(
        logger, request=mock_request_with_json2(), response=mock_response_with_html()
    )
    assert len(queue) == 1
    assert '["request_body",' in queue[0]
    assert '["request_header:' not in queue[0]
    assert '["response_body",' in queue[0]

    queue = []
    logger = HttpLogger(
        queue=queue, rules="!request_header:abc! remove\n!response_body! remove"
    )
    HttpMessage.send(
        logger, request=mock_request_with_json2(), response=mock_response_with_html()
    )
    assert len(queue) == 1
    assert '["request_body",' in queue[0]
    assert '["request_header:' in queue[0]
    assert '["request_header:abc' not in queue[0]
    assert '["response_body",' not in queue[0]


def test_uses_remove_if_rules():
    queue = []
    logger = HttpLogger(
        queue=queue, rules="!response_header:blahblahblah! remove_if !.*!"
    )
    HttpMessage.send(
        logger, request=mock_request_with_json2(), response=mock_response_with_html()
    )
    assert len(queue) == 1

    queue = []
    logger = HttpLogger(queue=queue, rules="!.*! remove_if !.*!")
    HttpMessage.send(
        logger, request=mock_request_with_json2(), response=mock_response_with_html()
    )
    assert len(queue) == 0

    queue = []
    logger = HttpLogger(queue=queue, rules="!request_body! remove_if !.*!")
    HttpMessage.send(
        logger, request=mock_request_with_json2(), response=mock_response_with_html()
    )
    assert len(queue) == 1
    assert '["request_body",' not in queue[0]
    assert '["response_body",' in queue[0]

    queue = []
    logger = HttpLogger(queue=queue, rules="!response_body! remove_if !.*!")
    HttpMessage.send(
        logger, request=mock_request_with_json2(), response=mock_response_with_html()
    )
    assert len(queue) == 1
    assert '["request_body",' in queue[0]
    assert '["response_body",' not in queue[0]

    queue = []
    logger = HttpLogger(
        queue=queue, rules="!response_body|request_body! remove_if !.*World.*!"
    )
    HttpMessage.send(
        logger, request=mock_request_with_json2(), response=mock_response_with_html()
    )
    assert len(queue) == 1
    assert '["request_body",' in queue[0]
    assert '["response_body",' not in queue[0]

    queue = []
    logger = HttpLogger(
        queue=queue, rules="!response_body|request_body! remove_if !.*blahblahblah.*!"
    )
    HttpMessage.send(
        logger, request=mock_request_with_json2(), response=mock_response_with_html()
    )
    assert len(queue) == 1
    assert '["request_body",' in queue[0]
    assert '["response_body",' in queue[0]

    queue = []
    logger = HttpLogger(
        queue=queue,
        rules="!request_body! remove_if !.*!\n!response_body! remove_if !.*!",
    )
    HttpMessage.send(
        logger, request=mock_request_with_json2(), response=mock_response_with_html()
    )
    assert len(queue) == 1
    assert '["request_body",' not in queue[0]
    assert '["response_body",' not in queue[0]


def test_uses_remove_if_found_rules():
    queue = []
    logger = HttpLogger(
        queue=queue, rules="!response_header:blahblahblah! remove_if_found !.*!"
    )
    HttpMessage.send(
        logger, request=mock_request_with_json2(), response=mock_response_with_html()
    )
    assert len(queue) == 1

    queue = []
    logger = HttpLogger(queue=queue, rules="!.*! remove_if_found !.*!")
    HttpMessage.send(
        logger, request=mock_request_with_json2(), response=mock_response_with_html()
    )
    assert len(queue) == 0

    queue = []
    logger = HttpLogger(queue=queue, rules="!request_body! remove_if_found !.*!")
    HttpMessage.send(
        logger, request=mock_request_with_json2(), response=mock_response_with_html()
    )
    assert len(queue) == 1
    assert '["request_body",' not in queue[0]
    assert '["response_body",' in queue[0]

    queue = []
    logger = HttpLogger(queue=queue, rules="!response_body! remove_if_found !.*!")
    HttpMessage.send(
        logger, request=mock_request_with_json2(), response=mock_response_with_html()
    )
    assert len(queue) == 1
    assert '["request_body",' in queue[0]
    assert '["response_body",' not in queue[0]

    queue = []
    logger = HttpLogger(
        queue=queue, rules="!response_body|request_body! remove_if_found !World!"
    )
    HttpMessage.send(
        logger, request=mock_request_with_json2(), response=mock_response_with_html()
    )
    assert len(queue) == 1
    assert '["request_body",' in queue[0]
    assert '["response_body",' not in queue[0]

    queue = []
    logger = HttpLogger(
        queue=queue, rules="!response_body|request_body! remove_if_found !.*World.*!"
    )
    HttpMessage.send(
        logger, request=mock_request_with_json2(), response=mock_response_with_html()
    )
    assert len(queue) == 1
    assert '["request_body",' in queue[0]
    assert '["response_body",' not in queue[0]

    queue = []
    logger = HttpLogger(
        queue=queue, rules="!response_body|request_body! remove_if_found !blahblahblah!"
    )
    HttpMessage.send(
        logger, request=mock_request_with_json2(), response=mock_response_with_html()
    )
    assert len(queue) == 1
    assert '["request_body",' in queue[0]
    assert '["response_body",' in queue[0]


def test_uses_remove_unless_rules():
    queue = []
    logger = HttpLogger(
        queue=queue, rules="!response_header:blahblahblah! remove_unless !.*!"
    )
    HttpMessage.send(
        logger, request=mock_request_with_json2(), response=mock_response_with_html()
    )
    assert len(queue) == 1

    queue = []
    logger = HttpLogger(queue=queue, rules="!.*! remove_unless !.*blahblahblah.*!")
    HttpMessage.send(
        logger, request=mock_request_with_json2(), response=mock_response_with_html()
    )
    assert len(queue) == 0

    queue = []
    logger = HttpLogger(
        queue=queue, rules="!request_body! remove_unless !.*blahblahblah.*!"
    )
    HttpMessage.send(
        logger, request=mock_request_with_json2(), response=mock_response_with_html()
    )
    assert len(queue) == 1
    assert '["request_body",' not in queue[0]
    assert '["response_body",' in queue[0]

    queue = []
    logger = HttpLogger(
        queue=queue, rules="!response_body! remove_unless !.*blahblahblah.*!"
    )
    HttpMessage.send(
        logger, request=mock_request_with_json2(), response=mock_response_with_html()
    )
    assert len(queue) == 1
    assert '["request_body",' in queue[0]
    assert '["response_body",' not in queue[0]

    queue = []
    logger = HttpLogger(
        queue=queue, rules="!response_body|request_body! remove_unless !.*World.*!"
    )
    HttpMessage.send(
        logger, request=mock_request_with_json2(), response=mock_response_with_html()
    )
    assert len(queue) == 1
    assert '["request_body",' not in queue[0]
    assert '["response_body",' in queue[0]

    queue = []
    logger = HttpLogger(
        queue=queue, rules="!response_body|request_body! remove_unless !.*!"
    )
    HttpMessage.send(
        logger, request=mock_request_with_json2(), response=mock_response_with_html()
    )
    assert len(queue) == 1
    assert '["request_body",' in queue[0]
    assert '["response_body",' in queue[0]

    queue = []
    logger = HttpLogger(
        queue=queue,
        rules="!response_body! remove_unless !.*!\n!request_body! remove_unless !.*!",
    )
    HttpMessage.send(
        logger, request=mock_request_with_json2(), response=mock_response_with_html()
    )
    assert len(queue) == 1
    assert '["request_body",' in queue[0]
    assert '["response_body",' in queue[0]


def test_uses_remove_unless_found_rules():
    queue = []
    logger = HttpLogger(
        queue=queue, rules="!response_header:blahblahblah! remove_unless_found !.*!"
    )
    HttpMessage.send(
        logger, request=mock_request_with_json2(), response=mock_response_with_html()
    )
    assert len(queue) == 1

    queue = []
    logger = HttpLogger(queue=queue, rules="!.*! remove_unless_found !blahblahblah!")
    HttpMessage.send(
        logger, request=mock_request_with_json2(), response=mock_response_with_html()
    )
    assert len(queue) == 0

    queue = []
    logger = HttpLogger(
        queue=queue, rules="!request_body! remove_unless_found !blahblahblah!"
    )
    HttpMessage.send(
        logger, request=mock_request_with_json2(), response=mock_response_with_html()
    )
    assert len(queue) == 1
    assert '["request_body",' not in queue[0]
    assert '["response_body",' in queue[0]

    queue = []
    logger = HttpLogger(
        queue=queue, rules="!response_body! remove_unless_found !blahblahblah!"
    )
    HttpMessage.send(
        logger, request=mock_request_with_json2(), response=mock_response_with_html()
    )
    assert len(queue) == 1
    assert '["request_body",' in queue[0]
    assert '["response_body",' not in queue[0]

    queue = []
    logger = HttpLogger(
        queue=queue, rules="!response_body|request_body! remove_unless_found !World!"
    )
    HttpMessage.send(
        logger, request=mock_request_with_json2(), response=mock_response_with_html()
    )
    assert len(queue) == 1
    assert '["request_body",' not in queue[0]
    assert '["response_body",' in queue[0]

    queue = []
    logger = HttpLogger(
        queue=queue,
        rules="!response_body|request_body! remove_unless_found !.*World.*!",
    )
    HttpMessage.send(
        logger, request=mock_request_with_json2(), response=mock_response_with_html()
    )
    assert len(queue) == 1
    assert '["request_body",' not in queue[0]
    assert '["response_body",' in queue[0]

    queue = []
    logger = HttpLogger(
        queue=queue, rules="!response_body|request_body! remove_unless_found !.*!"
    )
    HttpMessage.send(
        logger, request=mock_request_with_json2(), response=mock_response_with_html()
    )
    assert len(queue) == 1
    assert '["request_body",' in queue[0]
    assert '["response_body",' in queue[0]


def test_uses_replace_rules():
    queue = []
    logger = HttpLogger(
        queue=queue, rules="!response_body! replace !blahblahblah!, !ZZZZZ!"
    )
    HttpMessage.send(
        logger, request=mock_request_with_json2(), response=mock_response_with_html()
    )
    assert len(queue) == 1
    assert "World" in queue[0]
    assert "ZZZZZ" not in queue[0]

    queue = []
    logger = HttpLogger(queue=queue, rules="!response_body! replace !World!, !Mundo!")
    HttpMessage.send(
        logger, request=mock_request_with_json2(), response=mock_response_with_html()
    )
    assert len(queue) == 1
    assert '["response_body","<html>Hello Mundo!</html>"],' in queue[0]

    queue = []
    logger = HttpLogger(
        queue=queue, rules="!request_body|response_body! replace !^.*!, !ZZZZZ!"
    )
    HttpMessage.send(
        logger, request=mock_request_with_json2(), response=mock_response_with_html()
    )
    assert len(queue) == 1
    assert '["request_body","ZZZZZ"' in queue[0]
    assert '["response_body","ZZZZZ"' in queue[0]

    queue = []
    logger = HttpLogger(
        queue=queue,
        rules="!request_body! replace !^.*!, !QQ!\n!response_body! replace !^.*!, !SS!",
    )
    HttpMessage.send(
        logger, request=mock_request_with_json2(), response=mock_response_with_html()
    )
    assert len(queue) == 1
    assert '["request_body","QQ"' in queue[0]
    assert '["response_body","SS"' in queue[0]

    queue = []
    logger = HttpLogger(queue=queue, rules="!response_body! replace !World!, !!")
    HttpMessage.send(
        logger, request=mock_request_with_json2(), response=mock_response_with_html()
    )
    assert len(queue) == 1
    assert '["response_body","<html>Hello !</html>"],' in queue[0]

    queue = []
    logger = HttpLogger(queue=queue, rules="!response_body! replace !.*!, !!")
    HttpMessage.send(
        logger, request=mock_request_with_json2(), response=mock_response_with_html()
    )
    assert len(queue) == 1
    assert '["response_body",' not in queue[0]

    queue = []
    logger = HttpLogger(queue=queue, rules="!response_body! replace !World!, !Z!")
    HttpMessage.send(
        logger,
        request=mock_request_with_json2(),
        response=mock_response_with_html(),
        response_body=MOCK_HTML3,
    )
    assert len(queue) == 1
    assert '["response_body","<html>1 Z 2 Z Red Z Blue Z!</html>"],' in queue[0]

    queue = []
    logger = HttpLogger(queue=queue, rules="!response_body! replace !World!, !Z!")
    HttpMessage.send(
        logger,
        request=mock_request_with_json2(),
        response=mock_response_with_html(),
        response_body=MOCK_HTML4,
    )
    assert len(queue) == 1
    assert (
        '["response_body","<html>1 Z\\n2 Z\\nRed Z \\nBlue Z!\\n</html>"],' in queue[0]
    )


def test_uses_replace_rules_with_complex_expressions():
    queue = []
    logger = HttpLogger(
        queue=queue,
        rules="/response_body/ replace /[a-zA-Z0-9.!#$%&’*+\\/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\\.[a-zA-Z0-9-]+)/, /x@y.com/",
    )
    HttpMessage.send(
        logger,
        request=mock_request_with_json2(),
        response=mock_response_with_html(),
        response_body=MOCK_HTML.replace("World", "rob@resurface.io"),
    )
    assert len(queue) == 1
    assert '["response_body","<html>Hello x@y.com!</html>"],' in queue[0]

    queue = []
    logger = HttpLogger(
        queue=queue, rules="/response_body/ replace /[0-9\\.\\-\\/]{9,}/, /xyxy/"
    )
    HttpMessage.send(
        logger,
        request=mock_request_with_json2(),
        response=mock_response_with_html(),
        response_body=MOCK_HTML.replace("World", "123-45-1343"),
    )
    assert len(queue) == 1
    assert '["response_body","<html>Hello xyxy!</html>"],' in queue[0]

    # todo this specific case not working
    # queue = []
    # logger = HttpLogger(queue=queue, rules="!response_body! replace !World!, !<b>\\0</b>!")
    # HttpMessage.send(logger, request=mock_request_with_json2(), response=mock_response_with_html())
    # assert len(queue) == 1
    # assert "[\"response_body\",\"<html>Hello <b>World</b>!</html>\"]," in queue[0]

    queue = []
    logger = HttpLogger(
        queue=queue, rules="!response_body! replace !(World)!, !<b>\\1</b>!"
    )
    HttpMessage.send(
        logger, request=mock_request_with_json2(), response=mock_response_with_html()
    )
    assert len(queue) == 1
    assert '["response_body","<html>Hello <b>World</b>!</html>"],' in queue[0]

    queue = []
    logger = HttpLogger(
        queue=queue,
        rules="!response_body! replace !<input([^>]*)>([^<]*)</input>!, !<input\\1></input>!",
    )
    HttpMessage.send(
        logger,
        request=mock_request_with_json2(),
        response=mock_response_with_html(),
        response_body=MOCK_HTML5,
    )
    assert len(queue) == 1
    assert (
        '["response_body","<html>\\n<input type=\\"hidden\\"></input>\\n<input class=\'foo\' type=\\"hidden\\"></input>\\n</html>"],'
        in queue[0]
    )


def test_uses_sample_rules():
    queue = []

    try:
        HttpLogger(queue=queue, rules="sample 10\nsample 99")
        assert False is True
    except Exception as e:
        assert str(e) == "Multiple sample rules"

    logger = HttpLogger(queue=queue, rules="sample 10")
    for i in range(1, 101):
        HttpMessage.send(
            logger,
            request=mock_request_with_json2(),
            response=mock_response_with_html(),
        )
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
    logger = HttpLogger(queue=queue, rules="!response_header:blahblahblah! stop")
    HttpMessage.send(
        logger, request=mock_request_with_json2(), response=mock_response_with_html()
    )
    assert len(queue) == 1

    queue = []
    logger = HttpLogger(queue=queue, rules="!.*! stop")
    HttpMessage.send(
        logger, request=mock_request_with_json2(), response=mock_response_with_html()
    )
    assert len(queue) == 0

    queue = []
    logger = HttpLogger(queue=queue, rules="!request_body! stop")
    HttpMessage.send(
        logger, request=mock_request_with_json2(), response=mock_response_with_html()
    )
    assert len(queue) == 0

    queue = []
    logger = HttpLogger(queue=queue, rules="!response_body! stop")
    HttpMessage.send(
        logger, request=mock_request_with_json2(), response=mock_response_with_html()
    )
    assert len(queue) == 0

    queue = []
    logger = HttpLogger(queue=queue, rules="!request_body! stop\n!response_body! stop")
    HttpMessage.send(
        logger, request=mock_request_with_json2(), response=mock_response_with_html()
    )
    assert len(queue) == 0


def test_uses_stop_if_rules():
    queue = []
    logger = HttpLogger(
        queue=queue, rules="!response_header:blahblahblah! stop_if !.*!"
    )
    HttpMessage.send(
        logger, request=mock_request_with_json2(), response=mock_response_with_html()
    )
    assert len(queue) == 1

    queue = []
    logger = HttpLogger(queue=queue, rules="!response_body! stop_if !.*!")
    HttpMessage.send(
        logger, request=mock_request_with_json2(), response=mock_response_with_html()
    )
    assert len(queue) == 0

    queue = []
    logger = HttpLogger(queue=queue, rules="!response_body! stop_if !.*World.*!")
    HttpMessage.send(
        logger, request=mock_request_with_json2(), response=mock_response_with_html()
    )
    assert len(queue) == 0

    queue = []
    logger = HttpLogger(queue=queue, rules="!response_body! stop_if !.*blahblahblah.*!")
    HttpMessage.send(
        logger, request=mock_request_with_json2(), response=mock_response_with_html()
    )
    assert len(queue) == 1


def test_uses_stop_if_found_rules():
    queue = []
    logger = HttpLogger(
        queue=queue, rules="!response_header:blahblahblah! stop_if_found !.*!"
    )
    HttpMessage.send(
        logger, request=mock_request_with_json2(), response=mock_response_with_html()
    )
    assert len(queue) == 1

    queue = []
    logger = HttpLogger(queue=queue, rules="!response_body! stop_if_found !.*!")
    HttpMessage.send(
        logger, request=mock_request_with_json2(), response=mock_response_with_html()
    )
    assert len(queue) == 0

    queue = []
    logger = HttpLogger(queue=queue, rules="!response_body! stop_if_found !World!")
    HttpMessage.send(
        logger, request=mock_request_with_json2(), response=mock_response_with_html()
    )
    assert len(queue) == 0

    queue = []
    logger = HttpLogger(queue=queue, rules="!response_body! stop_if_found !.*World.*!")
    HttpMessage.send(
        logger, request=mock_request_with_json2(), response=mock_response_with_html()
    )
    assert len(queue) == 0

    queue = []
    logger = HttpLogger(
        queue=queue, rules="!response_body! stop_if_found !blahblahblah!"
    )
    HttpMessage.send(
        logger, request=mock_request_with_json2(), response=mock_response_with_html()
    )
    assert len(queue) == 1


def test_uses_stop_unless_rules():
    queue = []
    logger = HttpLogger(
        queue=queue, rules="!response_header:blahblahblah! stop_unless !.*!"
    )
    HttpMessage.send(
        logger, request=mock_request_with_json2(), response=mock_response_with_html()
    )
    assert len(queue) == 0

    queue = []
    logger = HttpLogger(queue=queue, rules="!response_body! stop_unless !.*!")
    HttpMessage.send(
        logger, request=mock_request_with_json2(), response=mock_response_with_html()
    )
    assert len(queue) == 1

    queue = []
    logger = HttpLogger(queue=queue, rules="!response_body! stop_unless !.*World.*!")
    HttpMessage.send(
        logger, request=mock_request_with_json2(), response=mock_response_with_html()
    )
    assert len(queue) == 1

    queue = []
    logger = HttpLogger(
        queue=queue, rules="!response_body! stop_unless !.*blahblahblah.*!"
    )
    HttpMessage.send(
        logger, request=mock_request_with_json2(), response=mock_response_with_html()
    )
    assert len(queue) == 0


def test_uses_stop_unless_found_rules():
    queue = []
    logger = HttpLogger(
        queue=queue, rules="!response_header:blahblahblah! stop_unless_found !.*!"
    )
    HttpMessage.send(
        logger, request=mock_request_with_json2(), response=mock_response_with_html()
    )
    assert len(queue) == 0

    queue = []
    logger = HttpLogger(queue=queue, rules="!response_body! stop_unless_found !.*!")
    HttpMessage.send(
        logger, request=mock_request_with_json2(), response=mock_response_with_html()
    )
    assert len(queue) == 1

    queue = []
    logger = HttpLogger(queue=queue, rules="!response_body! stop_unless_found !World!")
    HttpMessage.send(
        logger, request=mock_request_with_json2(), response=mock_response_with_html()
    )
    assert len(queue) == 1

    queue = []
    logger = HttpLogger(
        queue=queue, rules="!response_body! stop_unless_found !.*World.*!"
    )
    HttpMessage.send(
        logger, request=mock_request_with_json2(), response=mock_response_with_html()
    )
    assert len(queue) == 1

    queue = []
    logger = HttpLogger(
        queue=queue, rules="!response_body! stop_unless_found !blahblahblah!"
    )
    HttpMessage.send(
        logger, request=mock_request_with_json2(), response=mock_response_with_html()
    )
    assert len(queue) == 0
