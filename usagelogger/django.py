# coding: utf-8
# © 2016-2021 Resurface Labs Inc.

import time

from django.conf import settings

from usagelogger import HttpLogger, HttpMessage


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

    def __call__(self, request):
        start_time = time.time()
        response = self.get_response(request)
        interval = str((time.time() - start_time) * 1000)

        HttpMessage.send(
            self.logger,
            request=request,
            response=response,
            interval=interval,
        )
        return response
