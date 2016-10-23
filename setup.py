from setuptools import setup, find_packages

setup(
    name='crawly',
    version='0.1',
    description='Web crawler',
    url='https://github.com/pj2/crawly',
    author='Joshua Prendergast',
    author_email='me@jprendergast.uk',
    install_requires=[
        'requests',
        'BeautifulSoup',
        'pytest',
    ]
)
