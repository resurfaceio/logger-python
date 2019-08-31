# coding: utf-8
# © 2016-2019 Resurface Labs Inc.

from usagelogger import HttpLogger


class HttpLoggerForDjango:
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = HttpLogger()  # todo some way to set url & rules?

    def __call__(self, request):
        response = self.get_response(request)
        status = response.status_code
        if (status < 300 or status == 302) and HttpLogger.is_string_content_type(response['Content-Type']):
            self.logger.log(request=request, response=response)
        return response
