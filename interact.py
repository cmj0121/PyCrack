#! /usr/bin/env python2
#! coding: utf-8

BANNER = """PyCrack Shell
Type "help", "copyright", "credits" or "license" for more information.
"""

import __builtin__
import code
import rlcompleter, readline
import os

from modules import *


clear = lambda: os.system('clear')
def interact():
	class Completer(rlcompleter.Completer):
		def global_matches(self, text):
			expose = dir(__builtin__) + globals().keys()
			ret = [n for n in expose if "_" != n[0]]
			return [n for n in ret if n.startswith(text)]

		def attr_matches(self, text):
			_pos = text.rfind('.')
			expr, attr = text[:_pos], text[_pos+1:]

			obj = eval(expr)
			ret = [n for n in dir(obj) if "_" != n[0]]
			return ["%s.%s" %(expr, n) for n in ret if n.startswith(attr)]

	readline.set_completer(Completer().complete)
	readline.parse_and_bind("tab: complete")
	readline.parse_and_bind("C-p: complete")
	code.interact(banner=BANNER, local=globals())

if __name__ == "__main__":
	interact()
