#! /usr/bin/env python
#! coding: utf-8
__author__ = "cmj"
__copyright__ = "Copyright (C) 2014 cmj"

from ctypes import Structure, cdll
from ctypes import POINTER, CFUNCTYPE, byref, pointer
from ctypes import c_int, c_long
import os
import struct

class TimeSpec(Structure):
	""" A wrapper for struct timespec. Ref: include/time.h

	>>> ts = TimeSpec()
	>>> ts.tv_sec, ts.tv_nsec = 1, 0
	>>> print ts
	<TimeSpec|(1, 0)>

	>>> ts2 = TimeSpec(2, 1)
	>>> print ts2
	<TimeSpec|(2, 1)>

	>>> print ts
	<TimeSpec|(1, 0)>

	>>> print ts+ts2
	<TimeSpec|(3, 1)>
	"""
	_fields_ = [("tv_sec", c_long), ("tv_nsec", c_long)]
	def __init__(self, tv_sec=0, tv_nsec=0):
		self.tv_sec, self.tv_nsec = tv_sec, tv_nsec
	def __repr__(self):
		return "<TimeSpec|(%d, %d)>" %(self.tv_sec, self.tv_nsec)
	def __add__(self, obj):
		if not isinstance(obj, TimeSpec):
			raise TypeError("Only accept TimeSpec")
		return TimeSpec(self.tv_sec+obj.tv_sec, self.tv_nsec+obj.tv_nsec)
class iTimerSpec(Structure):
	""" A wrapper for struct itimerspec. Ref: include/time.h
	>>> its = iTimerSpec(TimeSpec(0, 0), TimeSpec(1, 0))
	>>> print its
	<iTimeSpec|interval: <TimeSpec|(0, 0)>, value: <TimeSpec|(1, 0)>>

	"""
	_fields_ = [("it_interval", TimeSpec), ("it_value", TimeSpec)]
	def __init__(self, ts1=None, ts2=None):
		self.it_interval, self.it_value = ts1, ts2
	def __repr__(self):
		return "<iTimeSpec|interval: %s, value: %s>" %(self.it_interval, self.it_value)
class TimerFile(file):
	""" A wrapper for fd struct to simulate as file object in python. """
	def __init__(self, fd):
		self.fd = fd
	def __close__(self):
		try:
			self.close()
		except:
			pass
	def close(self):
		os.close(self.fd)
	def read(self):
		return os.read(self.fd, 4096)
	def fileno(self):
		return self.fd
	def next(self):
		raise NotImplementedError


## Defined in include/bits/time.h
CLOCK_REALTIME				= 0
CLOCK_MONOTONIC				= 1
CLOCK_PROCESS_CPUTIME_ID	= 2
CLOCK_THREAD_CPUTIME_ID		= 3
CLOCK_MONOTONIC_RAW			= 4
CLOCK_REALTIME_COARSE		= 5
CLOCK_MONOTONIC_COARSE		= 6
CLOCK_BOOTTIME				= 7
CLOCK_REALTIME_ALARM		= 8
CLOCK_BOOTTIME_ALARM		= 9

class TimerFDError(Exception):
	""" Customize Exception used in TimerFD """
	def __init__(self, msg):
		self.msg = msg
	def __repr__(self):
		return "TimerFDError: %s" %self.msg
class TimerFD(object):
	""" A timer fd (File Descriptor) which is wrapped via ctypes

	>>> import time
	>>> timer = TimerFD()
	>>> for n in range(1, 4):
	... 	fd = timer.getTimer(interval=n)
	... 	ret = fd.read()
	... 	start = time.time()
	... 	ret = fd.read()
	... 	end = time.time()
	... 	if abs((end-start) - n)>0.01:
	... 		print "Faild on %s: %s" %(n, abs(n-(end-start)))
	
	"""
	def __init__(self, shardLib=None):
		platform = os.uname()[0]
		if "Linux" == platform: shardLib = "libc.so.6"
		else:
			raise TimerFDError("Not Support Platform %s")

		self.libc = cdll.LoadLibrary(shardLib)

	def getTimer(self, start=1, interval=1):
		""" Easy way to get the timer fd """
		fd  = self.create()
		x, y = int(interval), int((interval-int(interval))*(10**9))
		its = iTimerSpec(TimeSpec(x, y), TimeSpec(start, 0))
		self.settime(fd, 0, its, None)
		return fd
	def create(self, clockid=CLOCK_REALTIME, flags=0):
		timerfd_create = self.libc.timerfd_create
		timerfd_create.argtypes = [c_int, c_int]
		timerfd_create.restype = c_int

		fd = timerfd_create(clockid, flags)
		return TimerFile(fd)
	def settime(self, fd, flags, newTimeSpec, oldTimeSpec):
		if isinstance(fd, int): fd = fd
		elif isinstance(fd, file): fd = fd.fileno()
		else: raise TypeError("fd only accept File or File Descriptors")

		if newTimeSpec and not isinstance(newTimeSpec, iTimerSpec):
			raise TypeError("newTimeSpec only accept NULL or iTimerSpec")
		if oldTimeSpec and not isinstance(oldTimeSpec, iTimerSpec):
			raise TypeError("oldTimeSpec only accept NULL or iTimerSpec")

		timerfd_settime = self.libc.timerfd_settime
		timerfd_settime.argtypes = [c_int, c_int, POINTER(iTimerSpec), POINTER(iTimerSpec)]
		timerfd_settime.restype  = c_int

		return timerfd_settime(fd, flags,
			pointer(newTimeSpec) if newTimeSpec else None,
			byref(oldTimeSpec) if oldTimeSpec else None )
	def gettime(self, fd, timeSpec):
		if isinstance(fd, int): fd = fd
		elif isinstance(fd, file): fd = fd.fileno
		else: raise TypeError("fd only accept File or File Descriptors")

		if timeSpec and not isinstance(timeSpec, iTimerSpec):
			raise TypeError("timeSpec only accept NULL or iTimerSpec")

		return self.libc.timerfd_gettime(fd,
			pointer(timeSpec) if timeSpec else None, None )

if __name__ == "__main__":
	import doctest
	doctest.testmod()
