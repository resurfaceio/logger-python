# © 2016-2019 Resurface Labs Inc.

import json
import usagelogger
from usagelogger.usage_loggers import UsageLoggers
from urllib.parse import urlparse
import urllib.request


class BaseLogger(object):

    def __init__(self, agent, queue=None,
                 url=UsageLoggers.url_by_default(), enabled=True):

        self.agent = agent
        self.version = self._version_lookup()
        self.skip_compression = False
        self.skip_submission = False
        self._enabled = enabled
        self._url = None

        self.queue = queue
        # queue takes precedence over url
        if self.queue is not None:
            self.url = None
        elif url is not None:
            self.url = url
        else:
            self._enabled = False

    def disable(self):
        self._enabled = False

    def enable(self):
        if self.enableable:
            self._enabled = True

    @property
    def enableable(self):
        return self.queue is not None or self.url is not None

    @property
    def enabled(self):
        return self._enabled and UsageLoggers.is_enabled()

    def submit(self, submission):
        if submission is None or self.skip_submission is True or self.enabled is False:
            return True
        elif self.queue is not None:
            self.queue.append(submission)
            return True
        else:
            try:
                # TODO: replace this quick hack
                # TODO: implement compression
                # TODO: add specific exceptions for json parsing or http errors
                body = json.dumps(submission).encode('utf8')
                headers = {'content-type': 'application/json'}
                request = urllib.request.Request(self.url,
                                                 data=body,
                                                 headers=headers)
                response = urllib.request.urlopen(request)
                return response.getcode() == 204

            except Exception:
                return False

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, value):
        # Validate URL
        try:
            # urlparse will return a byte type for a scheme it doesn't
            # understand which will raise a TypeError when compared to a
            # string, so we will raise the same for no http and catch both
            if 'http' not in urlparse(value).scheme:
                raise TypeError('incorrect URL scheme')
            self._url = value
        except TypeError:
            self._url = None
            self._enabled = False

    @staticmethod
    def _version_lookup():
        return usagelogger.__version__
