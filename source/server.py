import os
import posixpath
import urllib
import BaseHTTPServer
from SimpleHTTPServer import SimpleHTTPRequestHandler
from unipath import Path

dir = Path(__file__).ancestor(2).absolute()

ROUTES = (
    ['', dir +'/_sites'],
)

class RequestHandler(SimpleHTTPRequestHandler):
    def translate_path(self, path):

        root = os.getcwd()

        for pattern, rootdir in ROUTES:
            if path.startswith(pattern):
                path = path[len(pattern):]
                root = rootdir
                break

        path = path.split('?',1)[0]
        path = path.split('#',1)[0]
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

def main():
    BaseHTTPServer.test(RequestHandler, BaseHTTPServer.HTTPServer)

if __name__ == '__main__':
    main()
