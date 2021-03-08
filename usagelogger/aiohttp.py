import time

from aiohttp import web

from usagelogger import HttpLogger, HttpMessage
from usagelogger.http_request_impl import HttpRequestImpl
from usagelogger.http_response_impl import HttpResponseImpl


def HttpLoggerForAIOHTTP(url, rules):
    logger = HttpLogger(url=url, rules=rules)

    @web.middleware
    async def resurface_logger_middleware(request, handler):
        start_time = time.time()
        response = await handler(request)

        interval = str((time.time() - start_time) * 1000)

        HttpMessage.send(
            logger,
            request=HttpRequestImpl(
                url=str(request.url),
                headers=request.headers,
                params=request.query,
                method=request.method,
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
