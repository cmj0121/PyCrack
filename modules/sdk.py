#! coding: utf-8

import pyte
import socket

socket.setdefaulttimeout(15)
class WebReq(object):
	"""
		[Int]		Status code
		[Dict]		Cookies
		[Dict]		HTTP Header
		[String]	Web Page
	"""
	def __init__(self, request, code, content, cookies={}, headers={}):
		self.request = request
		self.code    = code
		self.content = content
		self.cookies = cookies
		self.headers = headers
	def __str__(self):
		return """Request [%s]
    Status code: %.10s
    Cookie: %.40s
    Header: %.40s
    Content: %.40s
""" %(self.request, self.code, self.cookies, self.headers, self.content)
class MatchStr(object):
	def __init__(self, key, line=None):
		self.key, self.line = key, line
class PTT(object):
	UP = '\x1bOA'
	DOWN = '\x1bOB'
	LEFT = '\x1bOC'
	RIGHT = '\x1bOD'
	HOME = '\x1b[1~'
	END = '\x1b[4~'
	CTRL_Q = "\x11"
	CTRL_W = "\x17"
	CTRL_U = '\x15'
	DEBUG = False

	def __init__(self, user, pwd, host=("ptt.cc", 23), killReplica=True):
		self.screen = pyte.Screen(80, 24)
		self.stream = pyte.Stream()

		self.stream.attach(self.screen)
		self.login(user, pwd, host, killReplica)
	def __del__(self):
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
	def login(self, user, pwd, host, killReplica=True):
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
			self._send_("Y\r\n")
			self._recvUntil_(MatchStr("請按任意鍵繼續".decode('utf-8')))
		self._repeatSendUntilRecv_(" ", MatchStr("(G)oodbye".decode('utf-8')))
	def show(self):
		""" Show the screen """
		if self.DEBUG:
			print "====\n%s\n====" %"\n".join(self.screen.display)
def wrapGetWebPage(url, port=80):
	"""
	Get the web page by wrap function.

	@PARAM:
		url			Target website url
		[port]		Default: 80

	@RETURN:
		[WebReq]	Wrapped request object
	"""
	import requests

	if not url.startswith("http://"): url = "http://%s" %url

	req = requests.get(url)
	return WebReq(url, req.status_code, req.content, req.cookies, req.headers)
