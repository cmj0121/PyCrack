#! /usr/bin/env python2
#! coding: utf-8
#! coding: big-5

import __builtin__
import atexit
import code
import readline
import os
import sys
import task

sys.path.append('/home/cmj/junkcode/')


class Color(object):
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
	banner = "CMJ's Python Interpreter (v1.1)\n" \
			 "CopyRight (c) 2013 [cmj0121@gmail.com]. All rights resolved.\n"
	ps1 = ">>> "
	ps2 = "... "
	def __init__(self, theme):
		if theme == "default":
			theme = self.defaultTheme()

		for key in ("ps1", "ps2", "banner"):
			setattr(sys, key, "\001%s\002%s\001%s\002" %(theme[key], getattr(self, key), Color.normal))
	def defaultTheme(self):
		""" Change the theme for the interact interpreter """
		return {"ps1": "%s%s" %(Color.cyan, Color.bold),"ps2":Color.normal, "banner": Color.yellow}

def clear():
	print Color.normal
	os.system('clear')
def interact():
	def Completer(text, stat):
		def filterLv(key):
			global filterLevel

			if "private" == filterLevel:
				return True
			elif "protect" == filterLevel:
				if key.startswith("__") and key.endswith("__"): return False
				else: return True
			else:
				if "_" in key[0]: return False
				else: return True
		def global_matches(text):
			expose = dir(__builtin__) + globals().keys()
			ret = filter(filterLv, expose)
			return [n for n in ret if n.startswith(text)]
		def attr_matches(text):
			_pos = text.rfind('.')
			expr, attr = text[:_pos], text[_pos+1:]

			obj = eval(expr)
			ret = filter(filterLv, dir(obj))
			return ["%s.%s" %(expr, n) for n in ret if n.startswith(attr)]
		def path_matches(text):
			path = [n for n in text.split('/')]
			path, attr = "%s/" %"/".join(path[:-1]), path[-1]

			return ["%s%s" %(path, n) for n in os.listdir(path) if n.startswith(attr)]
		if text.startswith('.') or text.startswith('/'):
			ret = path_matches(text)
		elif '.' not in text:
			ret = global_matches(text)
		else:
			ret = attr_matches(text)

		try:
			return ret[stat]
		except IndexError:
			return None

	Theme("default")
	delims = readline.get_completer_delims().replace('/','')
	readline.set_completer_delims(delims)
	readline.set_completer(Completer)
	readline.parse_and_bind("tab: complete")
	readline.parse_and_bind("C-p: complete")
	code.interact(banner=sys.banner, local=globals())
def selftest():
	import doctest
	doctest.testmod()
def exit_interact():
	print "Goodbye..."

filterLevel = "public"
CURRENT_JOB = task.Task()
atexit.register(exit_interact)
atexit.register(CURRENT_JOB.DEL)
if __name__ == "__main__":
	interact()
