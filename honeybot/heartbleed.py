#! /usr/bin/env python
#! coding: utf-8

import struct
import socket
import sys
import traceback
import os

class Logging(object):
	def dumpPackage(self, session, package, fd=sys.stdout):
		""" Dump package contain in pretty format """
		session = "==== %s ====\n" %session
		fd.write(session)
		for _ in xrange(0, len(package), 16):
			tmp = [c for c in package[_:_+16]]
			HEX = " ".join(["%02x" %ord(c) for c in tmp])
			STR = "".join((c if 32 <= ord(c) <= 126 else '.' )for c in tmp)
			fd.write("  %04x: %-48s %s\n" %(_, HEX, STR))
		fd.write("\n\n")
		fd.flush()
	def accessLog(self, addr, fd=sys.stdout):
		""" Record the access log """
		fd.write("Try to access TLS from [%s]\n" %str(addr))
		fd.flush()
class TLS(Logging):
	"""
	Reference:
		1. [TLS v1.2], RFC 5246
			http://tools.ietf.org/html/rfc5246
		2. [TLS & DTLS Heartbeat Extension], RFC 6520
			https://tools.ietf.org/html/rfc6520
	"""
	HEADER_LEN = 5
	ALERT      = 21
	HANDSHAKE  = 22
	HEARTBEAT  = 24
	CMD = {"21": "ALERT", "22": "HANDSHAKE", "24": "HEARTBEAT"}

	def TLSDecode(self, buf, type=None):
		""" TLS Header Decode """
		if not type:
			## CMD: 1 / Version: 2 / Length: 2
			return struct.unpack(">BHH", buf[0:5])
		elif self.HANDSHAKE == type:
			## Handshake Type: 1 / Length: 3
			type    = struct.unpack(">B", buf[0])
			length  = struct.unpack(">i", "\x00" + buf[1:4])
			payload = buf[4:]
			return type, length, payload
		elif self.HEARTBEAT == type:
			## Heartbeat Type: 1 / Length: 1
			return struct.unpack('>BH{0}s'.format(len(buf)-3), buf)
	def TLSRecord(self, type, version, payload, length=None):
		""" General format for all TLS records """
		if not length: length = len(payload)
		buf  = struct.pack(">BHH", type, version, length)
		buf += struct.pack(">{0}s".format(len(payload)), payload)
		return buf
	def TLSHandshake(self, type, data, length=None):
		""" Exchange messages during the setup of the TLS session """
		if not length: length = len(data)
		payload  = struct.pack(">B", type)
		payload += struct.pack(">I", length)[1:]
		payload += struct.pack(">{0}s".format(len(data)), data)
		return self.TLSRecord(22, 0x0302, payload)
	def TLSHeartbeat(self, type, data, length=None):
		if type not in (1, 2):
			raise SystemError("TLS Heartbeat only support type: 1(req) / 2 (reply)")

		if not length: length = len(data)
		payload  = struct.pack(">BH", type, length)
		payload += struct.pack(">{0}s".format(len(data)), data)

		## The vulnerability will alow payload > 2^14
		## But we fix size as payload < 32K
		if len(payload) > (2**15):
			raise SystemError("TLS Heartbeat payload only allow < 2^15")
		return self.TLSRecord(24, 32, payload)
class HeartBleed(TLS):
	def __init__(self, port=443, max_client=10):
		if os.getuid()*os.getgid():
			print "HeartBleed honeypot need run as root..."
			exit(-1)
		self.tcpServer(port, max_client)
	def tcpServer(self, port, max_client):
		""" Create TCP Server as SSL/HeartBleed Service"""
		sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			sk.bind(("", port))
			sk.listen(max_client)
			while True:
				cli, addr = sk.accept()
				try:
					self.accessLog(addr)
					self.handle(cli, addr)
				except KeyboardInterrupt:
					cli.close()
					raise KeyboardInterrupt
				except Exception as e:
					print e
				finally:
					cli.close()
		except KeyboardInterrupt:
			print "Exist by CTRL+C"
			sk.close()
			exit(1)
		except Exception as e:
			print e
		finally:
			sk.close()
	def recv(self, cli, length, timeout=3):
		""" Receive all message with timeout / fix length"""
		import select
		import time
		end = time.time() + timeout
		remain_len = length
		data = ""
		while remain_len:
			if (end - time.time()) < 0: return None
			r, _, _ = select.select([cli], [], [], timeout)
			if cli in r:
				buf = cli.recv(remain_len)
				if not buf: return None
				data += buf
				remain_len -= len(buf)
		return data
	def handleHandshake(self, cli, payload):
		def ServerHello(ver, random, sessionID):
			reply  = ""
			reply += struct.pack(">H", ver)
			reply += struct.pack(">32s", random)
			reply += struct.pack(">B", sessionID)
			reply += "\xc0\x13"	## Cipher
			reply += "\x00"		## Compression Methods
			reply += "\x00\x00"	## Number Extension
			return reply
		while payload:
			## Handle HandShake payload
			##	MSG Type: 1 / Length: 3
			type, payload = struct.unpack(">B", payload[0]), payload[1:]
			length, payload = struct.unpack(">I", "\x00" + payload[:3]), payload[3:]

			if 1 == type[0]: ## ClientHello
				ver, random, session = struct.unpack(">H32sB", payload[:35])
				payload = payload[35:]

				cipherLen	= struct.unpack(">H", payload[:2])[0]
				payload		= payload[2:]
				cipher, payload = payload[:cipherLen/2], payload[cipherLen/2:]

				extensionLen= struct.unpack(">H", payload[:2])[0]
				payload 	= payload[2:]
				extension, payload = payload[:extensionLen], payload[extensionLen:]

				reply = ServerHello(ver, random, session)
				cli.send(self.TLSHandshake(2, reply))
			else:
				print "Cannot handle Handshake type: %s %s" %(type, length)
				raise NotImplementedError
	def handle(self, cli, addr):
		""" Handle TLS communication """
		while True:
			## Receive the TLS package
			buf = self.recv(cli, self.HEADER_LEN)
			if not buf: raise SystemError("Not receive any package")
			type, version, length = self.TLSDecode(buf)
			payload = self.recv(cli, length)
			self.dumpPackage("TSL [%s]" %self.CMD[str(type)], buf + payload)

			if type == self.HANDSHAKE:
				self.handleHandshake(cli, payload)
				data = self.TLSHandshake(14, "End Handshake")
				cli.send(data)
			elif type == self.HEARTBEAT:
				type, length, payload = self.TLSDecode(payload, self.HEARTBEAT)
				msg = self.FakeMem(length)
				data = self.TLSHeartbeat(2, msg)
				cli.send(data)
	def FakeMem(self, length):
		msg = "TLS HeartBleed honeypot"
		while len(msg) < length: msg += msg
		return msg[:length]	
def main():
	import doctest
	doctest.testmod()
	honeypot = HeartBleed()
if __name__ == "__main__": main()

