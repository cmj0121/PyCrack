from . import task

class COMMON(object):
	task = task.Task()
	def __del__(self):
		self.task.DEL()
	def _self_(self):
		import os
		import requests, re
		import socket

		print "I'm: %s@[%s]" %(os.getlogin(), os.getcwd())
		print "Internal IP: %s" %socket.gethostbyname(socket.gethostname())

		r = requests.get('http://checkip.dyndns.org')
		print "External IP: %s" %re.search(r'\d+\.\d+\.\d+\.\d+', r.text).group()
	def _targetInfo_(self, *host):
		import socket

		for h in host:
			if host.startswith("http://"): host = host[7:]
			try:
				ip = socket.gethostbyname(host)
				domain, alias, ip = socket.gethostbyaddr(ip)
				print "IP: %s" %",".join(ip)
				print "Domain: %s" %domain
				if alias: print "Alias: %s" %",".join(alias)
				print ""
			except Exception, e:
				pass
	def _clear_(self):
		import os
		print "\033[0m"
		os.system('clear')
	def _selftest_(self):
		import doctest
		doctest.testmod()

	info = property(_self_, _targetInfo_, None)
	clear = property(_clear_, None, None)
	selftest = property(_selftest_, None, None)
