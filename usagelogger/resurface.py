import time
from collections import OrderedDict
from typing import Optional

from requests.cookies import cookiejar_from_dict
from requests.hooks import default_hooks
from requests.models import DEFAULT_REDIRECT_LIMIT
from requests.sessions import Session as RequestsSession
from requests.utils import default_headers

from usagelogger import HttpLogger, HttpMessage

from ._adapter import MiddlewareHTTPAdapter


class Session(RequestsSession):
    def __init__(self, url: Optional[str] = None, rules: Optional[str] = None) -> None:
        self.headers = default_headers()

        self.auth = None

        self.proxies = {}

        self.hooks = default_hooks()

        self.params = {}

        self.stream = False

        self.verify = True

        self.cert = None

        self.max_redirects = DEFAULT_REDIRECT_LIMIT

        self.trust_env = True

        self.cookies = cookiejar_from_dict({})

        self.adapters = OrderedDict()

        middlewares = [ResurfaceHTTPAdapter(url=url, rules=rules)]

        adapter = MiddlewareHTTPAdapter(middlewares)

        self.mount("https://", adapter)
        self.mount("http://", adapter)


class ResurfaceHTTPAdapter:
    def __init__(
        self, url: Optional[str] = None, rules: Optional[str] = None, *args, **kwargs
    ):
        self.logger = HttpLogger(url=url, rules=rules)
        self.start_time = 0

    def before_init_poolmanager(self, connections, maxsize, block=False):
        """Called before `HTTPAdapter::init_poolmanager`. Optionally return a
        dictionary of keyword arguments to `PoolManager`.
        :returns: `dict` of keyword arguments or `None`
        """

    def before_send(self, request, *args, **kwargs):
        """Called before `HTTPAdapter::send`. If a truthy value is returned,
        :class:`MiddlewareHTTPAdapter <MiddlewareHTTPAdapter>` will short-
        circuit the remaining middlewares and `HTTPAdapter::send`, using the
        returned value instead.
        :param request: The `PreparedRequest` used to generate the response.
        :returns: The `Response` object or `None`.
        """

    def before_build_response(self, req, resp):
        self.start_time = time.time()
        return req, resp

    def after_build_response(self, req, resp, response):

        interval = str((time.time() - self.start_time) * 1000)
        HttpMessage.send(
            self.logger,
            request=req,
            response=response,
            interval=interval,
        )
        return response
