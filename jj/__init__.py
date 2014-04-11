#! /usr/bin/env python
#! coding: utf-8

import jpython, info

__all__ = ["dispatch", "jpython"]
dispatch = utils.Dispatch()
dispatch.addArgument("jpython", jpython.interact,
	help="Customize Python interpreter")
dispatch.addArgument("doctest", dispatch.test,
	help="Run self-test")
dispatch.addArgument("info", info.INFO(),
	help="Information for target")
