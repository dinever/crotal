import yaml
import os.path
import os

from crotal import reporter

class config(object):
    version = '0.7.0'

try:
    config_yml = open(os.path.join(os.getcwd(), '_config.yml'), 'r').read()
except Exception as e:
    reporter.no_site_dected()

config_dict = yaml.load(config_yml)
for item in config_dict:
    setattr(config, item, config_dict[item])

setattr(config, 'base_dir', os.getcwd())
setattr(config, 'config_path', os.getcwd())
setattr(config, 'posts_dir', os.path.join('source', 'posts'))
setattr(config, 'pages_dir', os.path.join('source', 'pages'))
setattr(config, 'publish_dir', os.path.join(config.base_dir, 'publish'))
setattr(config, 'deploy_dir', os.path.join(config.base_dir, 'deploy'))
setattr(config, 'static_dir', os.path.join('static'))
setattr(config, 'theme_dir', os.path.join('themes', config.theme))
setattr(config, 'templates_dir', os.path.join(config.theme_dir, 'public'))
setattr(config, 'theme_static_dir', os.path.join(config.theme_dir, 'static'))
setattr(config, 'db_path', os.path.join('db.json'))
setattr(config, 'private_dir', os.path.join('.private'))
