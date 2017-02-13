#!/usr/bin/env python3.5
"""
Pretty (Simple) Output module
Aareon Sullivan - 2017
"""

form = ['\033[1;37;40m{0}', '\033[1;32;40m[SUCCESS] ', '\033[1;31;40m[ERROR]   ','\033[1;36;40m[INFO]    ',
        '\033[1;33;40m[WARNING] ']


def do_syn(string, var):
    print(form[var]+form[0].format(string))

def success(string):
    do_syn(string, 1)

def error(string):
    do_syn(string, 2)

def info(string):
    do_syn(string, 3)

def warning(string):
    do_syn(string, 4)