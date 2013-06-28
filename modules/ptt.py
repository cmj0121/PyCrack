#! coding: utf-8
#! coding: big-5
__VERSION__ = 1.0

import commands
import select
import socket
import pyte
import yaml
from modules import sdk
import time
socket.setdefaulttimeout(10)

class MatchStr(object):
	def __init__(self, key, line=None):
		self.key, self.line = key, line

class PTTAllPostUser(sdk.PTT):
	def __init__(self, user, pwd, db_user, db_pwd, host=("ptt.cc", 23), nr=100, record="log", start=None):
		super(PTTAllPostUser, self).__init__(user, pwd, host)
		self.gotoAllPost()
		if start:
			self._send_("%s\r\n" %start)
		else:
			self._send_(self.END)

		while True:

			ret = []
			if True:
				cnt = 0			
				for _ in xrange(nr):
					try:
						ret += [self.GetUser(NR=str(_+1))]
					except Exception, e:
						print Exception(e)
						cnt += 1
						pass

					self._send_(self.UP)
					time.sleep(0.01)
					if cnt > 20: return

			if True: ## Store into file
				with open(record, "w") as f:
					for line in ret:
						name, alias = line[0].split('(')[0], line[0].split('(')[1]
						name, alias = name.strip(), alias.strip()[:-1]
						now = [n for n in line[1].split(' ') if n][0].split('/')
						now = "-".join([now[-1]] + now[:-1])

						tmp = "%s&&%s&&%s&&%s&&%s&&%s"
						tmp = tmp %(name, alias, now, line[2], ",".join(line[3]), ",".join(line[4]))
						f.write("%s\n" %tmp.encode('utf-8'))

			if True: ## Store into DB
				shell = r"LOAD DATA LOCAL INFILE '%s' REPLACE into TABLE PTT character set utf8 " \
						r"fields terminated by '&&' lines terminated by '\n'"
				shell = shell %(record)
				st, ret = commands.getstatusoutput('mysql -h ds -u %s -D cmj --password=%s -e "%s"' %(db_user, db_pwd, shell))
				if st:
					print "[%d] %s" %(st, ret)
					break
	def getCurrentLine(self, token="●"):
		token = [token.decode('utf-8')]
		token += [u'\ufffd\ufffd']
		for line in self.screen.display:
			if token[0] in line or token[1] in line:
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
		self.reset()
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
		return name, date.split(' ')[0], last, mails, links
		#self.test()
	def test(self):
		self._recvUntil_("測試, 不可能停".decode('utf-8'))
	def show(self, debug=False):
		""" Show the screen """
		if debug:
			print "====\n%s\n====" %"\n".join(self.screen.display)

