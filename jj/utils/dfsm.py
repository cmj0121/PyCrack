#! /usr/bin/env python
#! coding: utf-8
__author__    = "cmj"
__copyright__ = "Copyright (C) 2014 cmj"

"""
Decorator-based Python Finite-State Machine (dFSM)

Usage:
	First you need to create your own class which each method handle the logical and
	define the next state by the decorator (implict for ordering) until no decorator
	declared. Default we using __call__ as the start state.

	WLOG, we use the generator as the input value and each function get one value by
	next()	

	There are three decorator for usage:
		1- dFSMStart(fn_name)			Start State for FSM
		2- dFSM((fn_name, rule),...)	Internal node on FSM
		3- dFSMEnd						End node

"""

__all__ = ["dFSMEndError", "dFSMStart", "dFSM", 'dFSMEnd']

class dFSMEndError(Exception):
	def __init__(self, obj):
		self.ret = obj
	def __repr__(self):
		return "<dFSM End> %s"  %self.ret
def dFSMStart(StartStat, match_fn):
	def dFSMStart_wrapper(fn):
		def dFSMStart_inner_wrapper(self, itera):
			ret = []
			while True:
				_fn_ = getattr(self, StartStat)
				try:
					key = next(itera)
					ret += [_fn_(key, itera, match_fn)]
				except dFSMEndError as e:
					ret += [e.ret]
				except StopIteration as e:
					break
			return fn(self, ret)
		return dFSMStart_inner_wrapper
	return dFSMStart_wrapper
def dFSM(*states):
	def dFSM_wrapper(fn):
		def dFSM_inner_wrapper(self, key, itera, match_fn):
			ret = fn(self, key)
			if states:
				key = next(itera)
				for f, m in states:
					_fn_ = getattr(self, f)
					if match_fn(m, key):
						ret = _fn_(key, itera, match_fn)
			return ret
		return dFSM_inner_wrapper
	return dFSM_wrapper
def dFSMEnd(fn):
	def dFSMEnd_wrapper(self, key, itera, match_fn):
		ret = fn(self, key)
		raise dFSMEndError(ret)
	return dFSMEnd_wrapper


import re
class Foo(object):
	"""

	A ->  B -> C -> E
	  \         /
	   -> D ->-
          ||
	      F

	>>> foo = Foo()
	>>> foo((_ for _ in "A B C E".split()))
	A -> B -> C -> E.

	>>> foo((_ for _ in "A B C E A B C E".split()))
	A -> B -> C -> E.
	A -> B -> C -> E.

	>>> foo((_ for _ in "A D F D F D E".split()))
	A -> D -> F -> D -> F -> D -> E.

	"""
	def __init__(self):
		self._state_ = ""

	@dFSMStart("A", re.match)
	def __call__(self, ret):
		print "\n".join(ret)

	@dFSM(("B", "B"), ("D", "D"))
	def A(self, key):
		self._state_ = "A -> "

	@dFSM(("C", "C"))
	def B(self, key):
		self._state_ += "B -> "

	@dFSM(("E", "E"))
	def C(self, key):
		self._state_ += "C -> "

	@dFSM(("E", "E"), ("F", "F"))
	def D(self, key):
		self._state_ += "D -> "

	@dFSMEnd
	def E(self, key):
		self._state_ += "E."
		ret = self._state_[:]
		self._state_ = ""
		return ret

	@dFSM(("D", "D"))
	def F(self, key):
		self._state_ += "F -> "
		
def main():
	import doctest
	doctest.testmod()
if __name__ == "__main__": main()

