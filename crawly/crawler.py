import logging
import re
import requests
from HTMLParser import HTMLParseError
from bs4 import BeautifulSoup
from .url import URL

logger = logging.getLogger(__name__)


class Crawler(object):
    """Crawls a URL following all links within its domain and printing a tree."""

    def __init__(self, origin, print_static=False):
        self.origin = origin
        self.print_static = print_static
        self.visited = set()
        self.queue = []

    def reset(self):
        """Reset the crawler's state."""
        self.visited = set()
        self.queue = [self.origin]

    def crawl(self):
        """Crawl for links beginning from ``origin``."""
        n = 0

        self.reset()
        while self.queue:
            cur = self.queue.pop(0)
            self._crawl(cur)
            n += 1
            print ''

        print 'Accessed {0} resources.'.format(n)

    def _crawl(self, url):
        """Access ``url`` and produce the next portion of the tree."""
        try:
            resp = requests.get(str(url))
            self.visited.add(url)
        except IOError, e:
            logger.error(u'Unexpected error whilst getting {0}.'.format(url), exc_info=e)
            status = -1
            success = False
        else:
            status = resp.status_code
            success = self.is_success_code(status)

        is_page = 'text/html' in resp.headers.get('Content-Type')
        self.print_link(url, is_page, status=status)

        if not (is_page and success):
            return # No more links to process here

        try:
            soup = BeautifulSoup(resp.text, 'html.parser')
        except (HTMLParseError, IOError):
            logger.error(u'Failed to parse {0} as HTML.'.format(url), exc_info=e)
            return

        # Print out static file listing
        if self.print_static:
            self.process_static(soup, url)

        self.process_a(soup, url)

    def process_static(self, soup, source_url):
        """Process links to static files."""
        for static in set(self.extract_links(soup, source_url, ['img', 'link', 'script'])):
            self.print_link(static, False, level=1)

    def process_a(self, soup, source_url):
        """Process and accept more crawlable links into the queue."""
        a_links = set(self.extract_links(soup, source_url, ['a']))
        for url in a_links:
            # Add unvisited / unmarked HTML pages to the queue
            added = url in self.visited or url in self.queue
            if not added:
                self.queue.append(url)

            # Print out all unique URLs on this page
            self.print_link(url, True, level=1)

    def extract_links(self, soup, source_url, tag_names):
        """Return all URLs found under ``tag_names`` in the HTML document."""
        tags = soup.find_all(name=re.compile('|'.join(tag_names)))
        for tag in tags:
            url = self.parse_url(tag.get('href') or tag.get('src'), source_url)
            if url:
                yield url

    def parse_url(self, url_text, source_url):
        """Attempt to parse a URL attribute. Returns a URL if successful or None otherwise."""
        if not url_text:
            return

        url = URL(url_text)
        if url.scheme and url.scheme not in ('http', 'https'):
            return

        # Ensure protocol + netloc exists for relative and double slash URLs
        if url.is_relative() or not url.parts.scheme:
            url = url.to_absolute(source_url)

        if not url.has_same_domain(self.origin):
            return

        return url

    def print_link(self, url, is_page, level=0, status=None):
        """Print out a line of the site map."""
        print ' ' * level * 4,
        print 'P' if is_page else 'S',
        print str(url),

        if status is not None:
            print status,

        print ''

    def is_success_code(self, code):
        """Return True if the numeric ``code`` indicates a success."""
        return code >= 200 and code < 400
