import json
import os
import pytest

from discogs_client import Client
from discogs_client.fetchers import LoggingDelegator, FilesystemFetcher, MemoryFetcher


def got(client, assert_url):
    method, url, data, headers = client._fetcher.last_request
    if method == 'GET' and url == assert_url:
        return True
    return False


def posted(client, assert_url, assert_data):
    method, url, data, headers = client.d._fetcher.last_request
    if method == 'POST' and url == assert_url and data == json.dumps(assert_data):
        return True
    return False


@pytest.fixture()
def file_client():
    client = Client('test_client/0.1 +http://example.org')
    client._base_url = ''
    client._fetcher = LoggingDelegator(FilesystemFetcher(os.path.dirname(os.path.abspath(__file__)) + '/res'))
    client._verbose = True
    client.got = got
    client.posted = posted
    return client


@pytest.fixture()
def memory_client():
    responses = {
        '/artists/1': (b'{"id": 1, "name": "Badger"}', 200),
        '/500': (b'{"message": "mushroom"}', 500),
        '/204': (b'', 204),
    }
    client = Client('ua')
    client._base_url = ''
    client._fetcher = LoggingDelegator(MemoryFetcher(responses))
    client.got = got
    client.posted = posted
    return client


