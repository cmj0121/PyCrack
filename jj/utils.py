#! /usr/bin/env python
#! coding: utf-8

def regExit(fn):
	""" Register callback function when exit program """
	import atexit
	atexit.register(fn)
	return fn
def clearPyc():
	""" Remove all .pyc file """
	import os

	cmd = "find . | grep .pyc$"
	ret = [_ for _ in os.popen(cmd).read().split('\n') if _]
	for _ in ret:
		os.unlink(_)

def main():
	import doctest
	doctest.testmod()
if __name__ == "__main__": main()

