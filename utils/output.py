#!/usr/bin/env python3.5
"""
Pretty (Simple) Output module
Aareon Sullivan - 2017
"""

form = ['\033[1;37;40m{0}', '\033[1;32;40m[SUCCESS] ', '\033[1;31;40m[ERROR]   ','\033[1;36;40m[INFO]    ',
        '\033[1;33;40m[WARNING] ']


class PrOut:
    def doSyn(self, string, var):
        print(form[var]+form[0].format(string))

    def success(self, string):
        self.doSyn(string, 1)

    def error(self, string):
        self.doSyn(string, 2)

    def info(self, string):
        self.doSyn(string, 3)

    def warning(self, string):
        self.doSyn(string, 4)