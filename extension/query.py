#! /usr/bin/env python
#! coding: utf-8
#! coding: big-5
__VERSION__ = 1.0

import pyte
import socket
import time
from sdk.CLI import CLI

class MatchStr(object):
	def __init__(self, key, line=None):
		self.key, self.line = key, line
_M = MatchStr

class TELNET(object):
	UP		= '\x1bOA'
	DOWN	= '\x1bOB'
	LEFT	= '\x1bOD'
	RIGHT	= '\x1bOC'
	HOME	= '\x1b[1~'
	END		= '\x1b[4~'
	CTRL_Q	= "\x11"
	CTRL_W	= "\x17"
	CTRL_U	= '\x15'
	DEBUG	= 0
	TIMEOUT	= 15
	def __init__(self, user, pwd, host, killReplica):
		self._timeout = socket.getdefaulttimeout()
		socket.setdefaulttimeout(float(self.TIMEOUT))

		self.screen = pyte.Screen(80, 24)
		self.stream = pyte.Stream()

		self.stream.attach(self.screen)
	def __del__(self):
		self.DEL()
	def DEL(self):
		socket.setdefaulttimeout(self._timeout)
		self.sk.close()
	def _recv_(self):
		ret = self.sk.recv(1024).decode('big5', 'replace')
		self.stream.feed(ret)
		if hasattr(self, "show") and callable(self.show):
			self.show()
	def _recvUntil_(self, *conditions):
		""" recv socket message until recv useful message """
		if not conditions or not isinstance(conditions, tuple):
			raise TypeError("conditions only accept MatchStr")

		if 1 == len(conditions) and (isinstance(conditions[0], str) or isinstance(conditions[0], unicode)):
			conditions = (MatchStr(conditions[0]),)

		while True:
			for cond in conditions:
				comp = self.screen.display[cond.line] if cond.line else "\n".join(self.screen.display)
				if cond.key in comp:
					return conditions.index(cond)
			self._recv_()
	def _send_(self, msg):
		""" Send a command to target """
		if not isinstance(msg, str) and not isinstance(msg, unicode): msg = str(msg)
		self.sk.send(str(msg))
	def _sendUntilRecv_(self, msg, *conditions):
		""" send message until recv useful message """
		pos = self._recvUntil_(*conditions)
		self._send_(msg)
	def _repeatSendUntilRecv_(self, msg, *conditions):
		""" recv socket message until recv useful message """
		if not conditions or not isinstance(conditions, tuple):
			raise TypeError("conditions only accept MatchStr")

		if 1 == len(conditions) and (isinstance(conditions[0], str) or isinstance(conditions[0], unicode)):
			conditions = (MatchStr(conditions[0]),)

		while True:
			self._send_(msg)
			if hasattr(self, "show") and callable(self.show):
				self.show()

			for cond in conditions:
				comp = self.screen.display[cond.line] if cond.line else "\n".join(self.screen.display)
				if cond.key in comp:
					return conditions.index(cond)

			ret = self.sk.recv(1024).decode('big5', 'replace')
			self.stream.feed(ret)
