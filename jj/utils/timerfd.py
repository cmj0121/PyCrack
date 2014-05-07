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
	def read(self, bufsiz=4096):
		return os.read(self.fd, bufsiz)
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

	>>> timer = TimerFD()
	>>> fd = timer.create()
	
	"""
	def __init__(self, shardLib="libc.so.6"):
		self.libc = cdll.LoadLibrary(shardLib)
	def create(self, clockid=CLOCK_REALTIME, flags=0):
		timerfd_create = self.libc.timerfd_create
		timerfd_create.argtypes = [c_int, c_int]
		timerfd_create.restype = c_int

		fd = timerfd_create(clockid, flags)
		return TimerFile(fd)
	def settime(self, fd, flags, newTimeSpec, oldTimeSpec, START_FROM_NOW=False):
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

		if START_FROM_NOW:
			clock_gettime = libc.clock_gettime
			clock_gettime.argtypes = [c_int, POINTER(TimeSpec)]
			clock_gettime.restype  = c_int

			now = TimeSpec()
			if 0 > clock_gettime(CLOCK_MONOTONIC, byref(now)):
				raise TimerFDError("Cannot get the current time")
			newTimeSpec.it_value += now
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

