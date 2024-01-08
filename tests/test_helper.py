# coding: utf-8
# © 2016-2024 Graylog, Inc.

import json

from usagelogger import HttpRequestImpl, HttpResponseImpl

DEMO_URL = "https://demo.resurface.io"

MOCK_AGENT = "helper.py"

MOCK_HTML = "<html>Hello World!</html>"

MOCK_HTML2 = "<html>Hola Mundo!</html>"

MOCK_HTML3 = "<html>1 World 2 World Red World Blue World!</html>"

MOCK_HTML4 = "<html>1 World\n2 World\nRed World \nBlue World!\n</html>"

MOCK_HTML5 = """<html>
<input type="hidden">SECRET1</input>
<input class='foo' type="hidden">
SECRET2
</input>
</html>"""

MOCK_JSON = '{ "hello" : "world" }'

MOCK_JSON_ESCAPED = '{ \\"hello\\" : \\"world\\" }'

MOCK_NOW = 1455908640173

MOCK_QUERY_STRING = "foo=bar"

MOCK_URL = "http://localhost:3000/index.html"

MOCK_URLS_DENIED = [
    DEMO_URL + "/noway3is5this1valid2",
    "https://www.noway3is5this1valid2.com/",
]

MOCK_URLS_INVALID = [
    "",
    "noway3is5this1valid2",
    "ftp:\\www.noway3is5this1valid2.com/",
    "urn:ISSN:1535–3613",
]

MOCK_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:26.0) Gecko/20100101 Firefox/26.0"
)


def mock_request():
    r = HttpRequestImpl()
    r.method = "GET"
    r.url = MOCK_URL
    return r


def mock_request_with_json():
    r = HttpRequestImpl()
    r.method = "POST"
    r.url = f"{MOCK_URL}?{MOCK_QUERY_STRING}"
    r.headers["Content-Type"] = "Application/JSON"
    r.params["message"] = MOCK_JSON
    r.body = MOCK_JSON
    return r


def mock_request_with_json2():
    r = mock_request_with_json()
    r.headers["ABC"] = "123"
    r.headers["A"] = "1, 2"
    r.params["ABC"] = "123, 234"
    return r


def mock_response():
    r = HttpResponseImpl()
    r.status = 200
    return r


def mock_response_with_html():
    r = mock_response()
    r.headers["Content-Type"] = "text/html; charset=utf-8"
    r.body = MOCK_HTML
    return r


def parseable(msg):
    if (
        (msg is None)
        or not msg.startswith("[")
        or not msg.endswith("]")
        or ("[]" in msg)
        or (",," in msg)
    ):
        return False
    try:
        json.loads(msg)
        return True
    except Exception:
        return False


def test_good_json():
    assert parseable("[\n]") is True
    assert parseable("[\n\t\n]") is True
    assert parseable('["A"]') is True
    assert parseable('["A","B"]') is True


def test_invalid_json():
    assert parseable(None) is False
    assert parseable("") is False
    assert parseable(" ") is False
    assert parseable("\n\n\n\n") is False
    assert parseable("1234") is False
    assert parseable("archer") is False
    assert parseable('"sterling archer"') is False
    assert parseable(",,") is False
    assert parseable("[]") is False
    assert parseable("[,,]") is False
    assert parseable('["]') is False
    assert parseable("[:,]") is False
    assert parseable(",") is False
    assert parseable("exact words") is False
    assert parseable("his exact words") is False
    assert parseable('"exact words') is False
    assert parseable('his exact words"') is False
    assert parseable('"hello":"world" }') is False
    assert parseable('{ "hello":"world"') is False
    assert parseable('{ "hello world"}') is False
