# coding: utf-8
# © 2016-2019 Resurface Labs Inc.

from usagelogger import HttpLogger


class HttpLoggerForDjango:
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = HttpLogger()  # todo some way to set url & rules?

    def __call__(self, request):
        response = self.get_response(request)
        self.logger.log(request=request, response=response)  # todo filter by response code & content-type
        return response
