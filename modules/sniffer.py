#! /usr/bin/env python
#! coding: utf-8

import os
from scapy import route
from scapy.sendrecv import sniff

class PasswdSniffer(object):
	def FTP(self, port=23):
		pass

def main():
	if os.getuid() and os.geteuid():
		print "You need to become root first"
		exit(-1)

if __name__ == "__main__": main()

