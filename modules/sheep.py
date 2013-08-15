#! /usr/bin/env python
#! coding: utf-8

import tempfile
import socket
import random
import commands
import os
import sys
import getpass

def GetSheep(nr=100, **kwarg):
	def _getSheep(nr=100, debug=False):
		domain = []
		for _ in xrange(nr):
			ip = ".".join([str(random.randint(0,255)) for n in range(4)])
			if debug: print "Try: %s" %ip

			try:
				ret = socket.gethostbyaddr(ip)
			except socket.herror, e:
				pass
			else:
				domain += [[ip, ret[0]]]
		return domain

	while True:
		domain = _getSheep(nr, debug = True if "debug" in kwarg and kwarg["debug"] else False)
		domain = ["{0}&&{1}&&".format(n[0], n[1]) for n in domain]

		if "db_usr" in kwarg and "db_pwd" in kwarg:
			with tempfile.NamedTemporaryFile() as f:
				for line in domain:
					f.file.write("%s\n" %line)
				f.file.flush()

				shell = r"LOAD DATA LOCAL INFILE '%s' "\
						r"REPLACE into TABLE sheep " \
						r"fields terminated by '&&' lines terminated by '\n'"
				shell = shell %(f.name)
				cmd = 'mysql -h ds -u %s -D cmj --password=%s -e "%s"'
				cmd = cmd %(kwarg['db_usr'], kwarg['db_pwd'], shell)
				st, ret = commands.getstatusoutput(cmd)
				if st and "debug" in kwarg and kwarg['debug']:
					print "[%d] %s" %(st, ret)
				else:
					print "Update %d sheeps: %s" %(len(domain), ret)
def RobustGetSheep(**kwarg):
	"""
	"""
	while True:
		try:
			GetSheep(**kwarg)
		except KeyboardInterrupt:
			pass

