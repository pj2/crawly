import logging
import re
import requests
from HTMLParser import HTMLParseError
from bs4 import BeautifulSoup
from .href import Href

logger = logging.getLogger(__name__)


def crawl(origin):
    """Crawl a URL following all links within its domain and printing a
    tree."""
    i = 0
    queue = [origin]
    visited = set()

    while queue:
        cur = queue.pop(0)
        _crawl(cur, origin, visited, queue)
        i += 1

    print 'Accessed {0} resources.'.format(i)


def _crawl(href, origin, visited, queue):
    """Access ``href`` and produce the next portion of the tree."""
    try:
        resp = requests.get(str(href))
        visited.add(href)
    except IOError, e:
        logger.error(u'Unexpected error whilst getting {0}.'.format(href), exc_info=e)

        status = '(failed)'
        success = False
    else:
        status = resp.status_code
        success = status >= 200 and status < 400

    is_page = 'text/html' in resp.headers.get('Content-Type')
    if is_page:
        if success:
            try:
                links = extract_links(resp.text)
            except ValueError:
                pass # Ignore links in malformed documents
            else:
                for tag in links:
                    accept_link(tag, origin, queue, visited)

        print href, status # Web page
    else:
        print '*', href.uri # Static file


def extract_links(html):
    """Return a set of tags which contain links and are contained in the HTML
    document. Raises ValueError if the HTML is malformed."""
    try:
        soup = BeautifulSoup(html, 'html.parser')
        return soup.find_all(name=re.compile('img|script|link|a'))
    except (HTMLParseError, IOError):
        raise ValueError('malformed page')


def accept_link(tag, origin, queue, visited):
    """Process a tag which contains a link."""
    target = tag.get('href') or tag.get('src')
    if not target:
        return

    child = Href(target)
    if child.scheme and child.scheme not in ('http', 'https'):
        return

    # Ensure protocol + netloc exists for relative and double slash URLs
    if child.is_relative() or not child.parts.scheme:
        child = child.to_absolute(origin)

    already_exists = child in visited or child in queue
    if already_exists or not child.has_same_domain(origin):
        return

    queue.insert(0, child)
