# coding: utf-8
# © 2016-2021 Resurface Labs Inc.

from time import time
from typing import List, Optional

from usagelogger import HttpLogger


class HttpMessage(object):

    @classmethod
    def send(cls, logger: HttpLogger, request, response, response_body: Optional[str] = None,
             request_body: Optional[str] = None, now=None, interval=None) -> None:  # todo missing type hints

        if not logger.enabled: return

        # copy details from request & resonse
        message = cls.build(request, response, response_body, request_body)

        # todo copy details from active session

        # add timing details
        message.append(['now', str(now) if now is not None else str(round(time() * 1000))])
        if interval is not None: message.append(['interval', interval])

        logger.submit_if_passing(message)

    @classmethod
    def build(cls, request, response, response_body: Optional[str] = None,
              request_body: Optional[str] = None) -> Optional[List[List[str]]]:

        message: Optional[List[List[str]]] = None

        if request.__class__.__name__ == "WSGIRequest":
            message = []
            if request.method: message.append(['request_method', request.method])
            url = request.build_absolute_uri()
            if url: message.append(['request_url', url])
            if response.status_code: message.append(['response_code', str(response.status_code)])
            for k, v in request.headers.items(): message.append([f"request_header:{k}".lower(), v])
            if request.method == "GET":
                for k, v in request.GET.items(): message.append([f"request_param:{k}".lower(), v])
            elif request.method == "POST":
                for k, v in request.POST.items(): message.append([f"request_param:{k}".lower(), v])
            for k, v in response.items(): message.append([f"response_header:{k}".lower(), v])
            message.append(['response_body', response.content.decode('utf8')])

        elif request.__class__.__name__ == "HttpRequestImpl":
            message = []
            if request.method: message.append(['request_method', request.method])
            if request.url: message.append(['request_url', request.url])
            if response.status: message.append(['response_code', str(response.status)])
            for k, v in request.headers.items(): message.append([f"request_header:{k}".lower(), v])
            for k, v in request.params.items(): message.append([f"request_param:{k}".lower(), v])
            for k, v in response.headers.items(): message.append([f"response_header:{k}".lower(), v])
            final_request_body = request_body if (request_body is not None) else request.body
            if final_request_body: message.append(['request_body', final_request_body])
            final_response_body = response_body if (response_body is not None) else response.body
            if final_response_body: message.append(['response_body', final_response_body])

        return message
