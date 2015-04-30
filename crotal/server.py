import os
import sys
import time
import posixpath
import urllib
import BaseHTTPServer
from threading import Thread
from SimpleHTTPServer import SimpleHTTPRequestHandler

from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

from crotal import logger
from crotal.site import Site
from crotal.config import Config
from crotal.version import __version__


LOGO = (
        "________________________________________",
        "|   ____ ____   ___ _____  _    _      |",
        "|  / ___|  _ \\ / _ \\_   _|/ \\  | |     |",
        "| | |   | |_) | | | || | / _ \\ | |     |",
        "| | |___|  _ <| |_| || |/ ___ \\| |___  |",
        "|  \____|_| \_\\\\___/ |_/_/   \\_\\_____| |",
        "|                                      |",
        "|          Version: {:<6s}             |".format(__version__),
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

        for pattern, root_dir in RequestHandler.routes:
            if path.startswith(pattern):
                path = path[len(pattern):]
                root = root_dir
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


class ServerThread(Thread):

    def __init__(self, config, port):
        self.config = config
        self.routes = (
            ['', config.publish_dir],
        )
        self.port = port
        self.help_info = (
            "Server started in `{0}`'".format(self.config.publish_dir),
            "To see your site, visit http://localhost:{0}".format(self.port),
            "To shut down Crotal, press <CTRL> + C at any time."
        )
        super(ServerThread, self).__init__()

    def run(self):
        del sys.argv[0]
        self._run(RequestHandler, BaseHTTPServer.HTTPServer)

    def _run(self, handler_class,
         server_class, protocol="HTTP/1.0"):
        """
        Test the HTTP request handler class.

        This runs an HTTP server on port 8000 (or the first command line
        argument).

        """

        server_address = ('', self.port)

        handler_class.protocol_version = protocol
        handler_class.routes = self.routes

        httpd = server_class(server_address, handler_class)

        for line in self.help_info:
            logger.info(line)
        print
        httpd.serve_forever()


class ChangeHandler(PatternMatchingEventHandler):
    patterns = ["*.*"]

    def __init__(self, config, site, ignore_patterns=None):
        self.config = config
        self.site = site
        super(ChangeHandler, self).__init__(ignore_patterns=ignore_patterns)

    def process(self, event):
        self.site.parse_single_file(event.src_path.decode('utf8'), event.event_type)

    def on_modified(self, event):
        logger.green_text('update', event.src_path.decode('utf8'))
        self.process(event)

    def on_created(self, event):
        logger.green_text('create', event.src_path.decode('utf8'))
        self.process(event)

    def on_deleted(self, event):
        logger.green_text('remove', event.src_path.decode('utf8'))
        self.process(event)


def start(port, path=os.getcwd()):
    if not path:
        sys.exit()
    site = Site(path)
    site.generate()
    config = Config(path)
    serverThread = ServerThread(config, port)
    serverThread.daemon = True
    serverThread.start()
    observer = Observer()
    for loader in site.loaders:
        for path in loader.path:
            observer.schedule(ChangeHandler(config, site, ignore_patterns=["*/.DS_Store"]),
                              path=os.path.join(config.base_dir, path), recursive=True)
    observer.start()
    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            logger.info('Server shutting down.')
            sys.exit()

