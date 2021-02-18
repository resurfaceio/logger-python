import time

from usagelogger import HttpLogger, HttpMessage

from .requests_adapter import BaseMiddleware


class ResurfaceLoggerMiddleware(BaseMiddleware):
    def __init__(self, url, rules, *args, **kwargs):
        self.logger = HttpLogger(url=url, rules=rules)

    def after_build_response(self, req, resp, response):

        start_time = time.time()
        interval = str((time.time() - start_time) * 1000)

        HttpMessage.send(
            self.logger, request=req, response=response, interval=interval,
        )
        return response
