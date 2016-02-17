from datetime import datetime


class Field(object):
    pass


class CharField(Field):

    def __init__(self, max_length=None, default=None, other_names=None):
        self.max_length = max_length
        self.other_names = other_names if other_names else []
        self.default = default

    def parse(self, input):
        if input is None:
            return self.default
        if isinstance(input, basestring):
            return input[:self.max_length]
        else:
            return str(input)[:self.max_length]


class DateTimeField(Field):

    def __init__(self, format="", default=None, other_names=None):
        # TODO: work on the default value of DateTimeField
        self.format = format
        self.other_names = other_names if other_names else []

    def parse(self, input):
        if input is None:
            return datetime.now()
        return datetime.strptime(input, self.format)


class ListField(Field):

    def __init__(self, content_type, default=None, other_names=None):
        self.content_type = content_type
        self.other_names = other_names if other_names else []
        self.default = default

    def parse(self, input):
        """
        This method generates a list from a string with the format of "word1, word2, word3"
        """
        if input and isinstance(input, basestring):
            return [self.content_type(a.strip()) for a in input.split(',')]
        elif isinstance(input, list):
            return [self.content_type(a) for a in input]
        else:
            return list()


class TextField(Field):

    def __init__(self, default=None):
        self.other_names = []
        self.default = default

    def parse(self, input):
        if input is None:
            return self.default
        return input
