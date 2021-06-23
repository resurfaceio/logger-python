import warnings

from .middleware.flask import *  # noqa

warnings.warn(
    """Importing HttpLoggerForFlask from usagelogger.flask is depricating soon.
    Please import from usagelogger.middleware.flask instead."""
)
