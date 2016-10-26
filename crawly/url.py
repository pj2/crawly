from urlparse import urlparse, urlunparse, urljoin
import tldextract


class URL(object):
    """A resource locator."""

    def __init__(self, raw):
        self.raw = raw
        self.parts = urlparse(self.raw)
        self.tld_extract = tldextract.extract(self.raw)

    @property
    def uri(self):
        """Return the resource section of the URL."""
        return (self.parts.path +
                (u'?' + self.parts.query if self.parts.query else u'') +
                (u'#' + self.parts.fragment if self.parts.fragment else u''))

    @property
    def scheme(self):
        """Return the scheme (protocol) of the URL or None."""
        return self.parts.scheme or None

    def is_relative(self):
        """Return True if this URL is relative."""
        return self.parts.netloc == ''

    def has_same_domain(self, other_url):
        """Return True if this and ``other_url`` share the same domain."""
        return self.parts.netloc and \
            self.tld_extract.domain == other_url.tld_extract.domain and \
            self.tld_extract.suffix == other_url.tld_extract.suffix

    def to_absolute(self, base_url):
        """Return an absolute URL based on ``base_url``."""
        if base_url.is_relative():
            raise ValueError('base_url must be absolute')

        return URL(urljoin(base_url.raw, self.raw))

    def __eq__(self, other):
        return self.parts == getattr(other, 'parts', None)

    def __hash__(self):
        return self.parts.__hash__()

    def __str__(self):
        return self.parts.geturl()

    def __repr__(self):
        return '<URL: {0}>'.format(str(self))
