#! /usr/bin/env python
#! coding: utf-8

def CLI(func):
	""" Command-line Interface

		Automatically show the usage when run the function.
	"""
	import sys 
	def HELP():
		nr = func.func_code.co_argcount
		_ = func.func_defaults
		arg = func.func_code.co_varnames[:nr]
		if _:
			arg, kwarg = arg[:-1*len(_)], zip(arg[-1*len(_):],_)
		else:
			kwarg = {}
		print sys.argv[0],
		print " ".join(['[%s]' %_ for _ in arg]),
		print " ".join(["[--%s=%s]" %(x, y) for x, y in kwarg]), 
		exit(1)
	def wrapper():
		try:
			try:
				arg = [_ for _ in sys.argv[1:] if not _.startswith("--")]
				kwarg = (_[2:].split('=') for _ in sys.argv[1:] if _.startswith("--"))
				kwarg = {key: value for key, value in kwarg}
			except Exception, e:
				arg, kwarg = sys.argv[1:], {}
			return func(*arg, **kwarg)
		except TypeError, e:
			if e.message.startswith("%s() takes at least" %(func.func_name)):
				HELP()
			else:
				raise TypeError(e)
	return wrapper
