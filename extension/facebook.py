#! /usr/bin/env python
#! coding: utf-8

class FaceBook(object):
	def __init__(self, id):
		self._id_ = id
	def __str__(self):
		url = "https://graph.facebook.com/{id}"
		return url.format(id=self._id_)
	def profile(self):
		url = "https://graph.facebook.com/{id}/profile"
		return url.format(id=self._id_)
	def photo(self, size="normal"):
		""" Get the user's picture with particular size

			size:
				@str: square / small / normal / large
				@tuple: (width, height)
		"""
		url = "https://graph.facebook.com/{id}/picture?{payload}"
		if isinstance(size, str):
			payload = "type=%s" %size
		else:
			payload = "width=%d&height=%d" %(*size)
		return url.format(id=self._id_, payload=payload)

if __name__ == "__main__":
	raise NotImplementedError

