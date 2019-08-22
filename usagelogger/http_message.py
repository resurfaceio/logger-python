# coding: utf-8
# © 2016-2019 Resurface Labs Inc.

from typing import List, Optional
from usagelogger import HttpRequestImpl, HttpResponseImpl


class HttpMessage(object):

    @classmethod
    def build(cls, request: HttpRequestImpl, response: HttpResponseImpl,
              response_body: Optional[str] = None, request_body: Optional[str] = None):
        message: List[List[str]] = []
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
            message.append(["request_header:{0}".format(k).lower(), v])

    @classmethod
    def _append_request_params(cls, message: List[List[str]],
                               request: HttpRequestImpl) -> None:
        # todo read from params dict
        return

    @classmethod
    def _append_response_headers(cls, message: List[List[str]],
                                 response: HttpResponseImpl) -> None:
        for k, v in response.get_headers():
            message.append(["response_header:{0}".format(k).lower(), v])
