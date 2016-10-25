from urlparse import urlparse, urlunparse, urljoin
import tldextract


class Href(object):
    """A resource locator."""

    def __init__(self, raw):
        self.raw = raw
        self.parts = urlparse(self.raw)
        self.tld_extract = tldextract.extract(self.raw)

    @property
    def uri(self):
        """Return the resource section of the Href."""
        return (self.parts.path +
                (u'?' + self.parts.query if self.parts.query else u'') +
                (u'#' + self.parts.fragment if self.parts.fragment else u''))

    @property
    def scheme(self):
        """Return the scheme (protocol) of the Href or None."""
        return self.parts.scheme or None

    def is_relative(self):
        """Return True if this Href is relative."""
        return self.parts.netloc == ''

    def has_same_domain(self, other_href):
        """Return True if this and ``other_href`` share the same domain."""
        return self.parts.netloc and \
            self.tld_extract.domain == other_href.tld_extract.domain and \
            self.tld_extract.suffix == other_href.tld_extract.suffix

    def to_absolute(self, base_href):
        """Return an absolute Href based on ``base_href``."""
        if base_href.is_relative():
            raise ValueError('base_href must be absolute')

        scheme = self.scheme or base_href.scheme or u'http'
        raw = urlunparse((scheme,) + self.parts[1:])

        return Href(urljoin(base_href.raw, raw))

    def __eq__(self, other):
        return self.parts == getattr(other, 'parts', None)

    def __hash__(self):
        return self.parts.__hash__()

    def __str__(self):
        return self.parts.geturl()

    def __repr__(self):
        return '<Href: {0}>'.format(str(self))
