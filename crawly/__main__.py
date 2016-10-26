import sys
import argparse
import logging
from .crawler import Crawler
from .url import URL


if __name__ == '__main__':
    argp = argparse.ArgumentParser('crawly')
    argp.add_argument('url', help='target URL to crawl e.g. http://www.google.com')
    argp.add_argument('-v', action='store_true', help='produce more output')
    argp.add_argument('-s', action='store_true', help='print out static files listing')

    args = argp.parse_args()
    url = URL(args.url)

    if url.is_relative() or not url.parts.scheme:
        print 'invalid url'
        sys.exit(1)

    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG if args.v else logging.ERROR)

    try:
        Crawler(url, args.s).crawl()
    except (KeyboardInterrupt, EOFError):
        pass
