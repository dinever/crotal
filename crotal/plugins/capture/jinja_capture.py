from jinja2 import nodes
from jinja2.ext import Extension


class CaptureExtension(Extension):
    """
    Generic HTML capture, inspired by Rails' capture helper

    In any template, you can capture an area of content and store it in a global
    variable:

    {% contentfor 'name_of_variable' %}
        blah blah blah
    {% endcontentfor %}

    To display the result
    {{ name_of_variable }}

    Multiple contentfor blocks will append additional content to any previously
    captured content.

    The context is global, and works within macros as well, so it's useful for letting macros define
    javascript or <head> tag content that needs to go at a particular position
    on the base template.

    Inspired by http://stackoverflow.com/questions/4292630/insert-javascript-at-top-of-including-file-in-jinja-2
    and http://api.rubyonrails.org/classes/ActionView/Helpers/CaptureHelper.html
    """
    tags = set(['contentfor'])

    def __init__(self, environment):
        super(CaptureExtension, self).__init__(environment)

    def parse(self, parser):
        """Parse tokens """
        tag = parser.stream.next()
        args = [parser.parse_expression()]
        body = parser.parse_statements(['name:endcontentfor'], drop_needle=True)
        return nodes.CallBlock(self.call_method('_capture', args),[], [], body).set_lineno(tag.lineno)

    def _capture(self, name, caller):
        if name not in self.environment.globals:
            self.environment.globals[name] = ''
        self.environment.globals[name] += caller()
        return ""