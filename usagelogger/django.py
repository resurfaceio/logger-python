import warnings

from .middleware.django import *  # noqa  # pylint: disable=allow-with-wildcard-import,unused-wildcard-import

warnings.warn(
    """Importing HttpLoggerForDjango from usagelogger.django is depricating soon.
    Please import from usagelogger.middleware.django instead."""
)
