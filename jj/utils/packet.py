#! /usr/bin/env python

import struct


class PacketError(Exception):
	def __init__(self, msg):
		self.msg = msg
	def __str__(self):
		return "PacketError: {0}".format(self.msg)
class Packet(object):
	""" Network packet wrapper and parser.

		NOTE: We always pack / unpack as network-endian

	>>> try:
	... 	p = Packet()
	... except PacketError as e:
	... 	pass
	... else:
	... 	raise Exception

	>>> class Foo(Packet):
	... 	__hdr__ = (("type", "B"), ("version", "H"))
	...
	>>> buf = "\x01\x02\x03\x04\x05"
	>>> f = Foo(buf)
	>>> f.type, f.version
	(1, 515)
	>>> buf[3:] == f.payload
	True
	>>> 5 == len(f)
	True

	>>> f = Foo()
	>>> f.type, f.version = 1, 707
	>>> buf = "\x01\x02\xc3"
	>>> buf == f.pack()
	True
	"""
	__endian__ = "!"
	def __init__(self, buf=None):
		if not hasattr(self, "__hdr__"):
			raise PacketError("You need to set __hdr__ first")

		## Prepare the necessary property
		self.__hdr_fmt__  = self.__endian__
		self.__hdr_fmt__ += "".join([fmt for _, fmt in self.__hdr__])
		self.__hdr_len__ = struct.calcsize(self.__hdr_fmt__)

		## Set the instance attribute
		if buf and len(buf) < self.__hdr_len__:
			raise PacketError("Not enough length")
		elif not buf: buf = ("\x00")*self.__hdr_len__
		self.unpack(buf)
	def __str__(self):
		return self.pack()
	def __repr__(self):
		ret = [attr for attr, _ in self.__hdr_len__]
		ret = ["{0}: {1}".format(_, getattr(self, _)) for _ in ret]
		ret = " | ".join(ret)
		ret = "{0} <{1}>".format(self.__class__.__name, ret)
		return ret
	def __len__(self):
		return self.__hdr_len__ + len(self.payload)
	def pack_hdr(self):
		attr = [getattr(self, attr) for attr, _ in self.__hdr__]
		return struct.pack(self.__hdr_fmt__, *attr)
	def pack(self):
		return self.pack_hdr() + self.payload
	def unpack(self, buf):
		fmt = struct.unpack(self.__hdr_fmt__, buf[:self.__hdr_len__])
		for _ in range(len(fmt)):
			setattr(self, self.__hdr__[_][0], fmt[_])
		if len(buf) > self.__hdr_len__:
			setattr(self, "payload", buf[self.__hdr_len__:])
		else:
			setattr(self, "payload", "")
if __name__ == "__main__":
	import doctest
	doctest.testmod()
