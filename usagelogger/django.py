import warnings

from .middleware.django import *  # noqa

warnings.warn(
    """Importing HttpLoggerForDjango from usagelogger.django is depricating soon.
    Please import from usagelogger.middleware.django instead."""
)
