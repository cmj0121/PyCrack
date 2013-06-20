#! /usr/bin/env python2
#! coding: utf-8

import __builtin__
import code
import rlcompleter, readline
import os
import sys
sys.path.append('/home/cmj/junkcode/')

from modules import *


class Color:
	normal = "\033[0m"
	black = "\033[30m"
	red = "\033[31m"
	green = "\033[32m"
	yellow = "\033[33m"
	blue = "\033[34m"
	purple = "\033[35m"
	cyan = "\033[36m"
	grey = "\033[37m"

	bold = "\033[1m"
	uline = "\033[4m"
	blink = "\033[5m"
	invert = "\033[7m"
class Theme(object):
	banner = "CMJ's Python Interpreter (v1.0)\n" \
			 "CopyRight (c) 2013 [cmj0121@gmail.com]. All rights resolved.\n"
	ps1 = ">>> "
	ps2 = "... "
	def __init__(self, theme):
		if theme == "default":
			theme = self.defaultTheme()

		for key in ("ps1", "ps2", "banner"):
			setattr(sys, key, "%s%s%s" %(theme[key], getattr(self, key), Color.normal))
	def defaultTheme(self):
		""" Change the theme for the interact interpreter """
		return {"ps1": "%s%s" %(Color.cyan, Color.bold),"ps2":Color.normal, "banner": Color.yellow}

def clear():
	print Color.normal
	os.system('clear')
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

	Theme("default")
	readline.set_completer(Completer().complete)
	readline.parse_and_bind("tab: complete")
	readline.parse_and_bind("C-p: complete")
	code.interact(banner=sys.banner, local=globals())

if __name__ == "__main__":
	interact()
