#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
    PinYin
    Author:cleverdeng
    E-mail:clverdeng@gmail.com
"""

__version__ = '0.9'
__all__ = ["PinYin"]

import os.path

class PinYin(object):
    def __init__(self):
        dir = os.path.dirname(os.path.abspath(__file__))
        self.word_dict = {}
        self.dict_file = dir + '/word.data'

    def load_word(self):
        if not os.path.exists(self.dict_file):
            raise IOError("NotFoundFile")

        with file(self.dict_file) as f_obj:
            for f_line in f_obj.readlines():
                try:
                    line = f_line.split('    ')
                    self.word_dict[line[0]] = line[1]
                except:
                    line = f_line.split('   ')
                    self.word_dict[line[0]] = line[1]


    def hanzi2pinyin(self, string=""):
        result = []
        if not isinstance(string, unicode):
            string = string.decode("utf-8")

        word = ''
        for char in string:
            key = '%X' % ord(char)
            if len(key) == 4:
                if word != '':
                    result.append(word)
                result.append(self.word_dict.get(key, char).split()[0][:-1].lower())
                word = ''
            elif key == '20':
                if word != '':
                    result.append(word)
                word = ''
            else:
                word = word + char.encode('utf-8')
        if word != '':
            result.append(word)

        return result


    def hanzi2pinyin_split(self, string="", split=""):
        result = self.hanzi2pinyin(string=string)
        if split == "":
            return result
        else:
            return split.join(result)


if __name__ == "__main__":
    pass
