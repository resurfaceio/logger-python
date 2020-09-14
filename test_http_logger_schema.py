# coding: utf-8
# © 2016-2020 Resurface Labs Inc.

from test_helper import *
from usagelogger import HttpLogger


def test_loads_default_schema():
    queue = []
    logger = HttpLogger(queue=queue)
    assert logger.schema is None


def test_loads_schema():
    myschema = 'type Foo { bar: String }'

    queue = []
    logger = HttpLogger(queue=queue, schema=myschema)
    assert logger.schema == myschema

    assert len(queue) == 1
    msg = queue[0]
    assert parseable(msg) is True
    assert f"[\"graphql_schema\",\"{myschema}\"]" in msg


def test_loads_schema_from_file():
    myschema = 'type Query { hello: String }'

    queue = []
    logger = HttpLogger(queue=queue, schema='file://./test_schema1.txt')
    assert logger.schema == myschema

    assert len(queue) == 1
    msg = queue[0]
    assert parseable(msg) is True
    assert f"[\"graphql_schema\",\"{myschema}\"]" in msg


def test_raises_expected_errors():
    try:
        queue = []
        HttpLogger(queue=queue, schema="file://~/bleepblorpbleepblorp12345")
        assert False
    except FileNotFoundError as e:
        assert str(e) == 'Failed to load schema: ~/bleepblorpbleepblorp12345'
