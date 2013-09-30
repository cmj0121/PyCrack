#! /usr/bin/env python
#! coding: utf-8

from getpass import getpass
from multiprocessing import Process
import os
import sys


class _Task_(object):
	def __init__(self, func):
		if (isinstance(func, str) or isinstance(func, unicode)):
			try:
				self.func = eval(func)
			except NameError as e:
				raise SystemError("Function %s is not defined" %func)
		elif callable(func):
			self.func = func
		else:
			raise SystemError("We only support run function")

		if not callable(self.func):
			raise SystemError("We only support run function")
	def __del__(self):
		if -1 == self.pid: return

		os.unlink(self.pidFile)
		self.proc.terminate()
		self.proc.join()
	def __str__(self):
		if -1 == self.pid:
			st = "dead"
		else:
			with open(self.pidFile) as f:
				st = "alive (%s)" %f.read()
		return "Process [%s] is %s" %(self.func.func_name, st)
	def __repr__(self):
		return str(self)

	@property
	def pid(self):
		if hasattr(self, "proc") and self.proc.is_alive():
			return self.proc.pid
		else:
			return -1
	@property
	def pidFile(self):
		if -1 == self.pid:
			raise SystemError("Process not run!")
		return "/tmp/task.{pid}".format(pid=self.pid)

	def _loadParm_(self, func_name, doc):
		while True:
			ans = raw_input("Do you want to run %s [y/N]: " %(func_name)).upper()
			if ans and ans[0] not in ('Y', 'N', ''):
				continue

			if not ans: ans = 'N'
			break
		if "N" == ans[0]: return

		if not doc: return {}
		elif not isinstance(doc, str) and not isinstance(doc, unicode): return {}
		parm = {}

		for n in (line for line in doc.split('\n') if line.strip().startswith('@')):
			key = n.split(':')
			key, value = key[0].strip()[1:], ":".join(key[1:]).strip()
			value = "%s%s: " %(sys.ps2, value)
			parm[key] = getpass(value) if "Password" in value.title() else raw_input(value)

			if not parm[key] and '[' in value:
				parm[key] = value.split('[')[-1].split(']')[0]

			try:
				parm[key] = eval(parm[key])
			except Exception, e:
				pass

		return parm
	def run(self):
		func = self.func

		parm = self._loadParm_(func.func_name, func.func_doc)
		if not isinstance(parm, dict): return

		self.proc = Process(target=func, kwargs=parm)
		self.proc.start()
		if not os.path.exists(self.pidFile):
			with open(self.pidFile, "w") as f:
				pass
		return True
class Task(object):
	_jobs_ = []

	def __str__(self):
		return self.job
	def __repr__(self):
		return str(self)
	def __del__(self):
		del self._jobs_[:]
	def __delitem__(self, index):
		del self._jobs_[index]
	def __getitem__(self, index):
		return self._jobs_[index]
	def _getJob_(self):
		ret, cnt = [], 1
		for n in self._jobs_:
			ret += ["[%d] %s" %(cnt, str(n))]
			cnt += 1
		if ret: return "\n".join(ret)
		else: return "No current job or task"
	def _addJob_(self, func):
		if not isinstance(func, list) and not isinstance(func, tuple):
			func = (func, )
		for f in func:
			t = _Task_(f)
			if t.run():
				self._jobs_ += [t]
	def _deljob_(self, index=0):
		if isinstance(index, int):
			del self._jobs_[index]
		else:
			raise KeyError("Not support key=%s" %key)
	job = property(_getJob_, _addJob_, _deljob_)

