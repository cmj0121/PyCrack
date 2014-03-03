#! /usr/bin/env python
#! coding: utf-8

import os

class LockFile(object):
	""" Ensure process is running and exclusive or not 
		If allow multi-proccess running, PID file will record all process PID
	"""
	_exclusive_ = True
	_supplant_ = True
	def __init__(self):
		if os.getpid() != self.pid and self._exclusive_:
			if self._supplant_:
				os.kill(self.pid, 9)
			else:
				raise SystemError("Process (%d) is running." %self.pid)

		## Record the PID into PID file
		with open(self._pidFile_, "w" if self._supplant_ else "a") as f:
			f.write("%d\n" %os.getpid())
	def __del__(self):
		with open(self._pidFile_) as f:
			pidList = [_ for _ in f.read().split('\n') if _]
			pid = os.getpid()
			if pid in pidList: pidList.remove(pid)
		with open(self._pidFile_, "w") as f:
			f.write("%s\n" %"\n".join(pidList))


	@property
	def _pidFile_(self):
		if hasattr(self, "_name_"):
			proc = self._name_
		else:
			proc = self.__class__.__name__
		return "/tmp/{proc}.pid".format(proc=proc)
	@property
	def pid(self):
		""" Return the running process PID if pid file exists """
		if self._exclusive_ and os.path.isfile(self._pidFile_):
			with open(self._pidFile_) as f:
				## Always return first process
				pid = [_ for _ in f.read().split('\n') if _][0]

			## Delete pid file if process is not exist
			if not os.path.isdir("/proc/%s" %pid):
				os.unlink(self._pidFile_)
				pid = os.getpid()
		else:
			pid = os.getpid()
		return int(pid)
if __name__ == "__main__":
	raise NotImplementedError
