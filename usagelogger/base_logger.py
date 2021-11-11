# coding: utf-8
# © 2016-2021 Resurface Labs Inc.
import json
import os
import socket
import threading
import zlib
from queue import Queue
from typing import Dict, List, Optional
from urllib.parse import urlsplit

import requests

import usagelogger  # just to read version

from .usage_loggers import UsageLoggers

enclosure_queue: Queue = Queue()

WAF_ENABLED = bool(os.getenv("WAF_ENABLED", False))


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
        conn: requests.Session = requests.Session(),
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
                if urlsplit(url).scheme not in {"http", "https"}:
                    raise TypeError("incorrect URL scheme")
                self._url_scheme: str = urlsplit(url).scheme
                self._url = url
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
        if WAF_ENABLED:
            from ._waf import WAF

            self.waf = WAF.load_model()
        else:
            self.waf = None

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

    def __internal_submission(self, q: Queue):
        try:
            headers: Dict[str, str] = {
                "Connection": "keep-alive",
                "Content-Type": "application/ndjson; charset=UTF-8",
                "User-Agent": "Resurface/"
                + usagelogger.__version__
                + " ("
                + self.agent
                + ")",
            }

            to_submit = []

            while not q.empty():
                payload = q.get()
                # ML WAF
                if WAF_ENABLED:
                    proba = self.waf.get_threat_probabilities(
                        query=payload["msg"][1][1]
                    )
                    payload["msg"].append(["threat_score", proba])
                payload["msg"] = json.dumps(payload["msg"], separators=(",", ":"))
                if not payload["skip_compression"]:
                    body = payload["msg"]
                else:
                    headers["Content-Encoding"] = "deflated"
                    body = zlib.compress(payload["msg"])

                to_submit.append(body)
                q.task_done()

            # print(f"submitting {len(to_submit)} at once")
            ndjson_payload = ("\n".join(to_submit)).encode("utf-8")
            response = self.conn.post(
                payload["url"], data=ndjson_payload, headers=headers
            )
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

    def submit(self, msg: list) -> None:
        """Submits JSON message to intended destination."""

        if msg is None or self.skip_submission is True or self.enabled is False:
            pass
        elif self._queue is not None:
            self._queue.append(json.dumps(msg, separators=(",", ":")))
            with self._submit_successes_lock:
                self._submit_successes += 1
        else:
            payload = {
                "url": self.url,
                "msg": msg,
                "skip_compression": self.skip_compression,
            }
            enclosure_queue.put(payload)
            if "submission_thread" not in [x.name for x in threading.enumerate()]:
                worker = threading.Thread(
                    target=self.__internal_submission,
                    args=(enclosure_queue,),
                )
                worker.name = "submission_thread"
                worker.setDaemon(True)
                worker.start()
                worker.join()  # Not a good practice but required for that success and failure counts

            # enclosure_queue.join()  # We don't have to block our main thread.

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
