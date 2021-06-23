import time
from typing import Optional

from aiohttp import web

from usagelogger import HttpLogger, HttpMessage
from usagelogger.http_request_impl import HttpRequestImpl
from usagelogger.http_response_impl import HttpResponseImpl


def HttpLoggerForAIOHTTP(url: Optional[str] = None, rules: Optional[str] = None):
    logger = HttpLogger(url=url, rules=rules)

    @web.middleware
    async def resurface_logger_middleware(request, handler):
        start_time = time.time()
        response = await handler(request)

        interval = str((time.time() - start_time) * 1000)
        data__: bytes = await request.read()

        HttpMessage.send(
            logger,
            request=HttpRequestImpl(
                url=str(request.url),
                headers=request.headers,
                params=request.query,
                method=request.method,
                body=data__.decode(),
            ),
            response=HttpResponseImpl(
                status=response.status,
                headers=response.headers,
                body=response.body.decode("utf8"),
            ),
            interval=interval,
        )

        return response

    return resurface_logger_middleware
