import warnings

from . import middleware  # noqa
from .base_logger import BaseLogger  # noqa
from .http_logger import HttpLogger  # noqa
from .http_message import HttpMessage  # noqa
from .http_request_impl import HttpRequestImpl  # noqa
from .http_response_impl import HttpResponseImpl  # noqa
from .http_rules import HttpRules  # noqa
from .usage_loggers import UsageLoggers  # noqa


class ResurfaceWarning(UserWarning):
    def __init__(self, warning_type, environment_var=None, required_type=None):
        self.warning_type = warning_type
        self.env_var = environment_var
        self.required_type = required_type

    def __str__(self):
        if self.warning_type == "argtype":
            warn = (
                f"Invalid type for {self.env_var} "
                + f"(argument should be a {self.required_type}). "
                + "Logger won't be enabled."
            )
        elif self.warning_type == "nologger":
            warn = "Logger is not enabled."
        return warn

    def warn(self):
        warnings.warn(self, stacklevel=2)


__version__ = "2.2.6"

__all___ = [
    "UsageLoggers",
    "HttpRequestImpl",
    "HttpResponseImpl",
    "ResurfaceWarning",
    "HttpRules",
    "BaseLogger",
    "HttpLogger",
    "HttpMessage",
    "resurface",
    "middleware",
    # Depricating soon
    "flask",
    "django",
    "aiohttp",
]
