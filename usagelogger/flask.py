# coding: utf-8
# © 2016-2021 Resurface Labs Inc.

import time
from typing import Dict, Iterable, List, Optional, Tuple
from urllib import parse

from werkzeug.wrappers import Request
from werkzeug.wsgi import ClosingIterator

from usagelogger import HttpLogger, HttpMessage, HttpRequestImpl, HttpResponseImpl


class HttpLoggerForFlask:
    def __init__(self, app, url: Optional[str] = None, rules: Optional[str] = None):
        self.app = app
        self.logger = HttpLogger(url=url, rules=rules)
        self.start_time: float = 0.0
        self.interval: float = 0.0
        self.response: List[bytes] = []
        self.response_headers: Iterable[Tuple[str, str]] = []
        self.status: Optional[int] = None

    def start_response(
        self, status: str, response_headers: Iterable[Tuple[str, str]]
    ) -> None:
        self.start_time = time.time()
        self.status = int(status.split(" ")[0])
        self.response_headers = response_headers

    def finish_response(self, response: ClosingIterator) -> List[bytes]:
        self.interval = 1000.0 * (time.time() - self.start_time)
        new_response_chunks = []
        stored_response_chunks = []
        for line in response:
            new_response_chunks.append(line)
            stored_response_chunks.append(line)
        self.response = stored_response_chunks
        return stored_response_chunks

    def __call__(self, environ, start_response) -> ClosingIterator:
        def _start_response(status, response_headers, *args):
            self.start_response(status, response_headers)
            return start_response(status, response_headers, *args)

        response_chunks = self.finish_response(self.app(environ, _start_response))
        request = Request(environ)

        parased_raw_params: Dict[str, List[str]] = parse.parse_qs(
            parse.urlparse(request.url).query
        )
        params: Dict[str, str] = {}

        # Type correction
        for k, v in parased_raw_params.items():
            params[k] = v[0]

        HttpMessage.send(
            self.logger,
            request=HttpRequestImpl(
                method=request.method,
                url=str(request.url),
                headers=dict(request.headers),
                params=params,
            ),
            response=HttpResponseImpl(
                status=self.status,
                body=str(self.response[0].decode()) if self.response else None,
                headers=dict(self.response_headers),
            ),
            interval=str(self.interval),
        )
        return ClosingIterator(response_chunks)
