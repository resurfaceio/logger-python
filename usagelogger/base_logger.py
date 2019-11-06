# coding: utf-8
# © 2016-2019 Resurface Labs Inc.

import http.client
import os
import socket
from typing import Dict, List, Optional
from urllib.parse import urlsplit

import usagelogger  # just to read version
from usagelogger.usage_loggers import UsageLoggers


class BaseLogger(object):
    """Basic usage logger to embed or extend."""

    def __init__(self, agent: str,
                 enabled: Optional[bool] = True,
                 queue: Optional[List[str]] = None,
                 url: Optional[str] = None,
                 skip_compression: Optional[bool] = False,
                 skip_submission: Optional[bool] = False) -> None:

        self.agent = agent
        self.host = self.host_lookup()
        self.skip_compression = skip_compression
        self.skip_submission = skip_submission
        self.version = self.version_lookup()

        # read provided options
        if url is None: url = UsageLoggers.url_by_default()

        # set options in priority order
        self._enabled = enabled
        self._queue = queue if isinstance(queue, list) else None
        if self._queue is not None:
            self._url = None
        elif url is not None and isinstance(url, str):
            try:
                if urlsplit(url).scheme in {'http', 'https'}:
                    self._url_scheme: str = urlsplit(url).scheme
                    self._url = url
                else:
                    raise TypeError('incorrect URL scheme')
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
    def enableable(self) -> bool:
        return self._enableable

    @property
    def enabled(self) -> bool:
        return self._enabled and UsageLoggers.is_enabled()

    @property
    def queue(self) -> List[str]:
        return self._queue

    def submit(self, msg: Optional[str]) -> bool:
        """Submits JSON message to intended destination."""

        if msg is None or self.skip_submission is True or self.enabled is False:
            return True
        elif self._queue is not None:
            self._queue.append(msg)
            return True
        else:
            try:
                # todo implement compression (Clubhouse #49)
                url_parser = urlsplit(self.url)
                hostname = url_parser.hostname  # todo cache this (Clubhouse #49)
                url_path = url_parser.path + url_parser.query  # todo cache this (Clubhouse #49)

                headers: Dict[str, str] = {'Content-Type': 'application/json'}

                if self._url_scheme == "http":
                    conn = http.client.HTTPConnection(hostname)
                else:
                    conn = http.client.HTTPSConnection(hostname)

                conn.request("POST", url_path, msg, headers)
                response = conn.getresponse()
                conn.close()  # todo keep connection alive? (Clubhouse #49)

                return response.status == 204

            # http errors
            except (http.client.HTTPException, IOError, OSError):
                return False
            # JSON errors
            except (OverflowError, TypeError, ValueError):
                return False

    @property
    def url(self) -> str:
        return self._url

    @staticmethod
    def host_lookup() -> str:
        dyno = os.getenv('DYNO')
        if dyno is not None: return dyno
        try:
            return socket.gethostname()
        except:
            return 'unknown'

    @staticmethod
    def version_lookup() -> str:
        return usagelogger.__version__
