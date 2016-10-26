# -*- coding: utf-8 -*-
from urlparse import urljoin
from crawly.crawler import Crawler
from crawly.url import URL


def test_live_site_without_exception(site):
    """Crawls a live site without raising an exception"""
    Crawler(URL(urljoin(site, '/index.html'))).crawl()
