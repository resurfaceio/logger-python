"""The following code is adapted from git@github.com:jmcarp/requests-middleware.git under the MIT license.

Copyright 2014 Joshua Carp

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE."""


from requests import Response
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager
from requests.packages.urllib3.response import HTTPResponse


class MiddlewareHTTPAdapter(HTTPAdapter):
    """An HTTPAdapter onto which :class:`BaseMiddleware <BaseMiddleware>`
    can be registered. Middleware methods are called in the order of
    registration. Note: contrib that expose actions called during adapter
    initialization must be passed to `__init__` rather than `register`, else
    those actions will not take effect.
    :param list middlewares: List of :class:`BaseMiddleware <BaseMiddleware>`
        objects
    """

    def __init__(self, middlewares=None, *args, **kwargs):
        self.middlewares = middlewares or []
        super(MiddlewareHTTPAdapter, self).__init__(*args, **kwargs)

    def register(self, middleware):
        """Add a middleware to the middleware stack.
        :param BaseMiddleware middleware: The middleware object
        """
        self.middlewares.append(middleware)

    def init_poolmanager(self, connections, maxsize, block=False):
        """Assemble keyword arguments to be passed to `PoolManager`.
        Middlewares are called in reverse order, so if multiple middlewares
        define conflicting arguments, the higher-priority middleware will take
        precedence. Note: Arguments are passed directly to `PoolManager` and
        not to the superclass `init_poolmanager` because the superclass method
        does not currently accept **kwargs.
        """
        kwargs = {}
        for middleware in self.middlewares[::-1]:
            value = middleware.before_init_poolmanager(connections, maxsize, block)
            kwargs.update(value or {})

        self._pool_connections = connections
        self._pool_maxsize = maxsize
        self._pool_block = block

        self.poolmanager = PoolManager(
            num_pools=connections, maxsize=maxsize, block=block, **kwargs
        )

    def send(self, request, *args, **kwargs):
        """Send the request. If any middleware in the stack returns a `Response`
        or `HTTPResponse` value from its `before_send` method, short-circuit;
        else delegate to `HTTPAdapter::send`.
        :param request: The :class:`PreparedRequest <PreparedRequest>`
            being sent.
        :returns: The :class:`Response <Response>` object.
        """
        for middleware in self.middlewares:
            value = middleware.before_send(request, **kwargs)
            if isinstance(value, Response):
                return value
            if isinstance(value, HTTPResponse):
                return self.build_response(request, value)
            if value:
                raise ValueError(
                    'Middleware "before_send" methods must return '
                    "`Response`, `HTTPResponse`, or `None`"
                )
        return super(MiddlewareHTTPAdapter, self).send(request, *args, **kwargs)

    def build_response(self, req, resp):
        """Build the response. Call `HTTPAdapter::build_response`, then pass
        the response object to the `after_build_response` method of each
        middleware in the stack, in reverse order.
        :param req: The :class:`PreparedRequest <PreparedRequest>` used to
            generate the response.
        :param resp: The urllib3 response object.
        :returns: The :class:`Response <Response>` object.
        """
        for middleware in reversed(self.middlewares):
            req, resp = middleware.before_build_response(req, resp)
        response = super(MiddlewareHTTPAdapter, self).build_response(req, resp)
        for middleware in reversed(self.middlewares):
            response = middleware.after_build_response(req, resp, response)
        return response
