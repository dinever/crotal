from jinja2 import nodes
from jinja2.ext import Extension
from markdown import markdown
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
import re


class MarkdownExtension(Extension):
    tags = set(['markdown'])

    def __init__(self, environment):
        super(MarkdownExtension, self).__init__(environment)

    def parse(self, parser):
        lineno = parser.stream.next().lineno
        body = parser.parse_statements(['name:endmarkdown'], drop_needle=True)
        return nodes.CallBlock(self.call_method('_cache_support'),
                               [], [], body).set_lineno(lineno)

    def _cache_support(self, caller):
        f = caller()
        a = re.compile(r'\`\`\`[\s\S]*?\n\`\`\`')
        finds = a.findall(caller())
        for find in finds:
            b = re.compile(r'(?<=\`\`\`).*?(?=\n)')
            type = b.findall(find)[0].encode('utf-8')
            type = type.replace('\r', '')
            find_new = find.replace('```' + type, '')
            find_new = find_new.replace('```', '')
            if type != '':
                lexer = get_lexer_by_name(type, stripall=True)
            else:
                lexer = get_lexer_by_name('text', stripall=True)
            find_new = highlight(find_new, lexer, HtmlFormatter(linenos=False))
            f = f.replace(find, find_new)
        return markdown(f)
