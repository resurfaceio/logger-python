# coding: utf-8
# © 2016-2021 Resurface Labs Inc.

import re
import time

from django.conf import settings
from django.http.request import RawPostDataException

from usagelogger import HttpLogger, HttpMessage, HttpRequestImpl, HttpResponseImpl


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

    def prepare_request(self, request, response):
        RE_PATTERN = r'(?<=; filename=")(.*?)"\\r\\nContent-Type: (.*?)\\r\\n(.*?)((-+)([a-zA-Z0-9_.-]+)\\r\\nContent-Disposition:)'  # noqa
        RE_REPLACE_TO = r'\1"\\r\\nContent-Type: \2\\r\\n\\r\\n<file-data>\\r\\n\4'
        request.encoding = "utf-8"
        is_multipart = request.content_type == "multipart/form-data"

        try:
            if is_multipart:
                request._rsf_body = (
                    re.sub(
                        pattern=RE_PATTERN,
                        repl=RE_REPLACE_TO,
                        string="%r" % request.body,
                    )
                    .encode()
                    .decode("unicode_escape")
                )
            else:
                request._rsf_body = request.body.decode(request.encoding)
        except RawPostDataException:
            try:
                request._rsf_body = str(response.renderer_context["request"].data)
            except AttributeError:
                request._rsf_body = request.readlines()

        return request

    def __call__(self, request):
        start_time = time.time()
        response = self.get_response(request)
        interval = str((time.time() - start_time) * 1000)
        method = request.method

        _request = self.prepare_request(request, response)

        HttpMessage.send(
            self.logger,
            request=HttpRequestImpl(
                method=method,
                url=str(request.build_absolute_uri()),
                headers=request.headers,
                params=request.POST if method == "POST" else request.GET,
                body=_request._rsf_body,
            ),
            response=HttpResponseImpl(
                status=response.status_code,
                body=str(response.content.decode("utf8")) if response.content else None,
                headers=response,
            ),
            interval=interval,
        )
        return response
