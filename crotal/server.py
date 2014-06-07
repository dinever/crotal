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

from crotal.config import config
from crotal.controller import Controller
from crotal.generator import Generator
from crotal import reporter

current_dir = config.base_dir

css_dir = os.path.join(current_dir, 'themes', config.theme, 'static', 'css')
js_dir = os.path.join(current_dir, 'themes', config.theme, 'static', 'js')

ROUTES = (
    ['/css', css_dir],
    ['/js', js_dir],
    ['', config.publish_dir],
)

generator = Generator()
controller = Controller()

class RequestHandler(SimpleHTTPRequestHandler):

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

class ServerThread(Thread):

    def run(self):
        del sys.argv[0]
        BaseHTTPServer.test(RequestHandler, BaseHTTPServer.HTTPServer)

class ChangeHandler(PatternMatchingEventHandler):
    patterns = ["*.html", "*.markdown", "*.md"]

    def __init__(self):
        super(ChangeHandler, self).__init__()

    def process(self, event):
        generator.generate_site(silent=True)

    def on_modified(self, event):
        reporter.info_report(event.src_path, info='update')
        self.process(event)

    def on_created(self, event):
        reporter.info_report(event.src_path, info='create')
        self.process(event)

    def on_deleted(self, event):
        reporter.info_report(event.src_path, info='delete')
        self.process(event)

def main():
    generator.generate_site(silent=True)
    serverThread = ServerThread()
    serverThread.daemon = True
    serverThread.start()
    observer = Observer()
    observer.schedule(ChangeHandler(), path=config.posts_dir, recursive=True)
    observer.schedule(ChangeHandler(), path=config.pages_dir, recursive=True)
    observer.schedule(ChangeHandler(), path=config.templates_dir, recursive=True)
    observer.start()
    reporter.info_report('Server started.')
    while True:
        time.sleep(1)


if __name__ == '__main__':
    main()
