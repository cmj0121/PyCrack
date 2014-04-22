#! /usr/bin/env python
#! coding: utf-8

"""
Get target network information

Function
	1- geographic
"""

from utils import Target, WebBase, regMethod, Dispatch

class INFO(Dispatch, WebBase):
	"""
	>>> info = INFO()
	>>> ret = info.geo("8.8.8.8")["geo"]
	>>> "8.8.8.8" == ret["ip"]
	True

	>>> "United States" == ret["country_name"]
	True
	>>> (-97, 38) == (ret["longitude"], ret["latitude"])
	True

	>>> ret = info.serType("www.google.com", 8160, 80)["server"]
	>>> print ret["Server"]
	sffe
	"""
	def __init__(self):
		self.callback_fn = {}
		self.addArgument("", self.info,
			help="Default information scan")
		self.addArgument("geo", self.geo,
			help="Get geographic information")
		self.addArgument("cms", self.cms,
			help="Get CMS type")
		self.addArgument("server", self.serType,
			help="Server information")
	@regMethod('info')
	def __call__(self, *arg, **kwarg):
		return super(INFO, self).__call__(*arg, **kwarg)
	def info(self, target, *arg, **kwarg):
		""" Default routine for info method """
		ret = {}
		ret.update(self.geo(target, *arg, **kwarg))
		ret.update(self.serType(target, *arg, **kwarg))
		ret.update(self.cms(target, *arg, **kwarg))
		return ret
	@regMethod()
	def geo(self, target, *arg, **kwarg):
		""" Get the geographic for target """
		import json

		t = Target(target)
		if not t.ip: raise SystemError("Target (%s) not found" %target)
		target = "freegeoip.net/json/{0}".format(t.ip)
		geo = self.getPage(target, *arg, **kwarg)
		if geo and 200 != geo.status_code: return {}
		else: return {"geo": json.loads(geo.text)}
	@regMethod("server")
	def serType(self, target, BUFSIZ, PORT, *arg, **kwarg):
		""" Get server information """
		import socket

		target = Target(target)
		domain = target.netloc
		sk = socket.create_connection((domain, PORT))
		## Get server type by send HEAD method
		req = 	"HEAD / HTTP/1.1\r\n" \
				"HOST: %s\r\n\r\n" %target
		sk.send(req)
		ret = sk.recv(BUFSIZ)
		if kwarg and (kwarg["DEBUG"] or kwarg["VERBOUS"]): print ret

		ret = [_ for _ in ret.split("\r\n") if _]
		ret = {_.split(":")[0]: ":".join(_.split(":")[1:]).strip()
					for _ in ret if ":" in _}
		if "Server" not in ret: ret["Server"] = "Unknown"
		return {"server": ret}
	@regMethod('cms')
	def cms(self, target, ENCODE, CMS_FILTER, CMS_TOKEN, *arg, **kwarg):
		""" Get the web page and parse the contain """
		import re

 		ret = {"cms": []}
		page = self.getPage(target, *arg, **kwarg)
		if not page:
			if kwarg and (kwarg["DEBUG"]):
				print "Taret ({0}) not found".format(target)
			return ret

		page = page.text
		if isinstance(page, unicode): page = page.encode(ENCODE)
		if kwarg and (kwarg["DEBUG"]):
			print "Load web page with len: {0}".format(len(page))

		## Find the meta info for content
		## Example: <meta name="generator" content="Discuz! 7.2" />
		match = [	_.strip()
					for filter in CMS_FILTER
					for _ in re.findall(filter, page, re.UNICODE)
					if _.strip()]

		ret["cms"] = [_ for _ in match for token in CMS_TOKEN
						if re.match(token, _, re.UNICODE)]
		return ret
	def showResult(self, RAW_DATA, PRETTY, *arg, **kwarg):
		if "raw" == PRETTY: print RAW_DATA
		elif not isinstance(RAW_DATA, dict):
			raise SystemError("Not valid type (%s) for RAW_DATA" %type(RAW_DATA))
		elif "pretty" == PRETTY:
			if "geo" in RAW_DATA:
				FORMAT  =  \
					u"{0:<10} {ip}\n" \
					u"{1:<10} {city}/{region_name}/{country_code} "\
					u"(N {latitude}, E {longitude})"
				print FORMAT.format("IP", "Location", **RAW_DATA["geo"])
			if "server" in RAW_DATA:
				FORMAT = \
					u"{0:<10} {Server}"
				print FORMAT.format("Server", **RAW_DATA["server"])
			if "cms" in RAW_DATA and RAW_DATA["cms"]:
				print u"{0:<10} {1}".format("CMS", ", ".join(RAW_DATA["cms"]))
		else: raise NotImplementedError("Not support format: %s" %PRETTY)
		return 0