class PTT(TELNET):
	def __init__(self, user, pwd, host, killReplica):
		super(PTT, self).__init__(user, pwd, host, killReplica)
		self.login(user, pwd, host, killReplica)
	def login(self, user, pwd, host, killReplica):
		""" Login policy

			We only process the log-in routine and kill the replica log-in if need
		"""
		sk = socket.create_connection(host)
		self.sk = sk

		## Connect and log-in
		self._sendUntilRecv_("%s\r\n" %user, MatchStr("請輸入代號".decode('utf-8'),-4))
		self._sendUntilRecv_("%s\r\n" %pwd, MatchStr(user, -4))
		repli = MatchStr("您想刪除其他重複登入的連線嗎".decode('utf-8'), -2)
		conti = MatchStr("請按任意鍵繼續".decode('utf-8'), -1)
		if 0 == self._recvUntil_(repli, conti):
			if killReplica: self._send_("Y\r\n")
			else: self._send_("N\r\n")

			self._recvUntil_(MatchStr("請按任意鍵繼續".decode('utf-8')))
		self._repeatSendUntilRecv_(" ", MatchStr("(G)oodbye".decode('utf-8')))
	def dumpUser(self):
		def getToken(line, token):
			import re
			req = re.search(token, line)
			if req:
				return req.group(0)
			else:
				return None

		token = "《經濟狀況》"
		try:
			self._recvUntil_(_M(token.decode('utf-8')), _M("我是".decode('utf-8')))
		except socket.timeout, e:
			raise SystemError("Out of except.")

		pos = self.screen.display[1].find(token.decode('utf-8'))
		if -1 == pos:
			if -1 != "".join(self.screen.display).find("我是".decode('utf-8')):
				raise SystemError("No such user.")
			raise SystemError("Out of except.")

		name = self.screen.display[1][6:pos].strip()
		_ = re.match(r"(.*?)\((.*?)\)", self.screen.display[1][6:pos].strip())
		if _:
			name, alias = _.group(1), _.group(2)
		else:
			raise SystemError("Cannot find out the name/alias")

		pos = self.screen.display[4].find("《上次故鄉》".decode('utf-8'))
		date, ip = self.screen.display[4][6:pos].strip(), self.screen.display[4][pos+6:].strip()

		# Get extra info
		links = [getToken(line, r" http://(.*?) ") for line in self.screen.display[6:]]
		mails = [getToken(line, r"([^@\s]+)@((?:[-a-z0-9]+\.)+[a-z]{2,})") for line in self.screen.display[6:]]
		links = [n for n in links if n]
		mails = [n for n in mails if n]

		return name, alias, date.split(' ')[0], ip, mails, links

	def gotoMainPage(self):
		self._send_(self.LEFT*5)
		self._repeatSendUntilRecv_('q', _M("我是".decode('utf-8'), -1), _M('線上'.decode('utf-8'), -1))
	def gotoQueryPage(self, nr=10):
		def _queryPage_(self):
			self._send_("t\r\nq\r\n")
			self._recvUntil_(_M("請輸入使用者代號".decode('utf-8')))

		self.gotoMainPage()
		for _ in range(nr):
			try:
				_queryPage_(self)
			except KeyboardInterrupt, e:
				raise KeyboardInterrupt(e)
			except Exception, e:
				self.gotoMainPage()
			else:
				break
		else:
			raise SystemError("Try %s times still failed" %nr)

	def show(self):
		""" Show the screen """
		if self.DEBUG:
			print "====\n%s\n====" %"\n".join(self.screen.display)
	def reset(self, key=None):
		""" Send keys if set and reset the screen"""
		if key:
			self._send_(key)
		self.screen. reset()
class QueryUser(PTT):
	def __init__(self, user, pwd, host, multi=False):
		super(QueryUser, self).__init__(user, pwd, host, killReplica=multi)
		self.gotoMainPage()
	def query(self, user=None):
		self.gotoQueryPage()
		if not user:
			user = raw_input('query ')
		self._send_("%s\r\n" %user)
		self._recv_()
		ret = self.dumpUser()
		self.reset(' ')
		return ret

def _query_(usr, pwd, host, *username):
	if not username:
		help_msg()

	if host in ('ptt', 'ptt2'):
		host = ('140.112.172.11', 23) if 'ptt' == host else ('140.112.172.12', 23)
	p = QueryUser(usr, pwd, host)
	ret = []
	for _ in username:
		try:
			ret +=[p.query(_)]
		except SystemError, e:
			ret += ["%s: %s" %(_, e)]
		finally:
			print ret[-1]
	return ret
@CLI
def query(host, *username):
	import getpass
	usr = raw_input("Usr: ")
	pwd = getpass.getpass("Pwd: ")
	return _query_(usr, pwd, host, *username)
def help_msg():
	import sys
	print "%s [host] [[username] ...]" %sys.argv[0]
	exit(1)
if __name__ == "__main__":
	query()
