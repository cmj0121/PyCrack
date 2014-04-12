#! /usr/bin/env python
#! coding: utf-8

from conf import DEFAULT_CONF as _C
import sys

def regMethod(name=""):
	"""	Register function into CURRENT_CMD
	>>> def foo(CURRENT_CMD):
	... 	print " ".join(CURRENT_CMD)
	>>> foo(CURRENT_CMD=['x'])
	x

	>>> @regMethod('text')
	... def foo(CURRENT_CMD):
	... 	print " ".join(CURRENT_CMD)
	>>> foo(CURRENT_CMD=['x'])
	x text

	>>> @regMethod()
	... def foo(CURRENT_CMD):
	... 	print " ".join(CURRENT_CMD)
	>>> foo(CURRENT_CMD=['x'])
	x foo

	>>> class FOO(object):
	... 	@regMethod("foo")
	... 	def __call__(self, CURRENT_CMD):
	...			print " ".join(CURRENT_CMD)
	>>> f = FOO()
	>>> f(CURRENT_CMD=["x"])
	x foo
	"""
	def wrap(fn):
		import types
		def wrap_fn(*arg, **kwarg):
			if "CURRENT_CMD" not in kwarg: return fn(*arg, **kwarg)

			## Append name into CURRENT_CMD
			if name: kwarg["CURRENT_CMD"] += [name]
			else: kwarg["CURRENT_CMD"] += [fn.func_name]
			return fn(*arg, **kwarg)
		return wrap_fn
	return wrap
def regExitCallback(fn):
	""" Register callback function when exit program """
	import atexit
	atexit.register(fn)
	return fn
def clearPyc():
	""" Remove all .pyc file """
	import os

	cmd = "find . | grep .pyc$"
	ret = [_ for _ in os.popen(cmd).read().split('\n') if _]
	for _ in ret:
		os.unlink(_)
class WebBase(object):
	""" Virtual class and handle all general Web OPs """
	def normalizationURL(self, url):
		"""
		normalizate URL as format: scheme://domain

		>>> ws = WebBase()
		>>> url = ws.normalizationURL("www.example.com")
		>>> "http://www.example.com" == url
		True

		>>> url = ws.normalizationURL("https://www.example.com")
		>>> "https://www.example.com" == url
		True
		"""
		if not url.startswith('http'): url = "http://" + url
		return url
	def getPage(self, url, AGENT="WS Scanner", *arg, **kwarg):
		"""
		The wrap for get web page.

		>>> ws = WebBase()
		>>> if ws.getPage("www.example.com"): print "RECV"
		RECV

		>>> if ws.getPage("a.b.c"): print "RECV"
		"""
		import requests
		headers = {'User-Agent': AGENT}
		try:
			return requests.get(self.normalizationURL(url), headers=headers)
		except requests.exceptions.ConnectionError as e:
			return None
	def getDomain(self, url):
		"""
		Get the domain from format URL

		>>> ws = WebBase()
		>>> ("", "") == ws.getDomain("www.example.com")
		True

		>>> ("http", "www.example.com") == ws.getDomain("http://www.example.com")
		True
		"""
		import urlparse
		_ = urlparse.urlparse(url)
		return _.scheme, _.netloc
	def asIP(self, target, *arg, **kwarg):
		"""
		Transfer to IP address if possible

		>>> ws = WebBase()
		>>> "127.0.0.1" == ws.asIP("localhost")
		True
		>>> "127.0.0.1" == ws.asIP("127.0.0.1")
		True
		>>> "" == ws.asIP("999.999.999.99")
		True
		>>> "" == ws.asIP('http://translate.google.com.tw/#auto/zh-TW/trick')
		False
		"""
		import re
		import socket

		if target.startswith('http'):
			ip = socket.gethostbyname(self.getDomain(target)[1])
		elif re.match(r'.*?:\d+', target):
			target, port = ":".join(target.split(":")[:-1]), target.split(":")[-1]
			ip = socket.gethostbyname(target)
		else:
			ip = socket.gethostbyname(target)
		return ip
class Dispatch(object):
	"""	Command dispatch """
	def __init__(self):
		self.callback_fn = {}
	def __call__(self, *arg, **kwarg):
		""" Run dispatch runtine """
		import traceback

		if not arg: return self.helpMsg(*arg, **kwarg)

		for _ in self.callback_fn:
			if _ == arg[0]:
				if kwarg["DEBUG"]:
					kwarg["RAW_DATA"] = self.callback_fn[_]["fn"](*arg[1:], **kwarg)
					return self.showResult(**kwarg)
				else:
					try:
						kwarg["RAW_DATA"] = self.callback_fn[_]["fn"](*arg[1:], **kwarg)
					except Exception as e:
						print "Get Exception: %s" %e
						kwarg["CURRENT_CMD"] = kwarg["CURRENT_CMD"][:-1]
						return self.helpMsg(*arg, **kwarg)
					else:
						return self.showResult(**kwarg)
		else:
			if "" in self.callback_fn:
				kwarg["RAW_DATA"] = self.callback_fn[""]["fn"](*arg, **kwarg)
				return self.showResult(**kwarg)
			else:
				return self.helpMsg(*arg, **kwarg)
	def addArgument(self, name, callback_fn, help=""):
		self.callback_fn.update({name: {
			"fn": callback_fn, "help": help }
		})
		return self
	@regMethod
	def test(self, *arg, **kwarg):
		""" Run doctest """
		import doctest

		_MODULE_ = (conf, jpython)
		print "Run doctest... ",
		doctest.testmod()
		for _ in _MODULE_: doctest.testmod(_)
		print "Success!"
	def helpMsg(self, *arg, **kwarg):
		""" Show help message """

		print "Usage: "
		kwarg["CURRENT_CMD"] = " ".join(kwarg["CURRENT_CMD"])
		MAXLEN = max([len(_) for _ in self.callback_fn])
		MAXLEN = MAXLEN + len(kwarg["CURRENT_CMD"]) + 2

		for _ in sorted(self.callback_fn.keys()):
			cmd = "{CURRENT_CMD} {0} ".format(_, **kwarg)
			FORMAT = "  {0:<{3}} {1:<16} {2}"
			FORMAT = FORMAT.format(cmd, "[TARGET]", self.callback_fn[_]["help"], MAXLEN)
			print FORMAT
		if "EXTRA_PARM" in kwarg:
			for _ in kwarg["EXTRA_PARM"]:
				print "    {PARM} {HELP}".format(**_)
		return 1
	def showResult(self, RAW_DATA, PRETTY, *arg, **kwarg):
		""" Show result """
		if "raw" == PRETTY: print rawData
		return 0

