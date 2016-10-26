# -*- coding: utf-8 -*-
import pytest
from crawly.url import URL


def test_hash():
    """Hash value is same for equal URLs"""
    loc = 'http://example.com/test.html'
    assert URL(loc).__hash__() == URL(loc).__hash__()


def test_hash_inverse():
    """Hash value is same for equal URLs (inverse)"""
    loc_1 = 'http://example.com/foo.html'
    loc_2 = 'http://example.com/bar.html'
    assert URL(loc_1).__hash__() != URL(loc_2).__hash__()


def test_equality():
    """Return equal if the addresses are the same"""
    loc = 'http://example.com/foo_bar.html'
    assert URL(loc) == URL(loc)


def test_equality_inverse():
    """Return not equal if the addresses are different"""
    loc_1 = 'http://example.com/foo_bar.html'
    loc_2 = 'http://example.com/bar_foo.html'
    assert URL(loc_1) != URL(loc_2)


def test_different_protocol_not_equal():
    """Return not equal if protocol is different"""
    loc_1 = 'http://example.com/foo_bar.html'
    loc_2 = 'https://example.com/bar_foo.html'
    assert URL(loc_1) != URL(loc_2)


def test_relative_to_absolute_equality():
    """Return equal for an absolute and converted relative URL"""
    origin = URL('http://example.com')
    a = URL('http://example.com/resource.html')
    b = URL('//example.com/resource.html').to_absolute(origin)

    assert str(a) == str(b)
    assert a == b
    assert a.__hash__() == b.__hash__()


@pytest.mark.parametrize('url', [
    URL('/example.com'),
])
def test_relativity(url):
    """Test for relativity"""
    assert url.is_relative()


@pytest.mark.parametrize('url', [
    URL('http://example.com'),
    URL('https://example.com/foobar.html'),
    URL('//example.com'),
    URL('//example.com/whatever.html'),
])
def test_relativity_inverse(url):
    """Test for relativity (inverse)"""
    assert not url.is_relative()


def test_same_domain():
    """Return equal for same domain"""
    a = URL('http://example.com')
    b = URL('http://example.com/foo.html')

    assert a.has_same_domain(b)


def test_same_domain_different_subdomain():
    """Return equal for same domain but different subdomain"""
    a = URL('http://foo.example.com')
    b = URL('http://example.com/foo.html')

    assert a.has_same_domain(b)


def test_different_origin_tld():
    """Return not equal domain for different TLDs"""
    a = URL('http://example.com')
    b = URL('http://example.net/foo.html')

    assert not a.has_same_domain(b)


def test_different_origin_domain():
    """Return not equal domain for different domains"""
    a = URL('http://example.com')
    b = URL('http://foobar.com/foo.html')

    assert not a.has_same_domain(b)


def test_querystring():
    assert URL('http://example.com/resource.html?foo=bar') == \
        URL('http://example.com/resource.html?foo=bar')


def test_join_no_slash_relative():
    a = URL('https://www.google.com/intl/en/about/')
    b = URL('company/philosophy/')

    assert b.to_absolute(a) == URL('https://www.google.com/intl/en/about/company/philosophy/')


def test_join_relative():
    a = URL('https://example.com/resource.html')
    b = URL('/resource.html')

    assert b.to_absolute(a) == URL('https://example.com/resource.html')


def test_unicode():
    a = URL('http://example.com/')
    b = URL(u'/世界')

    assert b.to_absolute(a) == URL(u'http://example.com/世界')
