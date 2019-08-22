# coding: utf-8
# © 2016-2019 Resurface Labs Inc.

from test_helper import *
from usagelogger import HttpLogger, HttpRequestImpl, HttpResponseImpl

logger = HttpLogger(rules="include standard")


def test_formats_request():
    msg = logger.format(request=mock_request(), response=mock_response(), now=MOCK_NOW)
    assert parseable(msg) is True
    assert f"[\"agent\",\"{HttpLogger.AGENT}\"]" in msg
    assert f"[\"version\",\"{HttpLogger.version_lookup()}\"]" in msg
    assert f"[\"now\",\"{MOCK_NOW}\"]" in msg
    assert f"[\"request_method\",\"GET\"]" in msg
    assert f"[\"request_url\",\"{MOCK_URL}\"]" in msg
    assert f"request_body" not in msg
    assert f"request_header" not in msg
    assert f"request_param" not in msg


def test_formats_request_with_body():
    msg = logger.format(request=mock_request_with_json(), response=mock_response(), request_body=MOCK_HTML)
    assert parseable(msg) is True
    assert f"[\"request_body\",\"{MOCK_HTML}\"]" in msg
    assert f"[\"request_header:content-type\",\"Application/JSON\"]" in msg
    assert f"[\"request_method\",\"POST\"]" in msg
    # todo assert f"[\"request_param:message\",\"{MOCK_JSON_ESCAPED}\"]" in msg
    assert f"[\"request_url\",\"{MOCK_URL}?{MOCK_QUERY_STRING}\"]" in msg
    assert "request_param:foo" not in msg


def test_formats_request_with_empty_body():
    msg = logger.format(request=mock_request_with_json2(), response=mock_response(), request_body='')
    assert parseable(msg) is True
    assert f"[\"request_header:a\",\"1, 2\"]" in msg
    assert f"[\"request_header:abc\",\"123\"]" in msg
    assert f"[\"request_header:content-type\",\"Application/JSON\"]" in msg
    assert f"[\"request_method\",\"POST\"]" in msg
    # todo assert f"[\"request_param:abc\",\"123, 234\"]" in msg
    # todo assert f"[\"request_param:message\",\"{MOCK_JSON_ESCAPED}\"]" in msg
    assert f"[\"request_url\",\"{MOCK_URL}?{MOCK_QUERY_STRING}\"]" in msg
    assert f"request_body" not in msg
    assert "request_param:foo" not in msg


def test_formats_request_with_missing_details():
    msg = logger.format(request=HttpRequestImpl(), response=mock_response())
    assert parseable(msg) is True
    assert f"request_body" not in msg
    assert f"request_header" not in msg
    assert f"request_method" not in msg
    assert f"request_param" not in msg
    assert f"request_url" not in msg


def test_formats_response():
    msg = logger.format(request=mock_request(), response=mock_response())
    assert parseable(msg) is True
    assert f"[\"response_code\",\"200\"]" in msg
    assert f"response_body" not in msg
    assert f"response_header" not in msg


def test_formats_response_with_body():
    msg = logger.format(request=mock_request(), response=mock_response_with_html(), response_body=MOCK_HTML2)
    assert parseable(msg) is True
    assert f"[\"response_body\",\"{MOCK_HTML2}\"]" in msg
    assert f"[\"response_code\",\"200\"]" in msg
    assert f"[\"response_header:content-type\",\"text/html; charset=utf-8\"]" in msg


def test_formats_response_with_empty_body():
    msg = logger.format(request=mock_request(), response=mock_response_with_html(), response_body='')
    assert parseable(msg) is True
    assert f"[\"response_code\",\"200\"]" in msg
    assert f"[\"response_header:content-type\",\"text/html; charset=utf-8\"]" in msg
    assert f"response_body" not in msg


def test_formats_response_with_missing_details():
    msg = logger.format(request=mock_request(), response=HttpResponseImpl())
    assert parseable(msg) is True
    assert f"response_body" not in msg
    assert f"response_code" not in msg
    assert f"response_header" not in msg
