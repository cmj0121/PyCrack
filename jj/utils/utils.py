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

class Target(object):
	""" Pseudo object for target
		>>> t = Target("cmj.tw")
		>>> t.ip == "106.186.121.24"
		True
		>>> t.scheme == "http"
		True
		>>> t.url == "http://cmj.tw"
		True

		>>> t = Target()
		>>> url = t.normalizationURL("www.example.com")
		>>> "http://www.example.com" == url
		True
		>>> url = t.normalizationURL("https://www.example.com")
		>>> "https://www.example.com" == url
		True

		>>> ("", "") == t.getDomain("www.example.com")
		True
		>>> ("http", "www.example.com") == t.getDomain("http://www.example.com")
		True

		>>> "127.0.0.1" == t.asIP("localhost")
		True
		>>> "127.0.0.1" == t.asIP("127.0.0.1")
		True
		>>> "" == t.asIP("999.999.999.99")
		True
		>>> "" == t.asIP('http://translate.google.com.tw/#auto/zh-TW/trick')
		True
	"""
	def __init__(self, target=None, **kwarg):
		if isinstance(target, Target):
			return target
		elif target:
			self.url = self.normalizationURL(target)
			self.scheme, self.netloc = self.getDomain(self.url)
			self.ip  = self.asIP(self.netloc)
		else:
			self.url = self.scheme = self.netloc = self.ip = None
	def normalizationURL(self, url):
		""" normalizate URL as format: scheme://domain """
		if not url.startswith('http'): url = "http://" + url
		return url
	def getDomain(self, url):
		""" Get the domain from format URL """
		import urlparse
		_ = urlparse.urlparse(url)
		return _.scheme, _.netloc
	def asIP(self, target, *arg, **kwarg):
		""" Transfer to IP address if possible from domain name """
		import re
		import socket

		try:
			if re.match(r'.*?:\d+', target):
				target, port = ":".join(target.split(":")[:-1]), target.split(":")[-1]
				ip = socket.gethostbyname(target)
			else:
				ip = socket.gethostbyname(target)
			return ip
		except socket.gaierror as e:
			if kwarg and "DEBUG" in kwarg and kwarg["DEBUG"]:
				print "Target (%s) %s" %(target, e)
			return "" 
class WebBase(object):
	"""
	Web-Based utils 
		>>> ws = WebBase()
		>>> if ws.getPage("www.example.com"): print "RECV"
		RECV

		>>> if ws.getPage("a.b.c"): print "RECV"
	"""
	def getPage(self, target, AGENT="WS Scanner", *arg, **kwarg):
		"""
		The wrap for get web page and support cache mechanism.

		"""
		import requests
		headers, url = {'User-Agent': AGENT}, Target(target).url
		if not url: return None
		try:
			if not hasattr(self, "_pages_"): self._pages_ = {}
			if url in self._pages_: return self._pages_[url]
			self._pages_[url] = requests.get(url, headers=headers)
			return self._pages_[url]
		except requests.exceptions.ConnectionError as e:
			if kwarg and "DEBUG" in kwarg and kwarg["DEBUG"]:
				print "Target (%s) %s" %(target, e)
			return None
class Dispatch(object):
	"""	Command dispatch """
	def __init__(self):
		self.callback_fn = {}
	def __call__(self, *arg, **kwarg):
		""" Run dispatch runtine """
		import traceback

		arg, kwarg = self.optParse(arg, kwarg)
		print kwarg["FORCE"]
		if 0 == len(arg):
			if "*" in self.callback_fn:
				kwarg["RAW_DATA"] = self.callback_fn["*"]["fn"](*arg, **kwarg)
				return self.showResult(**kwarg)
			else:
				return self.helpMsg(*arg, **kwarg)
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
						sys.exit(1)
					else:
						return self.showResult(**kwarg)
		else:
			if "*" in self.callback_fn:
				kwarg["RAW_DATA"] = self.callback_fn["*"]["fn"](*arg, **kwarg)
				return self.showResult(**kwarg)
			else:
				return self.helpMsg(*arg, **kwarg)
	def addArgument(self, name, callback_fn, help=""):
		self.callback_fn.update({name: {
			"fn": callback_fn, "help": help }
		})
		return self
	@regMethod('doctest')
	def test(self, *arg, **kwarg):
		""" Run doctest """
		import doctest
		import jj
		import types

		_MODULE_ = (getattr(jj, _) for _ in dir(jj))
		_MODULE_ = (_ for _ in _MODULE_ if isinstance(_, types.ModuleType))
		print "Run doctest... "
		print ("  Test %s " %("self" + "."*30)),
		doctest.testmod()
		print " Done"

		for _ in _MODULE_:
			print ("  Test %s " %(_.__name__ + "."*(34-len(_.__name__)))),
			doctest.testmod(_)
			print " Done"
		print "Success!"
	def helpMsg(self, *arg, **kwarg):
		""" Show help message """

		print "Usage: "
		kwarg["CURRENT_CMD"] = " ".join(kwarg["CURRENT_CMD"])
		MAXLEN = max([len(_) for _ in self.callback_fn])
		MAXLEN = MAXLEN + len(kwarg["CURRENT_CMD"]) + 2

		for _ in sorted(self.callback_fn.keys()):
			cmd = "{CURRENT_CMD} {0} ".format(_ if "*" != _ else "", **kwarg)
			FORMAT = "  {0:<{3}} {1:<16} {2}"
			FORMAT = FORMAT.format(cmd, "[TARGET]", self.callback_fn[_]["help"], MAXLEN)
			print FORMAT
		if "EXTRA_PARM" in kwarg:
			for _ in kwarg["EXTRA_PARM"]:
				print "    {PARM} {HELP}".format(**_)
		sys.exit(1)
	def showResult(self, RAW_DATA, PRETTY, *arg, **kwarg):
		""" Show result """
		print RAW_DATA
		return 0
	def optParse(self, arg, kwarg):
		""" Optional Parser """
		ret = []
		while arg:
			_, arg = arg[0], arg[1:]
			if _ in ("-q", "--quite"):
				kwarg["QUITE"] = True
			elif _ == "--force":
				kwarg["FORCE"] = True
			elif _ in ("-D", "--debug"):
				kwarg["DEBUG"] = True
			elif _ in ("-v", "-vv", "-vvv"):
				if kwarg["VERBOUS"]:
					raise SystemError("Multiple verbose options")
				kwarg["VERBOUS"] = _.count("v")
			elif _ == "-d":
				if not arg: raise SystemError("Missing value for -d")
				arg, kwarg["DEPTH"] = arg[1:], arg[0]
			elif _.startswith("--depth="):
				kwarg["DEPTH"] = _[len("--depth"):]
			else:
				ret += [_]
		return ret, kwarg

