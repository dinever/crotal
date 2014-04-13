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

from crotal.config import Config
from crotal.controller import Controller
from crotal import reporter

current_dir = os.getcwd()
config = Config(current_dir)

css_dir = os.path.join(current_dir, 'themes', config.theme, 'static', 'css')
js_dir = os.path.join(current_dir, 'themes', config.theme, 'static', 'js')
posts_dir = os.path.join(current_dir, 'source', 'posts')
pages_dir = os.path.join(current_dir, 'source', 'pages')

ROUTES = (
    ['/css', css_dir],
    ['/js', js_dir],
    ['', current_dir + '/_sites'],
)

controller = Controller(config, current_dir)
controller.copy_static_files()

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

class PostsHandler(PatternMatchingEventHandler):
    patterns = ["*.html", "*.markdown", "*.md"]

    def process(self, event):
        controller.get_posts()
        controller.get_pages()
        controller.get_templates()
        controller.save()
        controller.save_posts()
        controller.save_db()
        print event.src_path, event.event_type  # print now only for degug

    def on_modified(self, event):
        self.process(event)

    def on_created(self, event):
        self.process(event)

    def on_deleted(self, event):
        self.process(event)


class PagesHandler(PatternMatchingEventHandler):
    patterns = ["*.html", "*.markdown", "*.md"]

    def process(self, event):
        print event.src_path, event.event_type  # print now only for degug

    def on_modified(self, event):
        self.process(event)

    def on_created(self, event):
        self.process(event)

    def on_deleted(self, event):
        self.process(event)


def main():
    serverThread = ServerThread()
    serverThread.daemon = True
    serverThread.start()
    observer = Observer()
    observer.schedule(PostsHandler(), path=posts_dir, recursive=True)
    observer.schedule(PagesHandler(), path=pages_dir, recursive=True)
    observer.start()
    reporter.info_report('Server started.')
    while True:
        time.sleep(1)


if __name__ == '__main__':
    main()
