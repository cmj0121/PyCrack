#! /usr/bin/env python
#! coding: utf-8

import jpython
from utils import *
from info import INFO
from cve import CVE

__all__ = ["dispatch", "jpython", "CVE", "INFO"]
dispatch = Dispatch()
dispatch.addArgument("jpython", jpython.interact,
	help="Customize Python interpreter")
dispatch.addArgument("doctest", dispatch.test,
	help="Run self-test")
dispatch.addArgument("info", info.INFO(),
	help="Information for target")
dispatch.addArgument("cve", cve.CVE(),
	help="CVE List search")
