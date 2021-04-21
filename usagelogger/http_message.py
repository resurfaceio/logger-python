# coding: utf-8
# © 2016-2021 Resurface Labs Inc.

from re import match
from time import time
from typing import List, Optional
from urllib import parse

from usagelogger import HttpLogger


class HttpMessage(object):
    @classmethod
    def send(
        cls,
        logger: HttpLogger,
        request,
        response,
        response_body: Optional[str] = None,
        request_body: Optional[str] = None,
        now=None,
        interval=None,
    ) -> None:  # TODO: missing type hints

        if not logger.enabled:
            return

        # copy details from request & response
        message: List[List[str]] = cls.build(
            request, response, response_body, request_body
        )

        # copy details from active session
        if logger.rules.copy_session_field:
            session_dict = logger.conn.__dict__
            if session_dict:
                for r in logger.rules.copy_session_field:
                    for d0 in session_dict:
                        if match(r.param1, d0):
                            d1 = session_dict[d0]
                            if d0 == "cookies":
                                d1 = d1.get_dict()
                            if isinstance(d1, dict):
                                d1 = {k: v for k, v in d1.items() if v}
                            message.append([f"session_field:{d0.lower()}", str(d1)])

        # add timing details
        message.append(
            ["now", str(now) if now is not None else str(round(time() * 1000))]
        )
        if interval is not None:
            message.append(["interval", interval])

        logger.submit_if_passing(message)

    @classmethod
    def build(
        cls,
        request,
        response,
        response_body: Optional[str] = None,
        request_body: Optional[str] = None,
    ) -> List[List[str]]:

        message: List[List[str]] = []

        if request.__class__.__name__ == "WSGIRequest":
            message = []
            if request.method:
                message.append(["request_method", request.method])
            url = request.build_absolute_uri()
            if url:
                message.append(["request_url", url])
            if response.status_code:
                message.append(["response_code", str(response.status_code)])
            for k, v in request.headers.items():
                message.append([f"request_header:{k}".lower(), v])
            message.append(["request_body", request.body.decode()])
            if request.method == "GET":
                for k, v in request.GET.items():
                    message.append([f"request_param:{k}".lower(), v])
            elif request.method == "POST":
                for k, v in request.POST.items():
                    message.append([f"request_param:{k}".lower(), v])
            for k, v in response.items():
                message.append([f"response_header:{k}".lower(), v])
            message.append(["response_body", response.content.decode("utf8")])

        elif request.__class__.__name__ == "HttpRequestImpl":
            message = []
            if request.method:
                message.append(["request_method", request.method])
            if request.url:
                message.append(["request_url", request.url])
            if response.status:
                message.append(["response_code", str(response.status)])
            for k, v in request.headers.items():
                message.append([f"request_header:{k}".lower(), v])
            for k, v in request.params.items():
                message.append([f"request_param:{k}".lower(), v])
            for k, v in response.headers.items():
                message.append([f"response_header:{k}".lower(), v])
            final_request_body = (
                request_body if (request_body is not None) else request.body
            )
            if final_request_body:
                message.append(["request_body", final_request_body])
            final_response_body = (
                response_body if (response_body is not None) else response.body
            )
            if final_response_body:
                message.append(["response_body", final_response_body])

        elif request.__class__.__name__ == "PreparedRequest":
            message = []
            if request.method:
                message.append(["request_method", request.method])

            url = str(request.url)
            if url:
                message.append(["request_url", url])
            if response.status_code:
                message.append(["response_code", str(response.status_code)])
            for k, v in request.headers.items():
                message.append([f"request_header:{k}".lower(), v])

            parsed_url = parse.parse_qs(parse.urlparse(url).query)
            for k, v in parsed_url.items():
                message.append([f"request_param:{k}".lower(), v[0]])
            if request.body:
                body_ = request.body
                if type(body_) == bytes:
                    body_ = body_.decode()
                message.append(["request_body", body_])

            for k, v in response.headers.items():
                message.append([f"response_header:{k}".lower(), v])
            message.append(["response_body", response.content.decode("utf8")])

        return message
