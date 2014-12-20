import os

BASE_DIR = os.getcwd()

CONFIG_PATH = os.path.join(os.getcwd(), '_config.yml')

POSTS_DIR = os.path.join('source', 'posts')

PAGES_DIR = os.path.join('source', 'pages')

PUBLISH_DIR = os.path.join(os.getcwd(), 'preview')

DEPLOY_DIR = os.path.join(os.getcwd(), 'deploy')

STATIC_DIR = os.path.join('static')

DB_PATH = os.path.join('db.json')

PRIVATE_DIR = os.path.join('.private')
