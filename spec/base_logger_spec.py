# © 2016-2019 Resurface Labs Inc.

from expects import *
from mamba import description, it
from usagelogger import BaseLogger, UsageLoggers

# todo move out to helper
DEMO_URL = 'https://demo.resurface.io/ping'
MOCK_AGENT = 'helper.py'
MOCK_URLS_DENIED = [DEMO_URL + "/noway3is5this1valid2", "https://www.noway3is5this1valid2.com/"]
MOCK_URLS_INVALID = ["", "noway3is5this1valid2", "ftp:\\www.noway3is5this1valid2.com/", "urn:ISSN:1535–3613"]

with description('BaseLogger') as self:
    with it('creates instance'):
        logger = BaseLogger(MOCK_AGENT)
        expect(logger).not_to(be_none)
        expect(logger.agent).to(equal(MOCK_AGENT))
        expect(logger.enableable).to(be_false)
        expect(logger.enabled).to(be_false)

    with it('creates multiple instances'):
        agent1 = 'agent1'
        agent2 = 'AGENT2'
        agent3 = 'aGeNt3'
        url1 = 'http://resurface.io'
        url2 = 'http://whatever.com'
        logger1 = BaseLogger(agent1, url=url1)
        logger2 = BaseLogger(agent2, url=url2)
        logger3 = BaseLogger(agent3, url=DEMO_URL)

        expect(logger1.agent).to(equal(agent1))
        expect(logger1.enableable).to(be_true)
        expect(logger1.enabled).to(be_true)
        expect(logger1.url).to(equal(url1))
        expect(logger2.agent).to(equal(agent2))
        expect(logger2.enableable).to(be_true)
        expect(logger2.enabled).to(be_true)
        expect(logger2.url).to(equal(url2))
        expect(logger3.agent).to(equal(agent3))
        expect(logger3.enableable).to(be_true)
        expect(logger3.enabled).to(be_true)
        expect(logger3.url).to(equal(DEMO_URL))

        UsageLoggers.disable()
        expect(UsageLoggers.is_enabled()).to(be_false)
        expect(logger1.enabled).to(be_false)
        expect(logger2.enabled).to(be_false)
        expect(logger3.enabled).to(be_false)
        UsageLoggers.enable()
        expect(UsageLoggers.is_enabled()).to(be_true)
        expect(logger1.enabled).to(be_true)
        expect(logger2.enabled).to(be_true)
        expect(logger3.enabled).to(be_true)

    with it('has valid version'):
        version = BaseLogger.version_lookup()
        expect(version).not_to(be_none)
        expect(len(version)).to(be_above(0))
        expect(version).to(start_with('0.1.'))
        expect(version).not_to(contain('\\'))
        expect(version).not_to(contain('\"'))
        expect(version).not_to(contain("'"))
        expect(version).to(equal(BaseLogger(MOCK_AGENT).version))

    with it('performs enabling when expected'):
        logger = BaseLogger(MOCK_AGENT, url=DEMO_URL, enabled=False)
        expect(logger.enableable).to(be_true)
        expect(logger.enabled).to(be_false)
        expect(logger.url).to(equal(DEMO_URL))
        logger.enable()
        expect(logger.enabled).to(be_true)
        # todo add queue example

    with it('skips enabling for invalid urls'):
        for invalid_url in MOCK_URLS_INVALID:
            logger = BaseLogger(MOCK_AGENT, url=invalid_url)
            expect(logger.enableable).to(be_false)
            expect(logger.enabled).to(be_false)
            expect(logger.url).to(be_none)
            logger.enable()
            expect(logger.enabled).to(be_false)

    with it('skips enabling for missing url'):
        logger = BaseLogger(MOCK_AGENT)
        expect(logger.enableable).to(be_false)
        expect(logger.enabled).to(be_false)
        expect(logger.url).to(be_none)
        logger.enable()
        expect(logger.enabled).to(be_false)

    with it('skips enabling for undefined url'):
        logger = BaseLogger(MOCK_AGENT, url=None)
        expect(logger.enableable).to(be_false)
        expect(logger.enabled).to(be_false)
        expect(logger.url).to(be_none)
        logger.enable()
        expect(logger.enabled).to(be_false)

    with it('skips logging when disabled'):
        for denied_url in MOCK_URLS_DENIED:
            logger = BaseLogger(MOCK_AGENT, url=denied_url)
            logger.disable()
            expect(logger.enableable).to(be_true)
            expect(logger.enabled).to(be_false)
            expect(logger.submit(None)).to(be_true)  # would fail if enabled

    with it('submits to demo url'):
        logger = BaseLogger(MOCK_AGENT, url=DEMO_URL)
        expect(logger.url).to(equal(DEMO_URL))
        # todo add agent, version, now, protocol
        # todo convert to json
        expect(logger.submit('{}')).to(be_true)
        # todo try again with skip compression

    with it('submits to demo url via http'):
        logger = BaseLogger(MOCK_AGENT, url=DEMO_URL.replace('https', 'http', 1))
        expect(logger.url).to(start_with('http://'))
        # todo add agent, version, now, protocol
        # todo convert to json
        expect(logger.submit('{}')).to(be_true)
        # todo try again with skip compression

    with it('submits to demo url without compression'):
        expect(None).to(be_none)  # todo finish

    with it('submits to denied url and fails'):
        for denied_url in MOCK_URLS_DENIED:
            logger = BaseLogger(MOCK_AGENT, url=denied_url)
            expect(logger.enableable).to(be_true)
            expect(logger.enabled).to(be_true)
            expect(logger.submit('{}')).to(be_false)

    with it('submits to queue'):
        expect(None).to(be_none)  # todo finish

    with it('uses skip options'):
        expect(None).to(be_none)  # todo finish

# todo test unexpected types (array as url)
# todo test url passed forgetting 'url=' prefix
