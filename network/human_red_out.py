#!/usr/bin/python3

from datetime import datetime
from termcolor import cprint


def process(_input):
    _input = _input.split()
    # convert time to human output
    t_epoch = _input[0]
    time = '{:%I:%M:%S %P} - '.format(datetime.fromtimestamp(float(t_epoch)))
    # check for error messages
    if _input[3].endswith(':') and 'HTTP' in _input[4]:
        _type = 'error'
    elif _input[3] == 'redsocks':
        _type = 'control'
    else:
        _type = 'generic'
    return (time + ' '.join(_input[3:]), _type)


def prettify(_output, _type):
    if _type == 'generic':
        print(_output)
    elif _type == 'error':
        cprint(_output, 'grey', 'on_red')
    elif _type == 'control':
        cprint(_output, 'blue')
    return


if __name__ == '__main__':
    try:
        while True:
            _input = input()
            _output, _type = process(_input)
            prettify(_output, _type)
    except KeyboardInterrupt:
        exit(0)
