#! /usr/bin/env python
#! coding: utf-8

from getpass import getpass
from multiprocessing import Process
import sys


class _Task_(object):
	def __init__(self, func):
		self.func = func
	def __str__(self):
		return "Process [%s] is %s" %(self.func.func_name, "alive" if self.proc.is_alive() else "dead")
	def DEL(self):
		if hasattr(self, 'proc') and hasattr(self.proc, "is_alive") and self.proc.is_alive():
			self.proc.terminate()
	def _loadParm_(self, func_name, doc):
		while True:
			print "Do you want to run %s [y/N]:" %(func_name), 
			ans = raw_input().upper()
			if ans and ans[0] not in ('Y', 'N', ''):
				continue

			if not ans: ans = 'N'
			break
		if "N" == ans[0]: return

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
		func = eval(self.func) if isinstance(self.func, str) else self.func
		parm = self._loadParm_(func.func_name, func.func_doc)
		if not parm: return

		self.proc = Process(target=func, kwargs=parm)
		self.proc.start()
		return True
class Task(object):
	CURRENT_JOB = []

	def __str__(self):
		ret, cnt = [], 1
		for n in self.CURRENT_JOB:
			ret += ["[%d] %s" %(cnt, str(n))]
			cnt += 1
		if ret: return "\n".join(ret)
		else: return "No current job or task"
	def __repr__(self):
		return str(self)
	def DEL(self):
		for n in self.CURRENT_JOB:
			n.DEL()
	def __del__(self):
		self.DEL()
	def __delitem__(self, index):
		del self.CURRENT_JOB[index]
	def __getitem__(self, index):
		return self.CURRENT_JOB[index]
	def _addJob_(self, func):
		if not isinstance(func, list) and not isinstance(func, tuple):
			func = (func,)
		for f in func:
			t = _Task_(f)
			if t.run():
				self.CURRENT_JOB += [t]
	def _deljob_(self, index=0):
		del self.CURRENT_JOB[index]
	addJob = property(__str__, _addJob_, None)

