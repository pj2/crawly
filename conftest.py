import os
from threading import Thread
import SimpleHTTPServer
import SocketServer
import pytest


class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass


@pytest.fixture
def site(monkeypatch):
    """Runs a local server on a random port."""
    site_root = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'tests',
        'site'
    )
    monkeypatch.chdir(site_root)

    server = ThreadedTCPServer(
        ('localhost', 0), SimpleHTTPServer.SimpleHTTPRequestHandler)
    thread = Thread(target=server.serve_forever)
    thread.daemon = True

    try:
        thread.start()
        yield 'http://localhost:{0}/'.format(server.socket.getsockname()[1])
    finally:
        server.shutdown()
        server.server_close()
        thread.join(10)
