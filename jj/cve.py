#! /usr/bin/env python
#! coding: utf-8

import os
import time
from utils import *

class CVE(Dispatch, WebBase):
	""" CVE Enumerate Class

	>>> cve = CVE()
	>>> ret = cve.LoadCVE(2014, fmt="yaml")
	>>> if ret: print "Load CVE Success"
	Load CVE Success
	>>> ret = cve.LoadCVE(2013, fmt="json")
	>>> if ret: print "Load CVE Success"
	Load CVE Success

	>>> ret = cve.lastCVE(False)
	>>> if ret: print "Load CVE Success"
	Load CVE Success

	>>> cve.lastCVE(False) == cve[-1]
	True

	>>> cve.upgraceCVE()
	[]
	"""

	CVE_PATH = "{home}/.cve/CVE-{year}.{fmt}"
	LAST_CVE_PATH = "{home}/.cve/LastCVE"

	def __init__(self):
		self.callback_fn = {}
		self.addArgument("last", self.lastCVE,
			"Get the last CVE")
		self.addArgument("upgrade", self.upgraceCVE,
			"Get the upgrade CVE List")
		self.addArgument("*", self.search,
			"Search CVE by keyword")
	@regMethod('cve')
	def __call__(self, *arg, **kwarg):
		return super(CVE, self).__call__(*arg, **kwarg)
	def __getitem__(self, index):
		if isinstance(index, int):
			if index == -1:
				year = time.gmtime().tm_year
				cve = self.LoadCVE(year)
				return cve[-1]
			else:
				return self.LoadCVE(index)
		elif isinstance(index, str):
			year, nr = index.split('-')
			cve = self.LoadCVE(year)
			return cve[nr]
		else:
			raise KeyError(index)

	@regMethod('search')
	def search(self, *arg, **kwarg):
		if 2 <= kwarg["VERBOUS"]: print "Search %s" %str(arg)
		if 0 == len(arg): return self.lastCVE(*arg, **kwarg)
		else:
			raise NotImplementedError("Not Implement")
	@regMethod('upgrade')
	def upgraceCVE(self, home=os.path.expanduser('~'), *arg, **kwarg):
		""" Get the newest CVE from last update """
		path = self.LAST_CVE_PATH.format(home=home)
		with open(path) as f:
			last_cve = f.read()
			_, year, last_nr = last_cve.split('-')
		cve = self.lastCVE(FORCE=True)
		_, year, nr = cve.keys()[0].split('-')
		if nr>last_nr:
			return ["CVE-{year}-{nr}".format(year=year, nr=_)
					for _ in range(last_nr, nr+1)]
		else:
			return []
	def lastCVE(self, FORCE, home=os.path.expanduser('~'), *arg, **kwarg):
		""" Get the last CVE record """
		cve = self.LoadCVE(force=FORCE)[-1]
		path = self.LAST_CVE_PATH.format(home=home)
		with open(path, 'w') as f:
			f.write(cve.keys()[0])
		return cve
	def LoadCVE(self, year=None, fmt="yaml", force=False, *arg, **kwarg):
		""" Load CVE List for particular Year """

		if not year: year = time.gmtime().tm_year
		path = self._CVEPath_(year, fmt=fmt)
		if force or not os.path.exists(path): self.UpdateCVE(year, fmt=fmt)

		## Load and return dist format CVE List
		with open(path) as f: cve = f.read()
		if "yaml" == fmt:
			import yaml
			cve = yaml.load(cve.replace('\t', ''))
		elif "json" == fmt:
			import json
			cve = json.loads(cve)
		else:
			raise TypeError("Cannot Load CVE with fmt: %s" %fmt)

		## Parse and filter out the CVE List
		cve = [_ for _ in cve if "REJECT" not in _[_.keys()[0]]['Notes']["Description"]]
		cve = [_ for _ in cve if "RESERVED" not in _[_.keys()[0]]['Notes']["Description"]]
		cve = sorted(cve, key=lambda x: (x.keys()[0], x[x.keys()[0]]["Notes"]["Published"])) 
		return cve
	def UpdateCVE(self, year, fmt):
		""" Update CVE from cve.mitre.org """
		import requests
		from tempfile import NamedTemporaryFile
		from xml.etree import ElementTree

		url = "http://cve.mitre.org/data/downloads/allitems-cvrf-year-{year}.xml"
		url = url.format(year=year)
		req = requests.get(url)
		with NamedTemporaryFile(mode="w") as f:
			f.write(req.text)
			f.flush()
			xml = ElementTree.parse(f.name)
		root = xml.getroot()
		vul  = [_ for _ in root if _.tag.endswith('Vulnerability')]
		cve  = [self._ParseVul_(_) for _ in vul]


		path = self._CVEPath_(year, fmt=fmt)
		dir  = os.path.dirname(path)
		if not os.path.isdir(dir):
			if os.path.exists(dir): os.unlink(dir)
			os.mkdir(dir)
		with open(path, "w") as f:
			if "yaml" == fmt:
				import yaml
				f.write(yaml.dump(cve))
			elif "json" == fmt: 
				import json
				json.dump(cve, f)
	def _CVEPath_(self, year, home=os.path.expanduser('~'), fmt="yaml"):
		""" Return the CVE Path from Local """
		return self.CVE_PATH.format(year=year, home=home, fmt=fmt)
	def _ParseVul_(self, vul):
		""" Parse Vulnerability XML fromat as Dict """
		notes, ref = {}, {}
		for _ in vul.getchildren():
			if _.tag.endswith('Title'):
				cve = _.text
			elif _.tag.endswith('Notes'):
				for n in _:
					if "Description" == n.get('Type'):
						notes[n.get('Type')] = n.text.replace('\n', ' ')
					else:
						notes[n.get('Title')] = n.text
			elif _.tag.endswith("References"):
				for n in _:
					if n.get('Description'):
						ref[n.get('Description').text] = n.get('URL').text
		return {cve: {"Notes": notes, "References": ref}}
def main():
	import doctest
	doctest.testmod()
if __name__ == "__main__": main()

