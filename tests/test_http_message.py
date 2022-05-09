# coding: utf-8
# © 2016-2022 Resurface Labs Inc.

from tests.test_helper import (
    MOCK_HTML,
    MOCK_HTML2,
    MOCK_JSON_ESCAPED,
    MOCK_NOW,
    MOCK_QUERY_STRING,
    MOCK_URL,
    mock_request,
    mock_request_with_json,
    mock_request_with_json2,
    mock_response,
    mock_response_with_html,
    parseable,
)
from usagelogger import HttpLogger, HttpMessage, HttpRequestImpl, HttpResponseImpl


def test_formats_request():
    queue = []
    logger = HttpLogger(queue=queue, rules="include debug")
    HttpMessage.send(
        logger, request=mock_request(), response=mock_response(), now=MOCK_NOW
    )
    assert len(queue) == 1
    msg = queue[0]
    assert parseable(msg) is True
    assert f'["host","{HttpLogger.host_lookup()}"]' in msg
    assert f'["now","{MOCK_NOW}"]' in msg
    assert '["request_method","GET"]' in msg
    assert f'["request_url","{MOCK_URL}"]' in msg
    assert "request_body" not in msg
    assert "request_header" not in msg
    assert "request_param" not in msg
    assert "interval" not in msg


def test_formats_request_with_body():
    queue = []
    logger = HttpLogger(queue=queue, rules="include debug")
    HttpMessage.send(
        logger,
        request=mock_request_with_json(),
        response=mock_response(),
        request_body=MOCK_HTML,
    )
    assert len(queue) == 1
    msg = queue[0]
    assert parseable(msg) is True
    assert f'["request_body","{MOCK_HTML}"]' in msg
    assert '["request_header:content-type","Application/JSON"]' in msg
    assert '["request_method","POST"]' in msg
    assert f'["request_param:message","{MOCK_JSON_ESCAPED}"]' in msg
    assert f'["request_url","{MOCK_URL}?{MOCK_QUERY_STRING}"]' in msg
    assert "request_param:foo" not in msg


def test_formats_request_with_empty_body():
    queue = []
    logger = HttpLogger(queue=queue, rules="include debug")
    HttpMessage.send(
        logger,
        request=mock_request_with_json2(),
        response=mock_response(),
        request_body="",
    )
    assert len(queue) == 1
    msg = queue[0]
    assert parseable(msg) is True
    assert '["request_header:a","1, 2"]' in msg
    assert '["request_header:abc","123"]' in msg
    assert '["request_header:content-type","Application/JSON"]' in msg
    assert '["request_method","POST"]' in msg
    assert '["request_param:abc","123, 234"]' in msg
    assert f'["request_param:message","{MOCK_JSON_ESCAPED}"]' in msg
    assert f'["request_url","{MOCK_URL}?{MOCK_QUERY_STRING}"]' in msg
    assert "request_body" not in msg
    assert "request_param:foo" not in msg


def test_formats_request_with_missing_details():
    queue = []
    logger = HttpLogger(queue=queue, rules="include debug")
    HttpMessage.send(
        logger,
        request=HttpRequestImpl(),
        response=mock_response(),
        response_body=None,
        request_body=None,
        now=None,
        interval=None,
    )
    assert len(queue) == 1
    msg = queue[0]
    assert parseable(msg) is True
    assert "request_body" not in msg
    assert "request_header" not in msg
    assert "request_method" not in msg
    assert "request_param" not in msg
    assert "request_url" not in msg
    assert "interval" not in msg


def test_formats_response():
    queue = []
    logger = HttpLogger(queue=queue, rules="include debug")
    HttpMessage.send(logger, request=mock_request(), response=mock_response())
    assert len(queue) == 1
    msg = queue[0]
    assert parseable(msg) is True
    assert '["response_code","200"]' in msg
    assert "response_body" not in msg
    assert "response_header" not in msg


def test_formats_response_with_body():
    queue = []
    logger = HttpLogger(queue=queue, rules="include debug")
    HttpMessage.send(
        logger,
        request=mock_request(),
        response=mock_response_with_html(),
        response_body=MOCK_HTML2,
    )
    assert len(queue) == 1
    msg = queue[0]
    assert parseable(msg) is True
    assert f'["response_body","{MOCK_HTML2}"]' in msg
    assert '["response_code","200"]' in msg
    assert '["response_header:content-type","text/html; charset=utf-8"]' in msg


def test_formats_response_with_empty_body():
    queue = []
    logger = HttpLogger(queue=queue, rules="include debug")
    HttpMessage.send(
        logger,
        request=mock_request(),
        response=mock_response_with_html(),
        response_body="",
    )
    assert len(queue) == 1
    msg = queue[0]
    assert parseable(msg) is True
    assert '["response_code","200"]' in msg
    assert '["response_header:content-type","text/html; charset=utf-8"]' in msg
    assert "response_body" not in msg


def test_formats_response_with_missing_details():
    queue = []
    logger = HttpLogger(queue=queue, rules="include debug")
    HttpMessage.send(
        logger,
        request=mock_request(),
        response=HttpResponseImpl(),
        response_body=None,
        request_body=None,
        now=None,
        interval=None,
    )
    assert len(queue) == 1
    msg = queue[0]
    assert parseable(msg) is True
    assert "response_body" not in msg
    assert "response_code" not in msg
    assert "response_header" not in msg
    assert "interval" not in msg
