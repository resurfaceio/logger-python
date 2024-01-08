# coding: utf-8
# © 2016-2024 Graylog, Inc.

from tests.test_helper import MOCK_JSON, MOCK_URL
from usagelogger import HttpRequestImpl


def test_body():
    r = HttpRequestImpl()
    r.body = MOCK_JSON
    assert r.body == MOCK_JSON


def test_headers():
    r = HttpRequestImpl()
    r.headers["ABC"] = "123"
    assert len(r.headers) == 1
    assert r.headers["ABC"] == "123"


def test_method():
    r = HttpRequestImpl()
    r.method = "POST"
    assert r.method == "POST"


def test_params():
    r = HttpRequestImpl()
    r.params["ABC"] = "123"
    assert len(r.params) == 1
    assert r.params["ABC"] == "123"


def test_url():
    r = HttpRequestImpl()
    r.url = MOCK_URL
    assert r.url == MOCK_URL
