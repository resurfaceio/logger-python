import time

from usagelogger import HttpLogger, HttpMessage

from .requests_adapter import BaseMiddleware


class ResurfaceLoggerMiddleware(BaseMiddleware):
    def __init__(self, url, rules, *args, **kwargs):
        self.logger = HttpLogger(url=url, rules=rules)
        self.start_time = 0

    def before_build_response(self, req, resp):
        """Called before `HTTPAdapter::build_response`. Optionally modify the
        returned `PreparedRequest` and `HTTPResponse` objects.
        :param req: The `PreparedRequest` used to generate the response.
        :param resp: The urllib3 response object.
        :returns: Tuple of potentially modified (req, resp)
        """

        self.start_time = time.time()
        return req, resp

    def after_build_response(self, req, resp, response):

        interval = str((time.time() - self.start_time) * 1000)
        HttpMessage.send(
            self.logger, request=req, response=response, interval=interval,
        )
        return response
