# © 2016-2019 Resurface Labs Inc.

import json
import usagelogger
from usagelogger.usage_loggers import UsageLoggers
from urllib.parse import urlparse
import urllib.request


class BaseLogger(object):

    def __init__(self, agent, enabled=True, queue=None, url=UsageLoggers.url_by_default(),
                 skip_compression=False, skip_submission=False):

        self.agent = agent
        self.skip_compression = skip_compression
        self.skip_submission = skip_submission
        self.version = self.version_lookup()

        # set options in priority order
        self._enabled = enabled
        self._queue = queue if isinstance(queue, list) else None
        if self.queue is not None:
            self._url = None
        elif url is not None and isinstance(url, str):
            try:
                if 'http' not in urlparse(url).scheme:
                    raise TypeError('incorrect URL scheme')
                self._url = url
            except TypeError:
                self._enabled = False
                self._url = None
        else:
            self._enabled = False
            self._url = None
        self._enableable = self.queue is not None or self.url is not None

    def disable(self):
        self._enabled = False
        return self

    def enable(self):
        if self.enableable:
            self._enabled = True
        return self

    @property
    def enableable(self):
        return self._enableable

    @property
    def enabled(self):
        return self._enabled and UsageLoggers.is_enabled()

    @property
    def queue(self):
        return self._queue

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

    @staticmethod
    def version_lookup():
        return usagelogger.__version__
