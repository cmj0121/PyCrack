#! /usr/bin/env python2
#! coding: utf-8

import interact
import sys

def clear():
	import os

	ret = [_ for _ in os.popen("find . | grep pyc").read().split('\n') if _]
	for _ in ret:
		os.unlink(_)
if __name__ == "__main__":
	if 1 < len(sys.argv) and "clear" == sys.argv[1]:
		clear()
		exit(0)
	interact.interact()
