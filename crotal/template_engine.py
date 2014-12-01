import os
import re
import yaml

from jinja2 import FileSystemLoader
from jinja2.environment import Environment

from crotal import settings
from crotal.models.pages import Page
from crotal.plugins.markdown.jinja_markdown import MarkdownExtension
from crotal.plugins.capture.jinja_capture import CaptureExtension


class Engine(object):
    """
    Engine uses Jinja2 Template Engine to render template files.
    """
    def __init__(self):
        self._j2_env = Environment(
            loader=FileSystemLoader(settings.TEMPLATES_DIR),
            trim_blocks=True,
            extensions=[MarkdownExtension, CaptureExtension])

    def render(self, layout_content, parameter):
        header = ''
        template_info = {}
        if layout_content.startswith('---'):
            get_header = re.compile(r'---[\s\S]*?---')
            header = get_header.findall(layout_content)[0]
            layout_content = layout_content.replace(header, '', 1)
            header = header.replace('---', '')
            template_info = yaml.load(header)
        if 'page' in parameter and isinstance(parameter['page'], Page):
            for i, p in template_info.iteritems():
                setattr(parameter['page'], i, p)
        else:
            parameter['page'] = Page('')
            for i, p in template_info.iteritems():
                setattr(parameter['page'], i, p)
        if 'layout' in template_info:
            parameter['layout'] = template_info['layout']
        rendered = self._j2_env.from_string(layout_content).render(**parameter)
        if header != '':
            parameter['content'] = rendered
            file_name = os.path.normpath(
                os.path.join(settings.TEMPLATES_DIR, '_layout/',
                             parameter['layout']))
            if not parameter['layout'].endswith('.html'):
                file_name += '.html'
            template_layout_content = open(file_name, 'r').read().decode('utf8')
            rendered = self.render(
                template_layout_content,
                parameter)
        return rendered
