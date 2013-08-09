from . import task

class COMMON(object):
	task = task.Task()
	def __del__(self):
		self.task.DEL()
	@property
	def clear(self):
		import os
		print "\033[0m"
		os.system('clear')
	@property
	def selftest(self):
		import doctest
		doctest.testmod()
