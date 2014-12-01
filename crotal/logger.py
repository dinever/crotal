from clint.textui import colored

def info(message):
    print colored.green('[info] ') + message

def warning(message):
    print colored.yellow('[warning] ') + message

def error(message):
    print colored.red('[error] ') + message

def success(message):
    print colored.blue('[success] ') + message

def yellow_text(info, message=''):
    print colored.yellow('[' + info + '] ') + message

def red_text(info='', message=''):
    if info:
        print colored.red('[' + info + '] ') + message
    else:
        print colored.red(message)

def blue_text(info='', message=''):
    if info:
        print colored.blue('[' + info + '] ') + message
    else:
        print colored.blue(message)

def green_text(info='', message=''):
    if info:
        print colored.green('[' + info + '] ') + message
    else:
        print colored.green(message)

def info_input(message):
    return raw_input(colored.green('[' + message + ']: '))
