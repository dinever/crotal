from markdown import markdown
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
from datetime import datetime
import re
import settings
from .category import Categories


class Posts():
    def __init__(self):
        """docstring for __init__"""
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
        self.content = content.replace(self.header, '')
        self.save_html()
        self.title = self.save_info('title').replace('"','')
        self.pub_time = datetime.strptime(self.save_info('date'),"%Y-%m-%d %H:%M")
        self.author = settings.author
        try:
            self.categories = self.save_info('categories').split(' ')
        except:
            pass
        try:
            self.slug = self.save_info('slug')
        except:
            from _plugins.pinyin.pinyin import PinYin
            slug = PinYin()
            slug.load_word()
            self.slug = slug.hanzi2pinyin_split(string= self.title, split="-")
        self.url = '/blog/'+ self.pub_time.strftime("%G") + '/' + self.pub_time.strftime("%m") + '/' + self.pub_time.strftime("%d") + '/' + self.slug + '/'

    def save_info(self, keyword):
        return re.compile(r'(?<=' + keyword + ':\s).*?(?=\n)').findall(self.header)[0]

    def save_html(self):
        f = self.content
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
            find_new = highlight(find_new, lexer, HtmlFormatter(linenos=True))
            f = f.replace(find, find_new)
        self.html = markdown(f)
        self.front_html = markdown(f.split('<!--more-->')[0])
