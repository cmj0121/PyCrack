from modules import info
from modules import todo
from modules import task

class COMMON(object):
	def __init__(self):
		self.task = task.Task()
		self.todo = todo.TODO_LIST()

	def __del__(self):
		del self.task
		self.todo._save_(self.todo._job_)

	def _self_(self):
		import os
		import requests, re
		import socket

		print "I'm: %s@[%s]" %(os.getlogin(), os.getcwd())
		print "Internal IP: %s" %socket.gethostbyname(socket.gethostname())

		r = requests.get('http://checkip.dyndns.org')
		print "External IP: %s" %re.search(r'\d+\.\d+\.\d+\.\d+', r.text).group()
	def _targetInfo_(self, *host):
		for _host in host:
			try:
				ret = info.IPInfo(_host)
				if ret:
					print "IP  %s" %ret["ip"]
					print "Domain  %s" %ret["domain"]
					if ret["alias"]: 
						print "Alias  %s" %",".join(ret["alias"])
			except Exception, e:
				pass

			try:
				ret = info.WebInfo(_host)
				print ret
			except Exception, e:
				pass

			try:
				ret = info.SSHInfo(_host)
				print ret
			except Exception, e:
				pass
	info = property(_self_, _targetInfo_, None)

	def _clear_(self):
		import os
		print "\033[0m"
		os.system('clear')
	clear = property(_clear_, None, None)

	def _selftest_(self):
		import doctest
		doctest.testmod()
	selftest = property(_selftest_, None, None)

