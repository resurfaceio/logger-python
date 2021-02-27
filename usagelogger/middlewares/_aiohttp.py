import time

from aiohttp import web

from usagelogger import HttpLogger, HttpMessage


def HttpLoggerForAIOHTTP(url, rules):
    logger = HttpLogger(url=url, rules=rules)

    @web.middleware
    async def resurface_logger_middleware(request, handler):
        start_time = time.time()
        response = await handler(request)
        interval = str((time.time() - start_time) * 1000)

        HttpMessage.send(
            logger, request=request, response=response, interval=interval,
        )

        return response

    return resurface_logger_middleware
