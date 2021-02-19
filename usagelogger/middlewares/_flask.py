# coding: utf-8
# © 2016-2021 Resurface Labs Inc.

import itertools
import time

# Required to be loaded early to avoid hitting deadlock situation when processing requests
# See http://code.google.com/p/modwsgi/wiki/ApplicationIssues (at the bottom, under Non Blocking Module Imports)
from werkzeug.wrappers import Request

from usagelogger import HttpLogger, HttpMessage


class dotdict(dict):
    """dot.notation access to dictionary attributes"""

    __getattr__ = dict.get
    __setattr__ = dict.__setitem__  # type: ignore
    __delattr__ = dict.__delitem__  # type: ignore


class HttpLoggerForFlask:
    def __init__(self, app, url, rules):
        self.app = app
        self.logger = HttpLogger(url=url, rules=rules)
        self.request_counter = itertools.count()  # Threadsafe counter
        self.start_time: int = 0
        self.interval: float = 0.0
        self.response = None
        self.response_headers = None
        self.status = None

    def start_response(self, status, response_headers):
        self.start_time = time.time()
        self.status = status
        self.response_headers = response_headers

    def finish_response(self, response):
        self.interval = 1000.0 * (time.time() - self.start_time)
        self.response = response
        return response

    def __call__(self, environ, start_response):
        def _start_response(status, response_headers, *args):
            # Capture status and response_headers for later processing
            self.start_response(status, response_headers)
            return start_response(status, response_headers, *args)

        response_chunks = self.finish_response(self.app(environ, _start_response))

        request = Request(environ)

        res = dotdict(
            {
                "headers": dict(self.response_headers),
                "status_code": self.status,
                "content": self.response,
            }
        )

        HttpMessage.send(
            self.logger, request=request, response=res, interval=self.interval,
        )

        return response_chunks


if __name__ == "__main__":
    from flask import Flask

    app = Flask(__name__)

    app.wsgi_app = HttpLoggerForFlask(  # type: ignore
        app=app.wsgi_app, url="http://localhost:4001/message", rules="include debug"
    )

    @app.route("/home/")
    def home():
        return "hello home this is me"

    app.run(debug=True)
