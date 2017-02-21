from __future__ import absolute_import, division, print_function, unicode_literals

import pytest

from discogs_client.models import Artist, Release
from discogs_client.exceptions import HTTPError


def test_artist(file_client):
    """Artists can be fetched and parsed"""
    a = file_client.artist(1)
    assert a.name == 'Persuader, The'


def test_release(file_client):
    """Releases can be fetched and parsed"""
    r = file_client.release(1)
    assert r.title == 'Stockholm'


def test_master(file_client):
    """Masters can be fetched and parsed"""
    m = file_client.master(4242)
    assert len(m.tracklist) == 4


def test_user(file_client):
    """Users can be fetched and parsed"""
    u = file_client.user('example')
    assert u.username == 'example'
    assert u.name == 'Example Sampleman'


def test_search(file_client):
    results = file_client.search('trash80')
    assert len(results) == 13
    assert isinstance(results[0], Artist)
    assert isinstance(results[1], Release)


def test_utf8_search(file_client):
    uni_string = 'caf\xe9'.encode('utf8')
    try:
        results = file_client.search(uni_string)
    except Exception as e:
        pytest.fail('exception {} was raised'.format(e))


def test_fee(file_client):
    fee = file_client.fee_for(20.5, currency='EUR')
    assert fee.currency == 'USD'
    assert abs(fee.value-1.57) < 0.0001  # almost equal


def test_invalid_artist(file_client):
    """Invalid artist raises HTTPError"""
    with pytest.raises(HTTPError):
        file_client.artist(0).name


def test_invalid_release(file_client):
    """Invalid release raises HTTPError"""
    with pytest.raises(HTTPError):
        file_client.release(0).title


def test_http_error(file_client):
    """HTTPError provides useful information"""
    with pytest.raises(HTTPError):
        file_client.artist(0).name

    try:
        file_client.artist(0).name
    except HTTPError as e:
        assert e.status_code == 404
        assert '404: Resource not found.' == str(e)


def test_parent_label(file_client):
    """Test parent_label / sublabels relationship"""
    l = file_client.label(1)
    l2 = file_client.label(31405)

    assert l.parent_label is None
    assert l2 in l.sublabels
    assert l2.parent_label == l


def test_master_versions(file_client):
    """Test main_release / versions relationship"""
    m = file_client.master(4242)
    r = file_client.release(79)
    v = m.versions

    assert len(v) == 2
    assert r in v
    assert r.master == m

    r2 = file_client.release(3329867)
    assert r2.master is None


def test_user_writable(file_client):
    """User profile can be updated"""
    u = file_client.user('example')
    u.name  # Trigger a fetch

    method, url, data, headers = file_client._fetcher.requests[0]
    assert method == 'GET'
    assert url == '/users/example'

    new_home_page = 'http://www.discogs.com'
    u.home_page = new_home_page
    assert 'home_page' in u.changes
    assert 'profile' not in u.changes

    u.save()

    # Save
    method, url, data, headers = file_client._fetcher.requests[1]
    assert method == 'POST'
    assert url == '/users/example'
    assert data == {'home_page': new_home_page}

    # Refresh
    method, url, data, headers = file_client._fetcher.requests[2]
    assert method == 'GET'
    assert url == '/users/example'


def test_wantlist(file_client, memory_client):
    """Wantlists can be manipulated"""
    # Fetch the user/wantlist from the filesystem
    u = file_client.user('example')
    assert len(u.wantlist) == 3

    # Stub out expected responses
    memory_client._fetcher.fetcher.responses = {
        '/users/example/wants/5': (b'{"id": 5}', 201),
        '/users/example/wants/1': (b'', 204),
    }

    # Now bind the user to the memory client
    u.client = memory_client

    u.wantlist.add(5)
    method, url, data, headers = memory_client._fetcher.last_request
    assert method == 'PUT'
    assert url == '/users/example/wants/5'

    u.wantlist.remove(1)
    method, url, data, headers = memory_client._fetcher.last_request
    assert method == 'DELETE'
    assert url == '/users/example/wants/1'


def test_delete_object(file_client):
    """Can request DELETE on an APIObject"""
    u = file_client.user('example')
    u.delete()

    method, url, data, headers = file_client._fetcher.last_request
    assert method == 'DELETE'
    assert url == '/users/example'


def test_identity(file_client):
    """OAuth identity returns a User"""
    me = file_client.identity()
    assert me.data['consumer_name'] == 'Test Client'
    assert me == file_client.user('example')
