import asyncio
import time
import typing
from typing import List, Optional

from starlette.requests import Request
from starlette.responses import Response, StreamingResponse
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from usagelogger import HttpLogger, HttpMessage, HttpRequestImpl, HttpResponseImpl
from usagelogger.utils.multipart_decoder import decode_multipart


class HttpLoggerForFastAPI:
    def __init__(
        self, app: ASGIApp, url: Optional[str] = None, rules: Optional[str] = None
    ):
        self.app = app
        self.logger = HttpLogger(url=url, rules=rules)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        request = Request(scope, receive=receive)
        response = await self.call_next(request)

        start_time = time.time()

        stored_response_chunks: List[bytes] = []
        # async for chunk in response.body_iterator:
        #     stored_response_chunks.append(chunk)
        # 'content-length': '25'
        interval = str((time.time() - start_time) * 1000)
        data__: bytes = await request.body()
        is_multipart = "multipart" in request.headers.get("content-type")
        HttpMessage.send(
            self.logger,
            request=HttpRequestImpl(
                url=str(request.url),
                headers=dict(request.headers),
                params=dict(request.query_params),
                method=request.method,
                body=decode_multipart(data__) if is_multipart else data__.decode(),
            ),
            response=HttpResponseImpl(
                status=response.status_code,
                headers=dict(response.headers),
                body="" if stored_response_chunks else None,
            ),
            interval=interval,
        )

        response.raw_headers = self.headers

        await response(scope, receive, send)

    async def call_next(self, request: Request) -> Response:
        loop = asyncio.get_event_loop()
        queue: "asyncio.Queue[typing.Optional[Message]]" = asyncio.Queue()

        scope = request.scope
        receive = request.receive
        send = queue.put

        async def coro() -> None:
            try:
                await self.app(scope, receive, send)
            finally:
                await queue.put(None)

        task = loop.create_task(coro())
        message = await queue.get()
        if message is None:
            task.result()
            raise RuntimeError("No response returned.")
        assert message["type"] == "http.response.start"

        async def body_stream() -> typing.AsyncGenerator[bytes, None]:
            while True:
                message = await queue.get()
                if message is None:
                    break
                assert message["type"] == "http.response.body"
                yield message.get("body", b"")
            task.result()

        response = StreamingResponse(
            status_code=message["status"], content=body_stream()
        )
        self.headers = message["headers"]
        response.raw_headers = message["headers"]
        return response
