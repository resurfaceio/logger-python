# coding: utf-8
# © 2016-2019 Resurface Labs Inc.

from typing import List, Optional
from usagelogger import HttpRequestImpl, HttpResponseImpl


class HttpMessage(object):

    @classmethod
    def build(cls, request: HttpRequestImpl, response: HttpResponseImpl,  # todo not respecting type hints
              response_body: Optional[str] = None, request_body: Optional[str] = None):
        message: List[List[str]] = []
        if request.__class__.__name__ == "WSGIRequest":  # todo reflection cheat
            message.append(['request_method', request.method])
            message.append(['request_url', request.build_absolute_uri()])
            message.append(['response_code', str(response.status_code)])
            for k, v in request.headers.items(): message.append([f"request_header:{k}".lower(), v])
            # todo append request params
            for k, v in response.items(): message.append([f"response_header:{k}".lower(), v])
            # todo append request body and honor body param overrides
            message.append(['response_body', response.content.decode('utf8')])
            # todo honor body param overrides
        else:
            if request.method: message.append(['request_method', request.method])
            if request.request_url: message.append(['request_url', request.request_url])
            if response.status: message.append(['response_code', str(response.status)])
            cls._append_request_headers(message, request)
            cls._append_request_params(message, request)
            cls._append_response_headers(message, response)
            final_request_body = request_body if (request_body is not None) else request.body
            if final_request_body: message.append(['request_body', final_request_body])
            final_response_body = response_body if (response_body is not None) else response.body
            if final_response_body: message.append(['response_body', final_response_body])

        return message

    @classmethod
    def _append_request_headers(cls, message: List[List[str]],
                                request: HttpRequestImpl) -> None:
        for k, v in request.get_headers():
            message.append([f"request_header:{k}".lower(), v])

    @classmethod
    def _append_request_params(cls, message: List[List[str]],
                               request: HttpRequestImpl) -> None:
        # todo read from params dict
        return

    @classmethod
    def _append_response_headers(cls, message: List[List[str]],
                                 response: HttpResponseImpl) -> None:
        for k, v in response.get_headers():
            message.append([f"response_header:{k}".lower(), v])
