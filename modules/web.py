from modules import sdk

class BaseTreeNode(object):
	def __init__(self, name, sep="/"):
		self._p = self	# Parent
		self._n = name	# Name
		self._c = []	# ChildList
		self._s = sep	# Seperator
		self._l = True	# Is leave
	def __str__(self):
		return "%s" %self._n
	def __eq__(self, child):
		if isinstance(child, BaseTreeNode) and child.name == self.name:
			return True
		else:
			return False
	def __getitem__(self, name):
		for c in self._c:
			if c == name:
				return c
		else:
			raise KeyError("%s" %name)
	@property
	def name(self):
		return self._n
	@property
	def getChild(self):
			return self._c
	@property
	def isLeave(self):
		return self._l

	def unionChild(self, child):
		"""
		If two tree have same root, then union two tree
		"""
		if child.name != self.name:
			raise NotImplementedError("BaseTreeNode only union two same root")

		_tmp = []
		for c in child.getChild:
			if c in self.getChild:
				self[c.name].union(c)
			else:
				_tmp += [c]
		self._c += _tmp
	def setChild(self, child):
		if isinstance(child, str):
			child = child.split(self._s)

			cur = self
			for c in child:
				cur = cur.setChild(BaseTreeNode(c))
		elif hasattr(child, "getChild") and hasattr(child, "name"):
			for c in self.getChild:
				if c.name == child:
					self.union(child)
			else:
				self._c += [child]
		else:
			raise NotImplementedError("setChild not support: [{0}] {1}".format(type(child), child))

def getBasic404(URL, port=80, seedLen=10):
	import random
	import string

	_seed = [random.choice(string.letters+string.digits) for n in xrange(seedLen)]

	return sdk.wrapGetWebPage("%s/%s" %(URL, "".join(_seed)))
