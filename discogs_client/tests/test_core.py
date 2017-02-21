from __future__ import absolute_import, division, print_function, unicode_literals

import pytest

from discogs_client import Client
from discogs_client.exceptions import ConfigurationError, HTTPError
from datetime import datetime


def test_user_agent(file_client):
    """User-Agent should be properly set"""
    file_client.artist(1).name

    bad_client = Client('')

    with pytest.raises(ConfigurationError):
        bad_client.artist(1).name

    try:
        bad_client.artist(1).name
    except ConfigurationError as e:
        assert 'User-Agent' in str(e)


def test_caching(file_client):
    """Only perform a fetch when requesting missing data"""
    a = file_client.artist(1)

    assert a.id == 1
    assert file_client._fetcher.last_request is None

    assert a.name == 'Persuader, The'
    assert file_client.got(file_client, '/artists/1')

    assert a.real_name == 'Jesper Dahlb\u00e4ck'
    assert len(file_client._fetcher.requests) == 1

    # Get a key that's not in our cache
    a.fetch('blorf')
    assert len(file_client._fetcher.requests) == 2
    assert 'blorf' in a._known_invalid_keys

    # Now we know artists don't have blorves
    a.fetch('blorf')
    assert len(file_client._fetcher.requests) == 2


def test_equality(file_client):
    """APIObjects of the same class are equal if their IDs are"""
    a1 = file_client.artist(1)
    a1_ = file_client.artist(1)
    file_client.artist(2)

    r1 = file_client.release(1)

    assert a1 == a1_
    assert a1 == r1.artists[0]
    assert a1 != r1
    assert r1 != ':D'


def test_transform_datetime(file_client):
    """String timestamps are converted to datetimes"""
    registered = file_client.user('example').registered
    assert isinstance(registered, datetime)


def test_object_field(file_client):
    """APIObjects can have APIObjects as properties"""
    assert file_client.master(4242).main_release == file_client.release(79)


def test_read_only_simple_field(file_client):
    """Can't write to a SimpleField when writable=False"""
    u = file_client.user('example')
    with pytest.raises(AttributeError):
        u.rank = 9001


def test_read_only_object_field(file_client):
    """Can't write to an ObjectField"""
    m = file_client.master(4242)
    with pytest.raises(AttributeError):
        m.main_release = 'lol!'


def test_pagination(file_client):
    """PaginatedLists are parsed correctly, indexable, and iterable"""
    results = file_client.artist(1).releases

    assert results.per_page == 50
    assert results.pages == 2
    assert results.count == 57

    assert len(results) == 57
    assert len(results.page(1)) == 50

    with pytest.raises(HTTPError):
        results.page(42)

    try:
        results.page(42)
    except HTTPError as e:
        assert e.status_code == 404

    with pytest.raises(IndexError):
        results[3141592]

    assert results[0].id == 20209
    assert file_client.release(20209) in results

    # Changing pagination settings invalidates the cache
    results.per_page = 10
    assert results._num_pages is None
