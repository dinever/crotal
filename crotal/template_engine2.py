import os

from jinja2 import BaseLoader
from jinja2.environment import Environment

from crotal import logger
from crotal.plugins.markdown.jinja_markdown import MarkdownExtension


class TemplateLoader(BaseLoader):

    def __init__(self, config, mapping):
        self.mapping = mapping
        self.config = config

    def get_source(self, environment, template):
        template = os.path.join(self.config.templates_dir, template)
        if template in self.mapping:
            source = self.mapping[template].content
            return source, None, lambda: self.mapping[template].content
        else:
            logger.error("Template not found: {0}".format(template))
            source = "Missing Template: {0}".format(template)
            return source, None, lambda: source

    def list_templates(self):
        return sorted(self.mapping)


class TemplateEngine(object):
    """
    Engine uses Jinja2 Template Engine to render template files.
    """
    def __init__(self, config, template_mapping):
        self.config = config
        self._template_mapping = template_mapping
        self._template_loader = TemplateLoader(config, self._template_mapping)
        self._j2_env = Environment(
            loader=self._template_loader,
            trim_blocks=True,
            extensions=[MarkdownExtension]
        )

    def _layout_file(self, filename):
        if not filename.endswith('.html'):
            filename += '.html'
        return os.path.normpath(os.path.join(self.config.templates_dir,
                                      '_layout/', filename))

    def render(self, file_path, parameter):
        try:
            template = self._template_mapping[file_path]
        except KeyError, e:
            logger.error("Template not found: {0}".format(file_path))
            return "Template not found: {0}".format(file_path)
        while True:
            rendered = self.render_content(template.content, parameter)
            layout = template.layout
            if not layout:
                break
            else:
                parameter['content'] = rendered
                try:
                    template = self._template_mapping[self._layout_file(layout)]
                except KeyError, e:
                    logger.error("Template not found: {0}".format(file_path))
                    return "Template not found: {0}".format(file_path)
        return rendered

    def render_content(self, template_content, parameter):
        rendered = self._j2_env.from_string(template_content).render(**parameter)
        return rendered
