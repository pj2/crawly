import logging
import re
import requests
from HTMLParser import HTMLParseError
from bs4 import BeautifulSoup
from .href import Href

logger = logging.getLogger(__name__)

LEVEL_UP = 1
MAX_WIDTH = 119


def crawl(origin, print_static=True):
    """Crawl a URL following all links within its domain and printing a
    tree."""
    n = 0
    depth = 0
    queue = [origin]
    visited = set()

    while queue:
        cur = queue.pop(0)
        if cur == LEVEL_UP:
            depth += 1
        else:
            _crawl(cur, origin, visited, queue, depth, print_static)
            n += 1

    print 'Accessed {0} resources.'.format(n)


def _crawl(href, origin, visited, queue, depth, print_static):
    """Access ``href`` and produce the next portion of the tree."""
    try:
        resp = requests.get(str(href))
        visited.add(href)
    except IOError, e:
        logger.error(u'Unexpected error whilst getting {0}.'.format(href), exc_info=e)

        status = -1
        success = False
    else:
        status = resp.status_code
        success = is_success_code(status)

    is_page = 'text/html' in resp.headers.get('Content-Type')
    print_link(href, is_page, depth, status=status)

    if not (is_page and success):
        return # No more links to process here

    try:
        soup = BeautifulSoup(resp.text, 'html.parser')
    except (HTMLParseError, IOError):
        logger.error(u'Failed to parse {0} as HTML.'.format(href), exc_info=e)
    else:
        # Add HTML pages to the queue
        more_html = extract_links(soup, ['a'])
        if more_html:
            queue.append(LEVEL_UP)
            for href in more_html:
                accept_link(href, origin, queue, visited)

        # Print out static file listing
        if print_static:
            for static in extract_links(soup, ['img', 'link', 'script']):
                print_link(static, False, depth)


def extract_links(soup, tag_names):
    """Return all links found under ``tag_names`` in the HTML document."""
    out = []
    for tag in soup.find_all(name=re.compile('|'.join(tag_names))):
        target = tag.get('href') or tag.get('src')
        if target:
            out.append(Href(target))

    return out


def accept_link(child, origin, queue, visited):
    """Process a tag which contains a link."""
    if child.scheme and child.scheme not in ('http', 'https'):
        return

    # Ensure protocol + netloc exists for relative and double slash URLs
    # TODO Move to extract_links (for printing purposes)
    if child.is_relative() or not child.parts.scheme:
        child = child.to_absolute(origin)

    already_exists = child in visited or child in queue
    if not already_exists and child.has_same_domain(origin):
        queue.append(child)


def print_link(href, is_page, depth, status=None):
    """Print out a line of the site map."""
    print ' ' * (depth * 4 + (0 if is_page else 2)),
    print 'P' if is_page else 'S',

    link = str(href)
    if len(link) > MAX_WIDTH:
        print link[:MAX_WIDTH - 3] + ' ..',
    else:
        print link,

    if status is not None and not is_success_code(status):
        print status,

    print ''


def is_success_code(code):
    """Return True if the numeric ``code`` indicates a success."""
    return code >= 200 and code < 400
