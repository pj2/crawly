import logging
import re
import requests
from HTMLParser import HTMLParseError
from bs4 import BeautifulSoup
from .href import Href

logger = logging.getLogger(__name__)


class Crawler(object):
    """Crawls a URL following all links within its domain and printing a tree."""
    MAX_URL_WIDTH = 79

    def __init__(self, origin, print_static=False):
        self.origin = origin
        self.print_static = print_static
        self.visited = set()
        self.queue = []
        self.depth = 0

    def reset(self):
        """Reset the crawler's state."""
        self.visited = set()
        self.queue = [self.origin]
        self.depth = 0

    def crawl(self):
        """Crawl for links beginning from ``origin``."""
        n = 0

        self.reset()
        while self.queue:
            cur = self.queue.pop(0)
            self._crawl(cur)
            n += 1

        print 'Accessed {0} resources.'.format(n)

    def _crawl(self, href):
        """Access ``href`` and produce the next portion of the tree."""
        try:
            resp = requests.get(str(href))
            self.visited.add(href)
        except IOError, e:
            logger.error(u'Unexpected error whilst getting {0}.'.format(href), exc_info=e)
            status = -1
            success = False
        else:
            status = resp.status_code
            success = self.is_success_code(status)

        is_page = 'text/html' in resp.headers.get('Content-Type')
        self.print_link(href, is_page, status=status)

        if not (is_page and success):
            return # No more links to process here

        try:
            soup = BeautifulSoup(resp.text, 'html.parser')
        except (HTMLParseError, IOError):
            logger.error(u'Failed to parse {0} as HTML.'.format(href), exc_info=e)
            return

        # Print out static file listing
        if self.print_static:
            for static in self.extract_links(soup, ['img', 'link', 'script']):
                self.print_link(static, False)

        # Add HTML pages to the queue
        for href in self.extract_links(soup, ['a']):
            self.queue.append(href)

    def extract_links(self, soup, tag_names):
        """Return all links found under ``tag_names`` in the HTML document."""
        tags = soup.find_all(name=re.compile('|'.join(tag_names)))
        for tag in tags:
            href = self.parse_href(tag.get('href') or tag.get('src'))
            if href:
                yield href

    def parse_href(self, href_text):
        """Attempt to parse a href attribute. Returns a Href if successful or None otherwise."""
        if not href_text:
            return

        href = Href(href_text)
        if href.scheme and href.scheme not in ('http', 'https'):
            return

        # Ensure protocol + netloc exists for relative and double slash URLs
        if href.is_relative() or not href.parts.scheme:
            href = href.to_absolute(self.origin)

        seen = href in self.visited or href in self.queue
        if seen or not href.has_same_domain(self.origin):
            return

        return href

    def print_link(self, href, is_page, status=None):
        """Print out a line of the site map."""
        print ' ' * (self.depth * 2 + (0 if is_page else 1)),
        print 'P' if is_page else 'S',

        link = str(href)
        if len(link) > self.MAX_URL_WIDTH:
            print link[:self.MAX_URL_WIDTH - 3] + ' ..',
        else:
            print link,

        if status is not None and not self.is_success_code(status):
            print status,

        print ''

    def is_success_code(self, code):
        """Return True if the numeric ``code`` indicates a success."""
        return code >= 200 and code < 400
