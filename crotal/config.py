import yaml
from unipath import Path

class Config():
    '''
    Read config from _config.yml
    '''
    def __init__(self, dir):
        self.dir = dir
        self.config_yml = open(self.dir + '/_config.yml', 'r').read()
        self.config = yaml.load(self.config_yml)
        for item in self.config:
            setattr(self, item, self.config[item])
