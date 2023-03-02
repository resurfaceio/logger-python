# coding: utf-8
# © 2016-2023 Resurface Labs Inc.
import time

from django.conf import settings
from django.http.request import RawPostDataException

from usagelogger import HttpLogger, HttpMessage, HttpRequestImpl, HttpResponseImpl
from usagelogger.utils.multipart_decoder import decode_multipart


def __read_settings__(key):
    try:
        return settings.USAGELOGGER[key]
    except Exception:
        return None


class HttpLoggerForDjango:
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = HttpLogger(
            url=__read_settings__("url"), rules=__read_settings__("rules")
        )

    def prepare_request_body(self, request, response=None):

        is_multipart = request.content_type == "multipart/form-data"

        try:
            if response is None:
                if is_multipart:
                    body = decode_multipart(request.body)
                else:
                    body = request.body.decode()
            else:
                body = str(response.renderer_context["request"].data)
        except (RawPostDataException, AttributeError):
            body = None

        return body

    def __call__(self, request):
        start_time = time.time()
        request_body = self.prepare_request_body(request)
        response = self.get_response(request)
        interval = str((time.time() - start_time) * 1000)
        method = request.method

        if request_body is None:
            request_body = self.prepare_request_body(request, response)

        try:
            if response.content:
                response_body = str(response.content.decode("utf8"))
            else:
                response_body = None
        except AttributeError:
            response_body = None

        HttpMessage.send(
            self.logger,
            request=HttpRequestImpl(
                method=method,
                url=str(request.build_absolute_uri()),
                headers=request.headers,
                params=request.POST if method == "POST" else request.GET,
                body=request_body,
                remote_addr=request.META.get("HTTP_X_FORWARDED_FOR")
                or request.META.get("REMOTE_ADDR")
                or None,
            ),
            response=HttpResponseImpl(
                status=response.status_code,
                body=response_body,
                headers=response,
            ),
            interval=interval,
        )
        return response
