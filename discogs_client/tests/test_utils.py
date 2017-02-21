from __future__ import absolute_import, division, print_function, unicode_literals

from datetime import datetime
from discogs_client.utils import omit_none, parse_timestamp, update_qs


def test_omit_none():
    assert omit_none({'foo': None, 'baz': 'bat', 'qux': None, 'flan': 0}) == {'baz': 'bat', 'flan': 0}
    assert omit_none(dict((k, None) for k in ('qux', 'quux', 'quuux'))) == {}
    assert omit_none({'nope': 'yep'}) == {'nope': 'yep'}
    assert omit_none({}) == {}


def test_parse_timestamp():
    assert parse_timestamp('2012-01-01T00:00:00') == datetime(2012, 1, 1, 0, 0, 0)
    assert parse_timestamp('2001-05-25T00:00:42') == datetime(2001, 5, 25, 0, 0, 42)


def test_update_qs():
    assert update_qs('http://example.com', {'foo': 'bar'}) == 'http://example.com?foo=bar'
    assert update_qs('http://example.com?foo=bar', {'foo': 'baz'}) == 'http://example.com?foo=bar&foo=baz'

    # be careful for dict iteration order is not deterministic
    result = update_qs('http://example.com?c=3&a=yep', {'a': 1, 'b': '1'})
    try:
        assert result == 'http://example.com?c=3&a=yep&a=1&b=1'
    except AssertionError:
        assert result == 'http://example.com?c=3&a=yep&b=1&a=1'

    assert update_qs('http://example.com', {'a': 't\xe9st'}) == 'http://example.com?a=t%C3%A9st'
