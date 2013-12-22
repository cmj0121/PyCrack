#! /usr/bin/env python
#! coding: utf-8

import os
import socket
import time

class Switch(object):
	PIPE = "/tmp/muq_pipe"
	WAIT = 1
	LISTEN_NR = 100
	def __init__(self, isVender=False):
		self._link_(isVender)
	def _link_(self, vender):
		""" Link to the switch """
		## Delete original switch file
		if os.path.exists(self.PIPE): os.unlink(self.PIPE)

		sk = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
		while True:
			try:
				if vender:
					sk.bind(self.PIPE)
					sk.listen(selk.LISTEN_NR)
				else:
					sk.connect(self.PIPE)
			except socket.error as e:
				if 2 == e.errno:
					time.sleep(self.WAIT)
					continue
				raise
			except Exception as e:
				raise
			else:
				break

		self._sk_ = sk
if __name__ == "__main__":
	import sys

	s = Switch()
	print s
