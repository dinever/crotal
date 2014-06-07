import os
import re
import yaml

from jinja2 import FileSystemLoader
from jinja2.environment import Environment

from crotal.plugins.markdown.jinja_markdown import MarkdownExtension
from crotal.config import config


class Engine:
    '''
    Engine uses Jinja2 Template Engine to render template files.
    '''
    def __init__(self):
        self.j2_env = Environment(
            loader=FileSystemLoader(config.templates_dir),
            trim_blocks=True,
            extensions=[MarkdownExtension])

    def render(self, layout_content, parameter):
        header = ''
        template_info = {}
        if layout_content.startswith("---"):
            get_header = re.compile(r'---[\s\S]*?---')
            header = get_header.findall(layout_content)[0]
            layout_content = layout_content.replace(header, '', 1)
            header = header.replace('---', '')
            template_info = yaml.load(header)
        parameter = dict(parameter.items() + template_info.items())
        rendered = self.j2_env.from_string(layout_content).render(**parameter)
        if header != '':
            parameter['content'] = rendered
            fname = os.path.normpath(
                os.path.join(config.templates_dir,
                    '_layout/',
                    parameter['layout']))
            if not parameter['layout'].endswith(".html"):
                fname += '.html'
            template_layout_content = open(fname, 'r').read().decode('utf8')
            rendered = self.render(
                template_layout_content,
                parameter)
        return rendered
