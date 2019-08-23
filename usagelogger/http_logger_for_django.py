# coding: utf-8
# © 2016-2019 Resurface Labs Inc.


class HttpLoggerForDjango:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        print('HttpLoggerForDjango --------------------------------------------------------------------------------')
        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response
