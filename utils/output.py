#!/usr/bin/env python3.5
"""
Pretty (Simple) Output module
Aareon Sullivan - 2017
"""
from utils import parsing

config = parsing.parse_json('config.json')["logging"]

color = ['\033[1;31;40m', '\033[1;33;40m', '\033[1;32;40m', '\033[1;36;40m']

message = ['[ERROR]   ', '[WARNING] ', '[SUCCESS] ', '[INFO]    ']


def do_syn(string, var):
    if var <= config["print_level"]:
        print(color[var]+message[var]+'\033[1;37;40m{0}'.format(string))

    if var <= config["file_level"]:
        with open(config["file"], "a") as f:
            f.write(message[var]+'{0}'.format(string) + "\n")


def error(string):
    do_syn(string, 0)


def warning(string):
    do_syn(string, 1)


def success(string):
    do_syn(string, 2)


def info(string):
    do_syn(string, 3)



