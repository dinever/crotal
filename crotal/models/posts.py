from markdown import markdown
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
from datetime import datetime
import re
from .category import Categories

class Posts():
    def __init__(self, config):
        self.config = config
        self.header = ''
        self.title = ''
        self.pub_time = datetime
        self.categories = []
        self.content = ''
        self.html = ''
        self.front_html = ''
        self.author = ''
        self.slug = ''
        self.url = ''

    def save(self, content):
        get_header = re.compile(r'---[\s\S]*?---')
        self.header = get_header.findall(content)[0]
        self.content = content.replace(self.header, '', 1)
        self.save_html()
        self.title = self.save_info('title').replace('"','')
        self.pub_time = datetime.strptime(self.save_info('date'),"%Y-%m-%d %H:%M")
        self.author = self.config.author
        try:
            self.categories = self.save_info('categories').split(' ')
        except:
            pass
        try:
            self.slug = self.save_info('slug')
        except:
            from crotal.plugins.pinyin.pinyin import PinYin
            slug = PinYin()
            slug.load_word()
            self.slug = slug.hanzi2pinyin_split(string= self.title, split="-")
        for item in self.config.permalink.split('/'):
            if item.startswith(':'):
                self.url = self.url + '/' + self.escape_keywords(item.replace(':',''))
            else:
                self.url = self.url + '/' + item

    def escape_keywords(self, word):
        return {
            'year':self.pub_time.strftime('%G'),
            'month':self.pub_time.strftime('%m'),
            'day':self.pub_time.strftime('%d'),
            'title':self.slug,
        }[word]

    def save_info(self, keyword):
        return re.compile(r'(?<=' + keyword + ':\s).*?(?=\n)').findall(self.header)[0]

    def code_highlight(self, content):
        a = re.compile(r'\`\`\`[\s\S]*?\n\`\`\`')
        finds = a.findall(self.content)
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
            content = content.replace(find, find_new)
        return content

    def save_html(self):
        content = self.code_highlight(self.content)
        self.html = markdown(content)
        self.front_html = markdown(content.split('<!--more-->')[0])
