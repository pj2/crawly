# crawly
Python web crawler

# Usage
    cd crawly # From the project root

    # Installation
    virtualenv env
    . env/bin/activate
    pip install .

    crawly https://google.com   # Crawl google.com and output links
    crawly https://yahoo.com -s # Crawl yahoo.com and output links and static files
