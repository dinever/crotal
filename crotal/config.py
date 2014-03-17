import yaml
import os.path


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
