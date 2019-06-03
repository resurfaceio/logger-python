# © 2016-2019 Resurface Labs Inc.

from expects import *
from mamba import description, it

from usagelogger.usage_loggers import UsageLoggers

with description('UsageLoggers') as self:
    with it('provides default url'):
        expect(UsageLoggers.url_by_default()).to(be_none)
