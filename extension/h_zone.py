#! /usr/bin/env python
#! coding: utf-8

import re
import requests

class H_ZONE(object):
	BASE_URL = "http://www.zone-h.org"
	def _sites_(self, page):
		def dumpURL(url):
			return re.match(r'(\S+\.)+\S+(/\S+)*', url)
		token = r'<td>\s*(\S+)\s*</td>'
		return [_ for _ in re.findall(token, page) if dumpURL(_)]
	def archive(self, page=1, special=False):
		url = "%s/archive" %self.BASE_URL
		if special:
			url = "%s/special=1" %url
		url = "%s/page=%s" %(url, page)
		req = requests.get(url)
		if 200 == req.status_code:
	 		return self._sites_(req.text)
		else:
			return []

if __name__ == "__main__":
	import sys

	if 1 < len(sys.argv):
		nr = int(sys.argv[1])
	else:
		nr = 10
	h_zone = H_ZONE()
	for _ in range(nr):
		ret = "\n".join(h_zone.archive(_))
		if ret: print ret
