#! /usr/bin/env python
#! coding: utf-8

import json
import urllib2

class SYNOOAuth(object):
	def __init__(self, conf=None):
		if not conf:
			raise SystemError("You need input the configure file")

		if isinstance(conf, str):
			with open(conf) as f:
				self.conf = self._dumpConf_(f.read())
		elif isinstance(conf, dict):
			self.conf = conf
		else:
			raise SystemError("Unknow Type: %s" %conf)
			
	def _dumpConf_(self, data):
		return json.dumps(data)
	def _loadConf_(self, data):
		return json.loads(data)
	def _grantPermission_(self):
		url = self.conf['grantPermURL']
		parm = ["%s={%s}"%(_, _) if "=" not in _ else _ for _ in self.conf['grantPermParam']]
		ret = "%s?%s" %(url, "&".join(parm))
		return ret.format(**self.conf)
	def grantPerm(self):
		url = self._grantPermission_()
		print url

	def _getAccessToken_(self, code):
		self.conf.update({'code':code})
		url = self.conf['accessTokenURL']
		parm = ["%s={%s}"%(_, _) if "=" not in _ else _ for _ in self.conf['accessTokenParam']]
		ret = "%s?%s" %(url, "&".join(parm))
		return ret.format(**self.conf)
	def getAccessToken(self, code):
		url = self._getAccessToken_(code)
		ret = urllib2.urlopen(url).read()

		return dict([_.split('=') for _ in ret.split('&')])
if __name__ == "__main__":
	import sys
	import os

	google = {
		'grantPermURL': 'https://accounts.google.com/o/oauth2/auth',
		'grantPermParam': ['client_id', 'response_type=code', 'redirect_uri', 'state', 'scope=openid%20email'],
		'accessTokenURL': 'accounts.google.com',
		'accessTokenParam': ['client_id', 'client_secret', 'redirect_uri', 'code', 'grant_type=authorization_code'],
		'redirect_uri': 'http://cmj0121.synology.me:5000/webman/oauth.cgi',
		'client_id': '118122536625-kcepl246vn4af5999dd31gr1brufq2j2.apps.googleusercontent.com',
		'client_secret': 'MTGbpFlcafMde8v0Kndrr_5D',
		'state': 'SYNOOAUTH'}
	facebook = {
		'grantPermURL': 'https://www.facebook.com/dialog/oauth',
		'grantPermParam': ['client_id', 'redirect_uri', 'state'],
		'accessTokenURL': 'https://graph.facebook.com/oauth/access_token',
		'accessTokenParam': ['client_id', 'client_secret', 'redirect_uri', 'code'],
		'redirect_uri': 'http://cmj0121.synology.me:5000/webman/oauth.cgi',
		'client_id': '165438063645301',
		'client_secret': 'd979822b849a337f221477d91b48f2d1',
		'state': 'SYNOOAUTH'}


	TEST = google

	print "Content-type: text/html"
	print ""

	try:
		if 'QUERY_STRING' in os.environ:
			query = dict([_.split('=') for _ in os.environ['QUERY_STRING'].split('&')])
			code  = query['code']
			state = query['state']

			oauth = SYNOOAuth(TEST)
			print oauth.getAccessToken(code=code)
		else:
			oauth = SYNOOAuth(TEST)
			oauth.grantPerm()
	except Exception as e:
		print e
