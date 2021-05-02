from time import time
from typing import Optional

from usagelogger import HttpLogger, HttpMessage
from usagelogger.http_request_impl import HttpRequestImpl
from usagelogger.http_response_impl import HttpResponseImpl


class HTTPLoggerForTornado:
    def __init__(self, url: Optional[str] = None, rules: Optional[str] = None) -> None:
        self.logger = HttpLogger(url=url, rules=rules)
        self.interval = None

    @staticmethod
    def parse_request(handler):
        request_headers: dict = {}
        if handler.request.headers:
            request_headers = dict(handler.request.headers.get_all())

        request_body: bytes = b""
        if handler.request.body:
            request_body = handler.request.body
        return request_body, request_headers

    @staticmethod
    def parse_response(handler):
        response_headers: dict = {}
        if handler._headers:
            response_headers = dict(handler._headers.get_all())
        response_body = None

        return response_headers, response_body

    @staticmethod
    def fix_arguments(args):
        params = {}
        for k, v in args.items():
            params[k] = v[0].decode()
        return params

    @staticmethod
    def get_request_response_time(handler):
        request_time = time()
        response_time = request_time + handler.request.request_time()
        interval = 1000.0 * abs(request_time - response_time)
        return interval

    def log(self, handler):

        request_body, request_header = self.parse_request(handler)
        response_headers, response_body = self.parse_response(handler)

        HttpMessage.send(
            self.logger,
            request=HttpRequestImpl(
                url=handler.request.full_url(),
                headers=request_header,
                params=self.fix_arguments(handler.request.arguments),
                method=handler.request.method,
                body=request_body.decode(),
            ),
            response=HttpResponseImpl(
                status=handler._status_code,
                headers=response_headers,
                body=response_body,
            ),
            interval=self.get_request_response_time(handler),
        )
