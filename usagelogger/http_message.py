# coding: utf-8
# © 2016-2019 Resurface Labs Inc.
from typing import List, Optional
from usagelogger import HttpRequestImpl, HttpResponseImpl


class HttpMessage(object):

    @classmethod
    def build(cls, request: HttpRequestImpl, response: HttpResponseImpl,
              response_body: Optional[str] = None,
              request_body: Optional[str] = None):
        message: List[List[str]] = [['request_method', request.method],
                                    ['request_url', request.request_url],
                                    ['response_code', response.status]]
        cls._append_request_headers(message, request)
        cls._append_request_params(message, request)
        cls._append_response_headers(message, response)

        final_request_body = request_body if request_body else request.body
        if final_request_body:
            message.append(['request_body', final_request_body])

        final_response_body = response_body if response_body else \
            response.body.read()
        if final_response_body:
            message.append(['response_body', final_response_body])

        return message

    @classmethod
    def _append_request_headers(cls, message: List[List[str]],
                                request: HttpRequestImpl) -> None:
        for k, v in request.get_headers():
            message.append(["request_header:{0}".format(k).lower(), v])

    @classmethod
    def _append_request_params(cls, message: List[List[str]],
                               request: HttpRequestImpl) -> None:
        for k, v in request.get_query_params():
            message.append(["request_param:{0}".format(k).lower(), v])

    @classmethod
    def _append_response_headers(cls, message: List[List[str]],
                                 response: HttpResponseImpl) -> None:
        for k, v in response.get_headers():
            message.append(["response_header:{0}".format(k).lower(), v])
