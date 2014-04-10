#! /usr/bin/env python
#! coding: utf-8

from conf import DEFAULT_CONF as _C
import jpython
import sys

__all__ = ["dispatch", "jpython"]
class Dispatch(object):
	"""	Command dispatch """
	def __init__(self):
		self.callback_fn = {}
	def __call__(self):
		""" Run dispatch runtine """
		import sys

		arg = sys.argv[1:]
		if not arg:
			return self.helpMsg()
		for _ in self.callback_fn:
			if _ == arg[0]:
				self.callback_fn[_]["fn"](*arg[1:], **_C)
				break
		else:
			self.helpMsg()
	def addArgument(self, name, callback_fn, help=""):
		self.callback_fn.update({name: {
			"fn": callback_fn, "help": help }
		})
		return self
	def test(self, *arg, **kwarg):
		""" Run doctest """
		import doctest

		_MODULE_ = (conf, jpython)
		print "Run doctest... ",
		doctest.testmod()
		for _ in _MODULE_: doctest.testmod(_)
		print "Success!"
	def helpMsg(self):
		""" Show help message """
		print "Usage: "
		for _ in sorted(self.callback_fn.keys()):
			FORMAT = "  {PROG_NAME} {0:<7}    {1}"
			FORMAT = FORMAT.format(_, self.callback_fn[_]["help"], **_C)
			print FORMAT
		return 1
dispatch = Dispatch()
dispatch.addArgument("jpython", jpython.interact,
	help="Customize Python interpreter")
dispatch.addArgument("doctest", dispatch.test,
	help="Run self-test")
