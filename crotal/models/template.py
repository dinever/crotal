# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

from crotal.models import Model
from crotal.models.fields import *


class Template(Model):
    """
    Model `Template` for templates of the site.

    Attributes:

    ``PATH``: The relative path where this model is related to, please
    use the relative path to this script.

    ``path``: The path of the template file.

    ``layout``: The layout of the template file, which indicates the way
    that the template is going to be displayed.

    ``content``: The content of the template as a string.
    """
    PATH = ['themes/{theme}/public/']

    path = CharField()
    layout = CharField()
    content = TextField()

    @classmethod
    def parse_content(cls, file_path, content, config):
        """
        Overriding the ``parse_content`` of ``models.BaseModel`` and returns
        a Template object.

        :param file_path: Path of the designated file.
        :param content: Content of the file as a string.
        :param config: A configuration instance.
        :return: A template object.
        """
        attributes = {}
        attributes['content'] = content
        attributes['path'] = file_path
        cls.parse_attributes(file_path, config, attributes)
        return cls(**attributes)
