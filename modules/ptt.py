#! coding: utf-8
#! coding: big-5
__VERSION__ = 1.0
import select
import socket
import pyte
import yaml
from modules import sdk

socket.setdefaulttimeout(10)

class MatchStr(object):
	def __init__(self, key, line=None):
		self.key, self.line = key, line

class PTTAllPostUser(sdk.PTT):
	def __init__(self, user, pwd, host=("ptt.cc", 23), nr=100, record="log", start=None):
		super(PTTAllPostUser, self).__init__(user, pwd, host)
		self.gotoAllPost()
		if start:
			self._send_("%s\r\n" %start)
		else:
			self._send_(self.HOME)
			
		while True:
			ret = []
			for _ in xrange(nr):
				try:
					ret += [self.GetUser(NR=str(_+1))]
				except Exception, e:
					print Exception(e)
					pass

				self._send_(self.DOWN)
			with open(record, "a") as f:
				for line in ret:
					name, alias = line[0].split('(')[0], line[0].split('(')[1]
					name, alias = name.strip(), alias.strip()[:-1]
					tmp = "%s | %s | %s | %s | %s | %s"
					tmp = tmp %(name, alias, line[1], line[2], ",".join(line[3]), ",".join(line[4]))
					f.write("%s\n" %tmp.encode('utf-8'))
		
	def getCurrentLine(self, token="●"):
		token = token.decode('utf-8')
		for line in self.screen.display:
			if token in line:
				return line
		else:
			self._send_(' ')
			raise KeyError("Cannot find the current line by key: %s" %token)
	def gotoAllPost(self):
		self._send_("F\r\n\r\n")
		self._recvUntil_(MatchStr("看板《ALLPOST》".decode('utf-8'), 0))
		self._recvUntil_(MatchStr("(b)進板畫面".decode('utf-8'), 0))
	def reset(self):
		self.screen.reset()
	def GetUser(self, NR=None):
		def getToken(line, token):
			import re
			req = re.search(token, line)
			if req:
				return req.group(0)
			else:
				return None
		line = self.getCurrentLine()
		nr, date, name = line[1:7], line[10:15], line[16:29]
		self._send_(self.CTRL_Q)

		## Get precise info
		pos = self._recvUntil_(	MatchStr("請按任意鍵繼續".decode('utf-8'), -1), 
								MatchStr("▄▄▄▄▄▄".decode('utf-8'), -1),
								MatchStr("▄▄▄▄▄▄".decode('utf-8')))

		pos = self.screen.display[1].find("《經濟狀況》".decode('utf-8'))
		if pos == -1:
			self.show(debug=True)
			self.reset()
			self._send_(' ')
			self._recvUntil_(MatchStr("(y)回應".decode('utf-8'), -1), MatchStr("(X)推文".decode('utf-8'), -1))
			raise SystemError("Out of my except")
		name = self.screen.display[1][6:pos].strip() 

		pos = self.screen.display[4].find("《上次故鄉》".decode('utf-8'))
		date, last = self.screen.display[4][6:pos].strip(), self.screen.display[4][pos+6:].strip()

		# Get extra info
		links = [getToken(line, r" http://(.*?) ") for line in self.screen.display[6:]]
		mails = [getToken(line, r"([^@\s]+)@((?:[-a-z0-9]+\.)+[a-z]{2,})") for line in self.screen.display[6:]]
		links = [n for n in links if n]
		mails = [n for n in mails if n]
	
		print "%s - %s [%s] [%s]" %(nr, name, date, last)
		if mails:
			print "    [%s]" %",".join(mails)
		if links:
			print "    [%s]" %",".join(links)
		
		## FIXME
		self.screen.reset()

		self._send_(' ')
		self._recvUntil_(MatchStr("(y)回應".decode('utf-8'), -1), MatchStr("(X)推文".decode('utf-8'), -1))
		return name, date, last, mails, links
		#self.test()
	def test(self):
		self._recvUntil_("測試, 不可能停".decode('utf-8'))
	def show(self, debug=True):
		""" Show the screen """
		if debug:
			print "====\n%s\n====" %"\n".join(self.screen.display)

