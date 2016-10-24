import re
import requests
from HTMLParser import HTMLParseError
from bs4 import BeautifulSoup
from .href import Href


def crawl(origin):
    """Crawl a URL following all links within its domain and printing a
    tree."""
    queue = [origin]
    visited = set()

    while queue:
        cur = queue.pop(0)
        _crawl(cur, origin, visited, queue)


def _crawl(href, origin, visited, queue):
    """Access ``href`` and produce the next portion of the tree."""
    # Lookup the resource
    try:
        resp = requests.get(str(href))
        visited.add(href)
        print href

        resp.raise_for_status()
    except IOError:
        return # Don't follow unsuccessful links

    is_html = 'text/html' in resp.headers.get('Content-Type')
    if not is_html:
        return # No more links to follow on this resource

    try:
        for tag in extract_links(resp.text):
            accept_link(tag, origin, queue, visited)
    except ValueError:
        return # Skip links in malformed documents


def extract_links(html):
    """Return a set of tags which contain links and are contained in the HTML
    document. Raises ValueError if the HTML is malformed."""
    try:
        soup = BeautifulSoup(html, 'html.parser')
        return soup.find_all(name=re.compile('href|src|link|a'))
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

    if child.is_relative() or not child.parts.scheme:
        child = child.to_absolute(origin)

    if tag.name == 'a':
        # Add this link to the queue if it qualifies
        already_exists = child in visited or child in queue
        if not already_exists and child.has_same_domain(origin):
            queue.insert(0, child)
    else:
        print child
