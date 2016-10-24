import pytest
from crawly.href import Href


def test_hash():
    """Hash value is same for equal Hrefs"""
    loc = 'http://example.com/test.html'
    assert Href(loc).__hash__() == Href(loc).__hash__()


def test_hash_inverse():
    """Hash value is same for equal Hrefs (inverse)"""
    loc_1 = 'http://example.com/foo.html'
    loc_2 = 'http://example.com/bar.html'
    assert Href(loc_1).__hash__() != Href(loc_2).__hash__()


def test_equality():
    """Return equal if the addresses are the same"""
    loc = 'http://example.com/foo_bar.html'
    assert Href(loc) == Href(loc)


def test_equality_inverse():
    """Return not equal if the addresses are different"""
    loc_1 = 'http://example.com/foo_bar.html'
    loc_2 = 'http://example.com/bar_foo.html'
    assert Href(loc_1) != Href(loc_2)


def test_different_protocol_not_equal():
    """Return not equal is protocol is different"""
    loc_1 = 'http://example.com/foo_bar.html'
    loc_2 = 'https://example.com/bar_foo.html'
    assert Href(loc_1) != Href(loc_2)


def test_relative_to_absolute_equality():
    """Return equal for an absolute and converted relative Href"""
    origin = Href('http://example.com')
    a = Href('http://example.com/resource.html')
    b = Href('//example.com/resource.html').to_absolute(origin)

    assert str(a) == str(b)
    assert a == b
    assert a.__hash__() == b.__hash__()


@pytest.mark.parametrize('url', [
    Href('/example.com'),
])
def test_relativity(url):
    """Test for relativity"""
    assert url.is_relative()


@pytest.mark.parametrize('url', [
    Href('http://example.com'),
    Href('https://example.com/foobar.html'),
    Href('//example.com'),
    Href('//example.com/whatever.html'),
])
def test_relativity_inverse(url):
    """Test for relativity (inverse)"""
    assert not url.is_relative()


def test_same_domain():
    """Return equal for same domain"""
    a = Href('http://example.com')
    b = Href('http://example.com/foo.html')

    assert a.has_same_domain(b)


def test_same_domain_different_subdomain():
    """Return equal for same domain but different subdomain"""
    a = Href('http://foo.example.com')
    b = Href('http://example.com/foo.html')

    assert a.has_same_domain(b)


def test_different_origin_tld():
    """Return not equal domain for different TLDs"""
    a = Href('http://example.com')
    b = Href('http://example.net/foo.html')

    assert not a.has_same_domain(b)


def test_different_origin_domain():
    """Return not equal domain for different domains"""
    a = Href('http://example.com')
    b = Href('http://foobar.com/foo.html')

    assert not a.has_same_domain(b)
