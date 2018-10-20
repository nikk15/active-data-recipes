from __future__ import print_function, absolute_import, unicode_literals

import json
import sys
from imp import reload
from io import BytesIO, StringIO

import pytest
import yaml

from adr import query
from adr.query import format_query
from adr.util.config import Configuration

if sys.version_info > (3, 0):
    IO = StringIO
else:
    IO = BytesIO


@pytest.fixture
def config():
    config = Configuration()
    config.fmt = 'json'
    config.debug_url = "http://activedata.allizom.org/tools/query.html#query_id={}"
    return config


class RunQuery(object):
    def __init__(self, query_test):
        self.query_test = query_test

    def __call__(self, query, *args, **kwargs):
        return self.query_test['mock_data']


def test_query(monkeypatch, query_test, config):

    monkeypatch.setattr(query, 'query_activedata', RunQuery(query_test))
    module = 'adr.queries.{}'.format(query_test['query'])
    if module in sys.modules:
        reload(sys.modules[module])

    def print_diff():

        buf = IO()
        yaml.dump(result, buf)
        print("Yaml formatted result for copy/paste:")
        print(buf.getvalue())

        buf = IO()
        yaml.dump(query_test['expected'], buf)
        print("\nYaml formatted expected:")
        print(buf.getvalue())

    if query_test['debug']:

        config.debug = True
        result = format_query(query_test['query'], config)[1]

        print_diff()
        assert result == config.build_debug_url(query_test["expected"]["meta"]["saved_as"])

    else:

        config.debug = False
        formatted_query = format_query(query_test['query'], config)
        result = json.loads(formatted_query[0])
        debug_url = formatted_query[1]

        print_diff()
        assert result == query_test["expected"]
        assert debug_url is None
