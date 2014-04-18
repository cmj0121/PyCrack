#! /usr/bin/env python
#! coding: utf-8

try:
	from setuptools import setup, find_packages
except ImportError:
	print "Cannot import setuptools, try distutils.core"
	from distutils.core import setup
	def find_packages(): return ["jj"]

from jj.utils import DEFAULT_CONF as _C

setup(	name		= "jj",
		version		= _C["VERSION"],
		author		= _C["AUTHOR"],
		author_email= _C["AUTHOR_EMAIL"],
		description	= _C["DESCRIPTION"],
		packages	= find_packages(),
		data_files	= [('/usr/bin', _C["BINARY"])])
