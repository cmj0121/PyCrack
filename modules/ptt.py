#! coding: utf-8
#! coding: big-5
__VERSION__ = 1.0

import commands
import pyte
import socket
import time
import tempfile

class MatchStr(object):
	def __init__(self, key, line=None):
		self.key, self.line = key, line
class PTT(object):
	UP		= '\x1bOA'
	DOWN	= '\x1bOB'
	LEFT	= '\x1bOC'
	RIGHT	= '\x1bOD'
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
		self.login(user, pwd, host, killReplica)
	def __del__(self):
		socket.setdefaulttimeout(self._timeout)
		self.sk.close()
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
	def _recv_(self):
		ret = self.sk.recv(1024).decode('big5', 'replace')
		self.stream.feed(ret)
		if hasattr(self, "show") and callable(self.show):
			self.show()
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
	def show(self):
		""" Show the screen """
		if self.DEBUG:
			print "====\n%s\n====" %"\n".join(self.screen.display)
	def reset(self):
		self.screen.reset()
class PTTAllPostUser(PTT):
	def __init__(self, **kwargs):
		user	= kwargs['usr']
		pwd		= kwargs['pwd']
		host	= kwargs['host'] if 'host' in kwargs else ("ptt.cc", 23)
		multi	= kwargs['killReplica'] if 'killReplica' in kwargs else True
		self.nr		= kwargs['nr'] if 'nr' in kwargs else 100
		self.start	= kwargs['start'] if 'start' in kwargs else None
		self.db_usr	= kwargs['db_usr'] if 'db_usr' in kwargs else None
		self.db_pwd	= kwargs['db_pwd'] if 'db_pwd' in kwargs else None
		if 'timeout' in kwargs: self.TIMEOUT = int(kwargs['timeout'])

		super(PTTAllPostUser, self).__init__(user, pwd, host, killReplica=multi)
		self.gotoAllPost()
	def run(self):
		if self.start:
			self._send_("%s\r\n" %self.start)
		else:
			self._send_(self.END)

		while True:
			ret = []
			cnt = 0			
			for _ in xrange(self.nr):
				try:
					ret += [self.GetUser(NR=str(_+1))]
				except Exception, e:
					if 1 < self.DEBUG:
						print Exception(e)
					cnt += 1

				self._send_(self.UP)
				if cnt > 20:
					if 0 < self.DEBUG:
						print "Too many error"
					return

			if not self.db_usr or not self.db_pwd:
				continue

			with tempfile.NamedTemporaryFile() as f:
				for line in ret:
					name, alias = line[0].split('(')[0], line[0].split('(')[1]
					name, alias = name.strip(), alias.strip()[:-1]
					now = [n for n in line[1].split(' ') if n][0].split('/')
					now = "-".join([now[-1]] + now[:-1])

					tmp = "%s&&%s&&%s&&%s&&%s&&%s"
					tmp = tmp %(name, alias, now, line[2], ",".join(line[3]), ",".join(line[4]))
					f.file.write("%s\n" %tmp.encode('utf-8'))

				shell = r"LOAD DATA LOCAL INFILE '%s' REPLACE into TABLE PTT "\
						r"character set utf8 " \
						r"fields terminated by '&&' lines terminated by '\n'"
				shell = shell %(f.name)
				cmd = 'mysql -h ds -u %s -D cmj --password=%s -e "%s"'
				cmd = cmd %(self.db_usr, self.db_pwd, shell)
				st, ret = commands.getstatusoutput(cmd)
				if st and 0 < self.DEBUG:
					print "Execute %s failed\n\t[%d] %s" %(cmd, st, ret)
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
			#self.show(debug=True)
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
	
		if False:
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
class PTTOnlineUser(PTT):
	def __init__(self, **kwargs):
		user	= kwargs['usr']
		pwd		= kwargs['pwd']
		host	= kwargs['host'] if 'host' in kwargs else ("ptt.cc", 23)
		multi	= kwargs['killReplica'] if 'killReplica' in kwargs else True
		self.nr		= kwargs['nr'] if 'nr' in kwargs else 100
		self.start	= kwargs['start'] if 'start' in kwargs else None
		self.db_usr	= kwargs['db_usr'] if 'db_usr' in kwargs else None
		self.db_pwd	= kwargs['db_pwd'] if 'db_pwd' in kwargs else None
		if 'timeout' in kwargs: self.TIMEOUT = int(kwargs['timeout'])

		super(PTTOnlineUser, self).__init__(user, pwd, host, killReplica=multi)
		self.gotoOnlineUser()
	def run(self):
		if self.start:
			self._send_("%s\r\n" %self.start)

		while True:
			ret = []
			cnt = 0			
			for _ in xrange(self.nr):
				try:
					ret += [self.GetUser(NR=str(_+1))]
				except Exception, e:
					if 1 < self.DEBUG:
						print Exception(e)
					cnt += 1

				self._send_(self.UP)
				if cnt > 20:
					if 0 < self.DEBUG:
						print "Too many error"
					return

			if not self.db_usr or not self.db_pwd:
				continue

			with tempfile.NamedTemporaryFile() as f:
				for line in ret:
					name, alias = line[0].split('(')[0], line[0].split('(')[1]
					name, alias = name.strip(), alias.strip()[:-1]
					now = [n for n in line[1].split(' ') if n][0].split('/')
					now = "-".join([now[-1]] + now[:-1])

					tmp = "%s&&%s&&%s&&%s&&%s&&%s"
					tmp = tmp %(name, alias, now, line[2], ",".join(line[3]), ",".join(line[4]))
					f.file.write("%s\n" %tmp.encode('utf-8'))

				shell = r"LOAD DATA LOCAL INFILE '%s' REPLACE into TABLE PTT "\
						r"character set utf8 " \
						r"fields terminated by '&&' lines terminated by '\n'"
				shell = shell %(f.name)
				cmd = 'mysql -h ds -u %s -D cmj --password=%s -e "%s"'
				cmd = cmd %(self.db_usr, self.db_pwd, shell)
				st, ret = commands.getstatusoutput(cmd)
				if st and 0 < self.DEBUG:
					print "Execute %s failed\n\t[%d] %s" %(cmd, st, ret)
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
	def gotoOnlineUser(self):
		self._repeatSendUntilRecv_(self.CTRL_U, MatchStr("休閒聊天".decode('utf-8'), -1),MatchStr("聊天/寫信".decode('utf-8'), -1))
	def GetUser(self, NR=None):
		def getToken(line, token):
			import re
			req = re.search(token, line)
			if req:
				return req.group(0)
			else:
				return None
		self.reset()
		self._send_("q")

		## Get precise info
		pos = self._recvUntil_(	MatchStr("請按任意鍵繼續".decode('utf-8'), -1), 
								MatchStr("▄▄▄▄▄▄".decode('utf-8'), -1),
								MatchStr("▄▄▄▄▄▄".decode('utf-8')))

		pos = self.screen.display[1].find("《經濟狀況》".decode('utf-8'))
		if pos == -1:
			#self.show(debug=True)
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
	
		if False:
			print "%s - %s [%s] [%s]" %(nr, name, date, last)
			if mails:
				print "    [%s]" %",".join(mails)
			if links:
				print "    [%s]" %",".join(links)
		
		## FIXME
		self.screen.reset()

		self._send_(' ')
		self._recvUntil_(MatchStr("休閒聊天".decode('utf-8'), -1), MatchStr("聊天/寫信".decode('utf-8'), -1))
		return name, date.split(' ')[0], last, mails, links
		#self.test()
	def test(self):
		self._recvUntil_("測試, 不可能停".decode('utf-8'))
