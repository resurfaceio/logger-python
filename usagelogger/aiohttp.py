import warnings

from .middleware.aiohttp import *  # noqa # pylint: disable=wildcard-import

warnings.warn(
    """Importing HttpLoggerForAIOHTTP from usagelogger.aiohtto is depricating soon.
    Please import from usagelogger.middleware.aiohtto instead."""
)
