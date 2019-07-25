# coding: utf-8
# © 2016-2019 Resurface Labs Inc.
from typing import List, Optional


class HttpMessage(object):

    @classmethod
    def build(cls, request, response,
              response_body: Optional[str] = None,
              request_body: Optional[str] = None):
        message: List[List[str]] = [['request_method', request.get_method()],
                                    ['request_url', request.get_full_url()],
                                    ['response_code', response.getcode()]]
        cls._append_request_headers(message, request)
        cls._append_request_params(message, request)
        cls._append_response_headers(message, response)

        if request_body is not None and request_body != '':
            message.append(['request_body', request_body])

        final_response_body = response_body if \
            response_body is not None and response_body != '' else \
            response.read()
        if final_response_body != '':
            message.append(['response_body', final_response_body])

        return message

    @classmethod
    def _append_request_headers(cls, message: List[List[str]],
                                request) -> None:
        next(message.append(["request_header:{0}".format(item[0]).lower(),
                             item[1]]) for item in request.header_items())

    @classmethod
    def _append_request_params(cls, message: List[List[str]],
                               request) -> None:
        pass

    @classmethod
    def _append_response_headers(cls, message: List[List[str]],
                                 response) -> None:
        next(message.append(["response_header:{0}".format(item[0]).lower(),
                             item[1]]) for item in response.getheaders())
