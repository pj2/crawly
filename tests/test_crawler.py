# -*- coding: utf-8 -*-
import pytest
from urlparse import urljoin
from crawly.crawler import Crawler
from crawly.href import Href


def test_live_site_without_exception(site):
    """Crawls a live site without raising an exception"""
    Crawler(Href(urljoin(site, '/index.html'))).crawl()


@pytest.mark.parametrize('href,origin,visited', [
    # Absolute, same origin, not visited before
    ('http://example.com/resource.html', 'http://example.com', None),
    ('https://example.com/resource.html', 'http://example.com', None),

    # Absolute (double slash), same origin, not visited before
    ('//www.example.com/resource.html', 'http://www.example.com', None),

    # Different subdomains
    ('http://foo.example.com/resource.html', 'http://www.example.com', None),
    ('http://foo.bar.example.com/resource.html', 'http://www.example.com', None),
    ('http://example.com/resource.html', 'http://www.example.com', None),

    # Query string / fragment
    ('http://example.com/resource.html?foo=bar', 'http://example.com', 'http://example.com/resource.html'),
    ('http://example.com/resource.html#blah', 'http://example.com', 'http://example.com/resource.html'),

    # Relative, not visited before
    ('resource.html', 'http://example.com', None),
    ('/resource.html', 'http://example.com', None),

    # Absolute, same origin, visited before but _different_ protocol
    ('http://example.com/resource.html', 'https://example.com', 'https://example.com/resource.html'),
    ('https://example.com/resource.html', 'https://example.com', 'http://example.com/resource.html'),

    # Relative, visited before but _different_ protocol
    ('/resource.html', 'http://example.com', 'https://example.com/resource.html'),
    ('//example.com/resource.html', 'http://example.com', 'https://example.com/resource.html'),

    # Unicode
    (u'/世界', 'http://example.com', None),

    # Scary looking but OK
    ('awofawfi m29)(!F)', 'http://example.com', None),
    (u'šðèæž ŠÐÈÆŽ', 'http://example.com', None),
    (u'/šðèæž ŠÐÈÆŽ', 'http://example.com', None),
    (u'http://example.com/šðèæž ŠÐÈÆŽ', 'http://example.com', None),
])
def test_good_links(href, origin, visited):
    """Adds valid links to queue"""
    crawler = Crawler(Href(origin))
    crawler.queue = [Href(visited)] if visited is not None else []

    assert crawler.parse_href(href) is not None


@pytest.mark.parametrize('href,origin,visited', [
    # Absolute, different origin, not visited before
    ('http://example.com/resource.js', 'https://foobar.net', None),
    ('https://example.com/resource.js', 'https://foobar.net', None),

    # Absolute (double slash), different origin, not visited before
    ('//example.com/resource.js', 'https://foobar.net', None),
    ('//example.com/resource.js', 'https://foobar.net', None),

    # Double slash with no domain
    ('//resource.html', 'http://example.com', None),

    # Same origin, non-HTTP / HTTPS protocol
    ('ftp://example.com/resource.js', 'https://example.com', None),
    ('ssh://example.com/resource.js', 'https://example.com', None),

    # Different TLDs
    ('http://www.example.com/resource.js', 'https://example.net', None),

    # Query string / fragment
    ('http://example.com/resource.html?foo=bar', 'http://example.com', 'http://example.com/resource.html?foo=bar'),
    ('http://example.com/resource.html#blah', 'http://example.com', 'http://example.com/resource.html#blah'),

    # Already visited - HTTP
    ('resource.html', 'http://example.com', 'http://example.com/resource.html'),
    ('/resource.html', 'http://example.com', 'http://example.com/resource.html'),
    ('http://example.com/resource.html', 'http://example.com', 'http://example.com/resource.html'),

    # Already visited - HTTPS
    ('resource.html', 'https://example.com', 'https://example.com/resource.html'),
    ('//resource.html', 'https://example.com', 'https://example.com/resource.html'),
    ('https://example.com/resource.html', 'https://example.com', 'https://example.com/resource.html'),
])
def test_bad_links(href, origin, visited):
    """Ignores invalid links"""
    crawler = Crawler(Href(origin))
    crawler.queue = [Href(visited)] if visited is not None else []

    assert crawler.parse_href(href) is None
