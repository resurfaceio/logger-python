# coding: utf-8
# © 2016-2021 Resurface Labs Inc.
import os
import socket
import threading
import zlib
from typing import Dict, List, Optional
from urllib.parse import urlsplit

import requests

import usagelogger  # just to read version
from usagelogger.usage_loggers import UsageLoggers


class BaseLogger:
    """Basic usage logger to embed or extend."""

    def __init__(
        self,
        agent: str,
        enabled: bool = True,
        queue: Optional[List[str]] = None,
        url: Optional[str] = None,
        skip_compression: bool = False,
        skip_submission: bool = False,
        conn=requests.Session(),
    ) -> None:

        self.agent = agent
        self.host = self.host_lookup()
        self.skip_compression = skip_compression
        self.skip_submission = skip_submission
        self.version = self.version_lookup()
        self.conn = conn

        # read provided options
        if url is None:
            url = UsageLoggers.url_by_default()

        # set options in priority order
        self._enabled = enabled
        self._queue = queue if isinstance(queue, list) else None
        if self._queue is not None:
            self._url = None
        elif url is not None and isinstance(url, str):
            try:
                if urlsplit(url).scheme in {"http", "https"}:
                    self._url_scheme: str = urlsplit(url).scheme
                    self._url = url
                else:
                    raise TypeError("incorrect URL scheme")
            except TypeError:
                self._enabled = False
                self._url = None
        else:
            self._enabled = False
            self._url = None

        # finalize internal properties
        self._enableable = self.queue is not None or self.url is not None
        self._submit_failures = 0
        self._submit_failures_lock = threading.Lock()
        self._submit_successes = 0
        self._submit_successes_lock = threading.Lock()

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
    def queue(self) -> Optional[List[str]]:
        return self._queue

    def submit(self, msg: str) -> None:
        """Submits JSON message to intended destination."""

        if msg is None or self.skip_submission is True or self.enabled is False:
            pass
        elif self._queue is not None:
            self._queue.append(msg)
            with self._submit_successes_lock:
                self._submit_successes += 1
        else:
            try:
                headers: Dict[str, str] = {
                    "Connection": "keep-alive",
                    "Content-Type": "application/json; charset=UTF-8",
                    "User-Agent": "Resurface/"
                    + usagelogger.__version__
                    + " ("
                    + self.agent
                    + ")",
                }

                if not self.skip_compression:
                    body = msg.encode("utf-8")
                else:
                    headers["Content-Encoding"] = "deflated"
                    body = zlib.compress(msg.encode("utf-8"))

                response = self.conn.post(self.url, data=body, headers=headers)
                if response.status_code == 204:
                    with self._submit_successes_lock:
                        self._submit_successes += 1
                else:
                    with self._submit_failures_lock:
                        self._submit_failures += 1

            # http errors
            except (requests.exceptions.RequestException, IOError, OSError):
                with self._submit_failures_lock:
                    self._submit_failures += 1
            # JSON errors
            except (OverflowError, TypeError, ValueError):
                with self._submit_failures_lock:
                    self._submit_failures += 1

    @property
    def submit_failures(self) -> int:
        return self._submit_failures

    @property
    def submit_successes(self) -> int:
        return self._submit_successes

    @property
    def url(self) -> str:
        return self._url  # type: ignore

    @staticmethod
    def host_lookup() -> str:
        dyno = os.getenv("DYNO")
        if dyno is not None:
            return dyno
        try:
            return socket.gethostname()
        except Exception:
            return "unknown"

    @staticmethod
    def version_lookup() -> str:
        return usagelogger.__version__
