import os

from mako.template import Template
from mako.lookup import TemplateLookup
from mako import exceptions

from crotal import logger


class Lookup(TemplateLookup):

    def adjust_uri(self, uri, relativeto):
        """
        Override `adjust_uri` so that we can locate template from absolute uri.
        """
        self.calling_uri = relativeto
        return uri

    def get_template(self, uri):
        """
        Override `get_template` so that it returns a `error template` when lookup
        failed to locate the template.
        """
        uri = uri.replace('/', os.sep)
        if uri in self._collection:
            return self._collection[uri]
        else:
            error_message = "template not found: {0}, calling by: {1}".format(uri, self.calling_uri)
            logger.error(error_message)
            error_template = Template(text=error_message)
            self.put_template(uri, Template(text=error_message))
            return error_template


class TemplateLoader(object):

    def __init__(self, config, mapping):
        """
        This is a wrap for the Lookup object.
        """
        self.mapping = mapping
        self.config = config
        self.lookup = Lookup(output_encoding='utf-8', filesystem_checks=False)
        for template in self.mapping:
            self.lookup.put_string(os.path.relpath(template.path, self.config.templates_dir), template.content)

    def get_template(self, file_path):
        return self.lookup.get_template(os.path.relpath(file_path, self.config.templates_dir))

    def list_templates(self):
        return sorted(self.mapping)


class TemplateEngine(object):
    """
    Engine uses Mako Template Engine to render template files.
    """
    def __init__(self, config, template_mapping):
        self.config = config
        self._template_mapping = template_mapping
        self._template_loader = TemplateLoader(config, self._template_mapping)

    def _layout_file(self, filename):
        if not filename.endswith('.html'):
            filename += '.html'
        return os.path.normpath(os.path.join(self.config.templates_dir,
                                             '_layout/', filename))

    def render(self, file_path, parameter):
        template = self._template_loader.get_template(file_path)
        try:
            return template.render(**parameter)
        except:
            logger.error("Template Error: {0}".format(file_path))
            return exceptions.html_error_template().render()
