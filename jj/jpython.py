#! /usr/bin/env python2
#! coding: utf-8
#! coding: big-5

"""
Customize Python Interpreter

Function:
	1- Auto-Complete
	2- Theme Support
"""

import __builtin__
import code
import readline
import os
import sys
from jj import utils

## Match for prefix
def global_matches(text):
	"""
	Match for global variable

	>>> ["sys"] == global_matches("sy")
	True
	"""
	expose = dir(__builtin__) + globals().keys()
	ret = filter(lambda x: not (x and "_" == x[0]), expose)
	return [n for n in ret if n.startswith(text)]
def attr_matches(text):
	"""
	Match for object's attribute

	>>> ["sys.exc_clear", "sys.exc_info", "sys.exc_type"] == attr_matches("sys.exc_")
	True
	"""
	_pos = text.rfind('.')
	expr, attr = text[:_pos], text[_pos+1:]

	obj = eval(expr)
	ret = filter(lambda x: not (x and "_" == x[0]), dir(obj))
	return ["%s.%s" %(expr, n) for n in ret if n.startswith(attr)]
def path_matches(text):
	""" Search for path """
	path = [n for n in text.split('/')]
	path, attr = "%s/" %"/".join(path[:-1]), path[-1]

	return ["%s%s" %(path, n) for n in os.listdir(path) if n.startswith(attr)]
def interact(PS1, PS2, BANNER, *arg, **kwarg):
	def Completer(text, stat):
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
	@utils.regExitCallback
	def exit_interact():
		""" Clean all when exit """
		
		print "Goodbye..."

	## Compatible for Mac OS since Mac OS ship libedit for readline
	if "libedit" in readline.__doc__:
		import rlcompleter
		readline.parse_and_bind("bind ^I rl_complete")
	else:
		readline.parse_and_bind("tab: complete")

	## Change PS
	sys.ps1, sys.ps2 = PS1, PS2
	delims = readline.get_completer_delims().replace('/','')
	readline.set_completer_delims(delims)
	readline.set_completer(Completer)


	## Run Interpreter
	code.interact(banner=BANNER, local=globals())

if __name__ == "__main__":
	from jj.conf import DEFAULT_CONF as _C
	interact(**_C)
