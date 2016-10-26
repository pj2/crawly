from setuptools import setup, find_packages

setup(
    name='crawly',
    version='0.1',
    description='Web crawler',
    url='https://github.com/pj2/crawly',
    author='Joshua Prendergast',
    author_email='me@jprendergast.uk',
    packages=find_packages(),
    install_requires=[
        'requests',
        'BeautifulSoup',
        'tldextract',
        'bs4',
    ],
    tests_require=[
        'pytest',
        'pytest-pythonpath',
        'mock',
    ],
    entry_points={
        'console_scripts': [
            'crawly = crawly.__main__:main',
        ],
    },
)
