#! /usr/bin/env python
#! coding: utf-8

import commands
import os
from sdk.lockfile import LockFile
import socket
import yaml
import hashlib
from tempfile import NamedTemporaryFile

class TableObject(object):
	_key_ = []
	def __init__(self, **kwarg):
		self.load(**kwarg)
	def __str__(self):
		return  "\t".join([getattr(self, self._dumpkey_(_)) for _ in self._key_])
	def _dumpkey_(self, key):
		return "%s_%s" %(hash(self), key)
	def _dump_(self, key, kwarg):
		if key in kwarg:
			setattr(self, self._dumpkey_(key), "%s" %kwarg[key])
		else:
			setattr(self, self._dumpkey_(key), "")
	def load(self, **kwarg):
		for _ in self._key_:
			self._dump_(_, kwarg)
		return self
	def dict(self):
		return {_: self._dumpkey_(_) for _ in self._key_}

class INFO(object):
	_name_ = "USERINFO"

	TABLE =[	"id VARCHAR(32) KEY",
				"name VARCHAR(32)",
				"alias VARCHAR(32) CHARACTER SET UTF8",
				"ip CHAR(16)",
				"lastLogin DATE",
				"site VARCHAR(128)",
				"modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP on UPDATE CURRENT_TIMESTAMP",
				"mail TEXT",
				"link TEXT"]
	FIELD = ["id", "name", "alias", "ip", "lastLogin", "site", "link", "mail"]
	THRESHOLD = 1
	def __init__(self, usr, pwd):
		self.db_usr = usr
		self.db_pwd = pwd
		self._createTable_()
		self.queue, self.queue_fromat = set(), TableObject()
		self.queue_fromat._key_ = self.FIELD
	def __del__(self):
		self._store_("\n".join(self.queue))
		self.queue.clear()
	def __add__(self, data):
		self.queue.add(unicode(self.queue_fromat.load(**data)))
		if len(self) > self.THRESHOLD:
			self._store_("\n".join(self.queue))
			self.queue.clear()
		return self
	def __len__(self):
		return len(self.queue)
	def _exec_(self, cmd, site="ds", db="cmj"):
		""" Always input the unicode and recovery to system encoding """
		import sys

		SYS_ENCODING = sys.getfilesystemencoding()
		shell = u'mysql -u {user} --password={password} -h {site} -D {db} -e "{cmd};"'
		shell = shell.format(	user=self.db_usr, password=self.db_pwd,
								site=site, db=db, cmd=cmd)
		return commands.getstatusoutput(shell.encode(SYS_ENCODING))
	def __contains__(self, key):
		return key in ("field", "fn")
	def __getitem__(self, key):
		if "field" == key:
			return self._name_
		elif "fn" == key:
			return self.__add__
		else:
			raise KeyError("Key %s not found" %key)

	def _store_(self, value):
		if value:
			NAME = ".insert"
			with open(NAME, 'w') as f:
				f.write(value.encode('utf-8'))
			cmd =	r"LOAD DATA LOCAL INFILE '{file}' REPLACE INTO TABLE {table} " \
					r"CHARACTER SET UTF8 " \
					r"FIELDS TERMINATED BY '\t' LINES TERMINATED BY '\n' " \
					r"({field})"
			cmd = cmd.format(table=self._name_, file=NAME, field=",".join(self.FIELD))
			st, ret = self._exec_(cmd)
			os.unlink(NAME)
			ret = [_ for _ in ret.split('\n') if _]
			if st:
				raise SystemError("Insert data failed:\n\t%s\n\t%s" %(cmd.encode('utf-8'), "\n\t".join(ret)))
	def _createTable_(self):
		table = ",".join(self.TABLE)
		cmd = u"CREATE TABLE IF NOT EXISTS {name} ({table})"
		cmd = cmd.format(name=self._name_, table=",".join(self.TABLE))
		st, ret = self._exec_(cmd)
		ret = [_ for _ in ret.split('\n') if _]
		if st:
			raise SystemError("Create table failed: \n\t%s\n\t%s" %(cmd, "\n\t".join(ret)))
	def _showTable_(self):
		cmd = u"DESC %s" %self._name_
		st, ret = self._exec_(cmd)
		if st:
			raise SystemError("Show table (%s) failed" %self._name_)

		
		ret = [_.split('\t') for _ in ret.split('\n') if _]
		return [{ret[0][n]: _[n] for n in range(len(_))} for _ in ret[1:]]
	def _dropTable_(self):
		cmd = u"DROP TABLE %s" %self._name_
		st, ret = self._exec_(cmd)
		if st:
			raise SystemError("Cannot drop table (%s): %s" %(self._name_, ret))
	table = property(_showTable_, _createTable_, _dropTable_)

class Reward(LockFile):
	_name_ = "reward"
	_PIPE_ = "/tmp/reward.pipe"
	_supplant_ = True

	def __init__(self, *backend):
		super(Reward, self).__init__()
		self._backend_ = []
		for _ in backend:
			if "field" in _ and  "fn" in _ and callable(_['fn']):
				self._backend_ += [_]
	def __del__(self):
		if os.path.exists(self._PIPE_):
			os.unlink(self._PIPE_)
		while len(self._backend_):
			del self._backend_[0]
		super(Reward, self).__del__()

	def _bind_(self):
		if os.path.exists(self._PIPE_):
			os.unlink(self._PIPE_)

		sk = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
		sk.bind(self._PIPE_)
		return sk
	def _proccess_(self, data, addr=None):
		data = yaml.load(data)
		for _ in self._backend_:
			if _['field'] == data['field']:
				_['fn'](data)
	def runReward(self, size):
		sk = self._bind_()
		while True:
			data, addr = sk.recvfrom(size)
			self._proccess_(data, addr)
	def run(self, size=4096):
		try:
			self.runReward(size)
		except KeyboardInterrupt as e:
			return
		except Exception as e:
			raise
def runRewardServer(usr=None, pwd=None):
	import traceback
	import getpass
	if not usr or not pwd:
		usr = raw_input('Input the user name: ')
		pwd = getpass.getpass('Password: ')
	try:
		info = INFO(usr, pwd)
		reward = Reward(info)
		reward.run()
	except KeyboardInterrupt as e:
		pass
	except Exception as e:
		print Exception(e)
		print 
		traceback.print_exc()
	finally:
		del reward
	

class RewardCli():
	_name_ = "Reward"
	_PIPE_ = "/tmp/reward.pipe"

	def __init__(self, field, *data):
		data = [_.split('=') for _ in data if "=" in _]
		data = {_[0]: "=".join(_[1:]) for _ in data}
		data.update({'field': field})
		self._send_(data)
	def _send_(self, data):
		sk = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
		sk.sendto(yaml.dump(data), self._PIPE_)

if __name__ == "__main__":
	import sys

	if 1 < len(sys.argv):
		cli = RewardCli(*sys.argv[1:])
	else:
		print "Run reward server..."
		runRewardServer()
