# crawly
Python web crawler

# Usage
    cd crawly # From the project root...

    # Installation
    virtualenv env
    . env/bin/activate
    pip install .

    crawly https://google.com   # Crawl google.com and output links
    crawly https://yahoo.com -s # Crawl yahoo.com and output links and static files

    pip install pytest pytest-pythonpath mock
    py.test                     # Run the tests

# Design

The crawler is designed to download web pages continually using a breadth-first search. Visited pages are remembered and skipped to avoid recursion.

The following aspects were an interesting challenge:
* *URLs*. A link in a website may be absolute or relative. The link might follow a redirect chain, also. These all factor into determining the eventual destination of an <a> link.
* *reliability*. The Internet is not reliable so the crawler must account for that.
* *memory*. A domain's size is unbounded and it may be difficult to store all visited URLs as a result. One solution is to set a hard limit on the amount of pages visited. Another is to evict URLs after the set grows to a certain size.

The crawler's speed could be improved by using threading.