class PTT2OnlineUser(PTT):
	def __init__(self, **kwargs):
		user	= kwargs['usr']
		pwd		= kwargs['pwd']
		host	= kwargs['host'] if 'host' in kwargs else ("ptt2.cc", 23)
		multi	= kwargs['killReplica'] if 'killReplica' in kwargs else True
		self.nr		= kwargs['nr'] if 'nr' in kwargs else 100
		self.start	= kwargs['start'] if 'start' in kwargs else None
		self.db_usr	= kwargs['db_usr'] if 'db_usr' in kwargs else None
		self.db_pwd	= kwargs['db_pwd'] if 'db_pwd' in kwargs else None
		if 'timeout' in kwargs: self.TIMEOUT = int(kwargs['timeout'])

		super(PTT2OnlineUser, self).__init__(user, pwd, host, killReplica=multi)
		self.gotoOnlineUser()
	def run(self):
		if self.start:
			self._send_("%s\r\n" %self.start)

		while True:
			ret = []
			cnt = 0			
			for _ in xrange(self.nr):
				try:
					ret += [self.GetUser(NR=str(_+1))]
				except Exception, e:
					if 1 < self.DEBUG:
						print Exception(e)
					cnt += 1

				self._send_(self.UP)
				if cnt > 20:
					if 0 < self.DEBUG:
						print "Too many error"
					return

			if not self.db_usr or not self.db_pwd:
				continue

			with tempfile.NamedTemporaryFile() as f:
				for line in ret:
					name, alias = line[0].split('(')[0], line[0].split('(')[1]
					name, alias = name.strip(), alias.strip()[:-1]
					now = [n for n in line[1].split(' ') if n][0].split('/')
					now = "-".join([now[-1]] + now[:-1])

					tmp = "%s&&%s&&%s&&%s&&%s&&%s"
					tmp = tmp %(name, alias, now, line[2], ",".join(line[3]), ",".join(line[4]))
					f.file.write("%s\n" %tmp.encode('utf-8'))

				shell = r"LOAD DATA LOCAL INFILE '%s' REPLACE into TABLE PTT2 "\
						r"character set utf8 " \
						r"fields terminated by '&&' lines terminated by '\n'"
				shell = shell %(f.name)
				cmd = 'mysql -h ds -u %s -D cmj --password=%s -e "%s"'
				cmd = cmd %(self.db_usr, self.db_pwd, shell)
				st, ret = commands.getstatusoutput(cmd)
				if st and 0 < self.DEBUG:
					print "Execute %s failed\n\t[%d] %s" %(cmd, st, ret)
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
	def gotoOnlineUser(self):
		self._repeatSendUntilRecv_(self.CTRL_U, MatchStr("休閒聊天".decode('utf-8'), -1),MatchStr("聊天/寫信".decode('utf-8'), -1))
	def GetUser(self, NR=None):
		def getToken(line, token):
			import re
			req = re.search(token, line)
			if req:
				return req.group(0)
			else:
				return None
		self.reset()
		self._send_("q")

		## Get precise info
		pos = self._recvUntil_(	MatchStr("請按任意鍵繼續".decode('utf-8'), -1), 
								MatchStr("▄▄▄▄▄▄".decode('utf-8'), -1),
								MatchStr("▄▄▄▄▄▄".decode('utf-8')))

		pos = self.screen.display[1].find("《經濟狀況》".decode('utf-8'))
		if pos == -1:
			#self.show(debug=True)
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
	
		if False:
			print "%s - %s [%s] [%s]" %(nr, name, date, last)
			if mails:
				print "    [%s]" %",".join(mails)
			if links:
				print "    [%s]" %",".join(links)
		
		## FIXME
		self.screen.reset()

		self._send_(' ')
		self._recvUntil_(MatchStr("休閒聊天".decode('utf-8'), -1), MatchStr("聊天/寫信".decode('utf-8'), -1))
		return name, date.split(' ')[0], last, mails, links
		#self.test()
	def test(self):
		self._recvUntil_("測試, 不可能停".decode('utf-8'))

