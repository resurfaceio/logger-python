import warnings

from .middleware.flask import *  # noqa # pylint: disable=allow-with-wildcard-import,unused-wildcard-import

warnings.warn(
    """Importing HttpLoggerForFlask from usagelogger.flask is depricating soon.
    Please import from usagelogger.middleware.flask instead."""
)
