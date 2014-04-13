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

class Config():

    '''
    Read config from _config.yml
    '''

    def __init__(self, dir):
        self.dir = dir
        self.config_yml = open(
            os.path.join(
                self.dir,
                '_config.yml'),
            'r').read()
        self.config = yaml.load(self.config_yml)
        for item in self.config:
            setattr(self, item, self.config[item])
