# coding: utf-8
# © 2016-2021 Resurface Labs Inc.

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
        self.logger = HttpLogger(url=__read_settings__('url'), rules=__read_settings__('rules'))

    def __call__(self, request):
        response = self.get_response(request)
        status = response.status_code
        if (status < 300 or status == 302) and HttpLogger.is_string_content_type(response['Content-Type']):
            HttpMessage.send(self.logger, request=request, response=response)  # todo add timing details
        return response
