#! /usr/bin/env python
#! coding: utf-8

import socket
from modules import sdk

defaultTimeout = 5

def resolveInfo(host):
	try:
		name, alias, ips = socket.gethostbyname_ex(host)
	except socket.gaierror, e:
		ret = {}
	except Exception, e:
		raise Exception(e)
	else:
		ret = {"name": name, "alias": alias, "IP list": ips}
	return ret
def WebInfo(host, port=80):
	def ServerInfo(host, port):
		if not host:
			return -1, "Bad Parameter"
		elif host.startswith("http://"):
			host = host[7:]
		elif host.startswith("https://"):
			host = host[8:]
			port = 445

		try:
			addr = socket.gethostbyname(host)
			sk = socket.create_connection((addr, port), timeout=5)
			sk.send("TRACE ./ HTML/1.1")
			ret = (0, sk.recv(1024))
		except socket.timeout, e:
			ret = (-1, "Timeout")
		except Exception, e:
			print Exception(e)
			ret = (-1, "%s" %Exception(e))
		finally:
			return ret
	ret = {}

	## Get server info
	st,  page = _ServerInfo(host, port)
	if 0 == st:
		for word in ("nginx", "apache"):
			if word in page:
				ret["http server"] = word

	## Get web info
	web = sdk.wrapGetWebPage(host)
	ret.update({"header": web.header})

	return ret
def SSHInfo(host, port=22):
	_timeout = socket.getdefaulttimeout()
	socket.setdefaulttimeout(defaultTimeout)


	sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	ret = None
	try:
		sk.connect((host,port))
	except socket.timeout, e:
		ret = (-1, "Timeout")
	except Exception, e:
		raise Exception(e)
	else:
		ret = (0, sk.recv(4096))
		sk.close()
	socket.setdefaulttimeout(_timeout)
	return ret

	
def test():
	return ServerInfo("www.ck101.com")

if __name__ == "__main__":
	print test()[1]