def Robust(func):
	def wrapper(*args, **kwargs):
		while True:
			try:
				func(*args, **kwargs)
			except KeyboardInterrupt:
				continue
			except Exception, e:
				continue
			time.sleep(1)
	wrapper.func_name = func.func_name
	wrapper.func_doc  = func.func_doc
	globals()['Robust%s' %func.func_name] = wrapper
	return func
@Robust
def AllPostUser(**kwargs):
	"""
	@usr:			User
	@pwd:			Password
	@db_usr:		DB User
	@db_pwd:		DB Password
	@timeout:		timeout[15]
	@killReplica:	Kill Replica [True]
	"""
	ptt = PTTAllPostUser(**kwargs)
	ptt.run()
	del ptt
@Robust
def OnlineUser(**kwargs):
	"""
	@usr:			User
	@pwd:			Password
	@db_usr:		DB User
	@db_pwd:		DB Password
	@timeout:		timeout[15]
	@killReplica:	Kill Replica [True]
	"""
	ptt = PTTOnlineUser(**kwargs)
	ptt.run()
	del ptt
@Robust
def P2OnlineUser(**kwargs):
	"""
	@usr:			User
	@pwd:			Password
	@db_usr:		DB User
	@db_pwd:		DB Password
	@timeout:		timeout[15]
	@killReplica:	Kill Replica [True]
	"""
	ptt = PTT2OnlineUser(**kwargs)
	ptt.run()
	del ptt

JOB = RobustAllPostUser, RobustOnlineUser, RobustP2OnlineUser
