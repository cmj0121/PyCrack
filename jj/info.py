#! /usr/bin/env python
#! coding: utf-8

"""
Get target network information

Function
	1- geographic
"""

from utils import WebBase, regMethod, Dispatch

class INFO(Dispatch, WebBase):
	def __init__(self):
		self.callback_fn = {}
		self.addArgument("", self.info,
			help="Default information scan")
		self.addArgument("geo", self.geo,
			help="Get geographic information")
	@regMethod('info')
	def __call__(self, *arg, **kwarg):
		return super(INFO, self).__call__(*arg, **kwarg)
	def info(self, target, *arg, **kwarg):
		""" Default routine for info method """
		ret = {}
		ret.update(self.geo(target, *arg, **kwarg))
		return ret
	@regMethod()
	def geo(self, target, *arg, **kwarg):
		"""
		>>> geo = INFO()
		>>> ret = geo.geo("8.8.8.8")
		>>> "8.8.8.8" == ret["ip"]
		True

		>>> "United States" == ret["country_name"]
		True
		>>> (-97, 38) == (ret["longitude"], ret["latitude"])
		True
		"""
		import json

		target = "freegeoip.net/json/{0}".format(self.asIP(target, *arg, **kwarg))
		geo = self.getPage(target, *arg, **kwarg)
		if geo and 200 != geo.status_code: return {}
		else: return {"geo": json.loads(geo.text)}
	def showResult(self, RAW_DATA, PRETTY, *arg, **kwarg):
		if "raw" == PRETTY: print rawData
		elif "pretty" == PRETTY:
			FORMAT  =  \
				u"{0:<10} {ip}\n" \
				u"{1:<10} {city}/{region_name}/{country_code} (N {latitude}, E {longitude})"
			print FORMAT.format("IP", "Location", **RAW_DATA["geo"])
		else: raise NotImplementedError("Not support format: %s" %PRETTY)
		return 0

