# coding: utf-8
# © 2016-2024 Graylog, Inc.

from tests.test_helper import MOCK_JSON, MOCK_URL
from usagelogger import HttpResponseImpl


def test_body():
    r = HttpResponseImpl()
    r.body = MOCK_JSON
    assert r.body == MOCK_JSON


def test_headers():
    r = HttpResponseImpl()
    r.headers["ABC"] = "123"
    assert len(r.headers) == 1
    assert r.headers["ABC"] == "123"


def test_url():
    r = HttpResponseImpl()
    r.url = MOCK_URL
    assert r.url == MOCK_URL
