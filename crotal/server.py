import os
import sys
import time
import posixpath
import urllib
import BaseHTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler
from threading import Thread

from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

from crotal import settings
from crotal.core import Command
from crotal import logger
from crotal.version import __version__

ROUTES = (
    ['', settings.PUBLISH_DIR],
)

LOGO = (
        "________________________________________",
        "|   ____ ____   ___ _____  _    _      |",
        "|  / ___|  _ \\ / _ \\_   _|/ \\  | |     |",
        "| | |   | |_) | | | || | / _ \\ | |     |",
        "| | |___|  _ <| |_| || |/ ___ \\| |___  |",
        "|  \____|_| \_\\\\___/ |_/_/   \\_\\_____| |",
        "|                                      |",
        "|          Version: {:<6s}             |".format(__version__),
        "|          Author: Dinever             |",
        "|______________________________________|",
        )


class RequestHandler(SimpleHTTPRequestHandler):

    def log_request(self, code='-', size='-'):
        pass

    def log_message(self, format, *args):
        if args[0] == 404:
            logger.yellow_text('404', message='Can not get file: {0}'.format(self.path))

    def translate_path(self, path):

        root = os.getcwd()

        for pattern, rootdir in ROUTES:
            if path.startswith(pattern):
                path = path[len(pattern):]
                root = rootdir
                break

        path = path.split('?', 1)[0]
        path = path.split('#', 1)[0]
        path = posixpath.normpath(urllib.unquote(path))
        words = path.split('/')
        words = filter(None, words)

        path = root
        for word in words:
            drive, word = os.path.splitdrive(word)
            head, word = os.path.split(word)
            if word in (os.curdir, os.pardir):
                continue
            path = os.path.join(path, word)

        return path

def test(HandlerClass,
         ServerClass, protocol="HTTP/1.0"):
    """Test the HTTP request handler class.

    This runs an HTTP server on port 8000 (or the first command line
    argument).

    """

    if sys.argv[1:]:
        port = int(sys.argv[1])
    else:
        port = 8000
    server_address = ('', port)

    HandlerClass.protocol_version = protocol
    httpd = ServerClass(server_address, HandlerClass)

    sa = httpd.socket.getsockname()
    for line in LOGO:
        logger.info(line)
    print


    HELP_INFO = (
        "Server started in `{0}`'".format(settings.PUBLISH_DIR),
        "To see your site, visit http://localhost:{0}".format(port),
        "To shut down Crotal, press <CTRL> + C at any time."
    )
    for line in HELP_INFO:
        logger.info(line)
    print
    httpd.serve_forever()

class ServerThread(Thread):

    def run(self):
        del sys.argv[0]
        test(RequestHandler, BaseHTTPServer.HTTPServer)

class ChangeHandler(PatternMatchingEventHandler):
    patterns = ["*.*"]

    def __init__(self, settings):
        self.config = settings
        super(ChangeHandler, self).__init__()

    def process(self, event):
        Command.generate(silent=True)

    def on_modified(self, event):
        logger.green_text('update', event.src_path)
        self.process(event)

    def on_created(self, event):
        logger.green_text('[create] {0}'.format(event.src_path))
        self.process(event)

    def on_deleted(self, event):
        logger.green_text('[remove] {0}'.format(event.src_path))
        self.process(event)

def main(settings):
    Command.generate(silent=True)
    serverThread = ServerThread()
    serverThread.daemon = True
    serverThread.start()
    observer = Observer()
    observer.schedule(ChangeHandler(settings), path=settings.POSTS_DIR, recursive=True)
    observer.schedule(ChangeHandler(settings), path=settings.PAGES_DIR, recursive=True)
    observer.schedule(ChangeHandler(settings), path=settings.TEMPLATES_DIR, recursive=True)
    observer.schedule(ChangeHandler(settings), path=settings.THEME_STATIC_DIR, recursive=True)
    observer.start()
    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            logger.info('Server shutting down.')
            sys.exit()


if __name__ == '__main__':
    main()
