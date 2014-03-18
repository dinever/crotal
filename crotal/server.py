import os
import time
import posixpath
import urllib
import BaseHTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler
from threading import Thread

dir = os.getcwd()


class RequestHandler(SimpleHTTPRequestHandler):

    def translate_path(self, path):

        ROUTES = (
            ['', dir + '/_sites'],
        )
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
        BaseHTTPServer.test(RequestHandler, BaseHTTPServer.HTTPServer)


def main():
    serverThread = ServerThread()
    serverThread.daemon = True
    serverThread.start()
    while True:
        time.sleep(1)


if __name__ == '__main__':
    main()
