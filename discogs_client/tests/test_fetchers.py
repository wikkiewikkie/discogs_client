from __future__ import absolute_import, division, print_function, unicode_literals

import pytest

from discogs_client.exceptions import HTTPError


def test_memory_fetcher(memory_client):
    """Client can fetch responses with MemoryFetcher"""
    memory_client.artist(1)

    with pytest.raises(HTTPError):
        memory_client._get('/500')

    try:
        memory_client._get('/500')
    except HTTPError as e:
        assert e.status_code == 500

    with pytest.raises(HTTPError):
        memory_client.release(1).title

    assert memory_client._get('/204') is None
