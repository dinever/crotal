import os

from mako.lookup import TemplateLookup


class Lookup(TemplateLookup):

    def adjust_uri(self, uri, relativeto):
        return uri


class TemplateLoader(object):

    def __init__(self, config, mapping):
        self.mapping = mapping
        self.config = config
        self.lookup = Lookup(output_encoding='utf-8', filesystem_checks=False)
        for path, template in mapping.iteritems():
            self.lookup.put_string(os.path.relpath(path, self.config.templates_dir), template.content)

    def get_template(self, file_path):
        return self.lookup.get_template(os.path.relpath(file_path, self.config.templates_dir))

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

    def _layout_file(self, filename):
        if not filename.endswith('.html'):
            filename += '.html'
        return os.path.normpath(os.path.join(self.config.templates_dir,
                                             '_layout/', filename))

    def render(self, file_path, parameter):
        template = self._template_loader.get_template(file_path)
        return template.render(**parameter)
