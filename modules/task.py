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
	def __del__(self):
		import time
		print "Del"
		if hasattr(self, "proc") and self.proc.is_alive():
			self.proc.terminate()
			time.sleep(0.1)
			self.proc.join()
	def __str__(self):
		if hasattr(self, "proc") and self.proc.is_alive():
			st = "Alive"
		else:
			st = "Dead"
		return "Process [%s] is %s" %(self.func.func_name, st)
	def __repr__(self):
		return str(self)

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
		return True
def test_Task_():
	import commands
	import sys
	def foo():
		import time
		while True: time.sleep(1)

	t = _Task_(foo)
	t.run()
	st, ret = commands.getstatusoutput("ps aux | grep python | grep %s" %sys.argv[0])
	ret = [_ for _ in ret.split("\n") if _]
	if 0 != st or 3 != len(ret):
		raise SystemError("Test faild:\n\t%s" %"\n\t".join(ret))

class Task(object):
	def __init__(self):
		self._jobs_ = []
	def __str__(self):
		return self.job
	def __repr__(self):
		return str(self)
	def __del__(self):
		print "Del Task"
		while len(self._jobs_):
			del self._jobs_[0]
	def __delitem__(self, index):
		del self._jobs_[index]
	def __getitem__(self, index):
		return self._jobs_[index]
	def __add__(self, func):
		self._addJob_(func)
		return self
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
			else:
				print "[%s] cannot run" %func
	def _deljob_(self, index=0):
		if isinstance(index, int):
			del self._jobs_[index]
		else:
			raise KeyError("Not support key=%s" %key)
	job = property(_getJob_, _addJob_, _deljob_)


def test():
	test_Task_()

if __name__ == "__main__":
	test()
