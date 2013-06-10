#! /usr/bin/env python
#! coding: utf-8

BANNER = """PyCrack Shell
Type "help", "copyright", "credits" or "license" for more information.
"""

import __builtin__
import code
import rlcompleter, readline

def interact():

	class Completer(rlcompleter.Completer):
		expose = dir(__builtin__) + globals().keys()

		def global_matches(self, text):
			ret = [n for n in self.expose if "_" != n[0]]
			return [n for n in ret if n.startswith(text)]

		def attr_matches(self, text):
			_pos = text.rfind('.')
			expr, attr = text[:_pos], text[_pos+1:]

			obj = eval(expr)
			ret = [n for n in dir(obj) if "_" != n[0]]
			return ["%s.%s" %(expr, n) for n in ret if n.startswith(attr)]

	readline.set_completer(Completer().complete)
	readline.parse_and_bind("tab: complete")
	code.interact(banner=BANNER, local=globals())

if __name__ == "__main__":
	interact()
