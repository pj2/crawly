import argparse
import logging
from .crawler import crawl
from .href import Href


if __name__ == '__main__':
    argp = argparse.ArgumentParser('crawly')
    argp.add_argument('url', help='target URL to crawl')
    argp.add_argument('-v', action='store_true', help='produce more output')
    argp.add_argument('-s', action='store_true', help='print out static files listing')

    args = argp.parse_args()
    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG if args.v else logging.ERROR)

    try:
        # TODO Check this is a valid URL
        crawl(Href(args.url), args.s)
    except (KeyboardInterrupt, EOFError):
        pass
