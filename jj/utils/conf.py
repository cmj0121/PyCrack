#! /usr/bin/env python
#! coding: utf-8

import time
import sys

DEFAULT_CONF = {}
## THEME
DEFAULT_CONF["THEME_NORMAL"]	= "\033[0m"
DEFAULT_CONF["THEME_BLACK"]		= "\033[30m"
DEFAULT_CONF["THEME_RED"]		= "\033[31m"
DEFAULT_CONF["THEME_GREEM"]		= "\033[32m"
DEFAULT_CONF["THEME_YELLOW"]	= "\033[33m"
DEFAULT_CONF["THEME_BLUE"]		= "\033[34m"
DEFAULT_CONF["THEME_PURPLE"]	= "\033[35m"
DEFAULT_CONF["THEME_CYAN"]		= "\033[36m"
DEFAULT_CONF["THEME_GREY"]		= "\033[37m"
DEFAULT_CONF["THEME_BOLD"]		= "\033[1m"
DEFAULT_CONF["THEME_ULINE"]		= "\033[4m"
DEFAULT_CONF["THEME_BLANK"]		= "\033[5m"
DEFAULT_CONF["THEME_INVERT"]	= "\033[7m"

## Global Setting
DEFAULT_CONF["VERSION"]			= "0.1"
DEFAULT_CONF["PROG_NAME"]		= "jj"
DEFAULT_CONF["AUTHOR"]			= "cmj"
DEFAULT_CONF["AUTHOR_EMAIL"]	= "cmj@cmj.tw"
DEFAULT_CONF["DESCRIPTION"]		= "Easy python command"
DEFAULT_CONF["SOURCE_FOLDER"]	= ["jj"]
DEFAULT_CONF["BINARY"]			= ["bin/jj", "bin/jpython"]
DEFAULT_CONF["NOW"]				= time.gmtime()
DEFAULT_CONF["BANNER"]			= "{THEME_YELLOW}"\
	"{AUTHOR}'s Python ({0}.{1}.{2}) interpreter v{VERSION}.\n" \
	"All Copyight (C) reserved 2014-{NOW.tm_year}" \
	"{THEME_NORMAL}".format(sys.version_info.major, sys.version_info.minor, sys.version_info.micro, **DEFAULT_CONF)
DEFAULT_CONF["PS1"]				= "\001{THEME_CYAN}{THEME_BOLD}\002>>> \001{THEME_NORMAL}\002".format(**DEFAULT_CONF)
DEFAULT_CONF["PS2"]				= "\001{THEME_YELLOW}\002... \001{THEME_NORMAL}\002".format(**DEFAULT_CONF)
DEFAULT_CONF["CURRENT_CMD"]	= [DEFAULT_CONF["PROG_NAME"]]

## Global Parameter
DEFAULT_CONF["DEPTH"]		= 1			## -d, --depth=
DEFAULT_CONF["DEBUG"]		= False		## -D, --debug
DEFAULT_CONF["FILE"]		= ""		## -f, --file=
DEFAULT_CONF["OUT_FILE"]	= ""		## -o, --output=
DEFAULT_CONF["JOBS"]		= 1			## -j, --jobs=
DEFAULT_CONF["QUITE"]		= False		## -q, --quite
DEFAULT_CONF["VERBOUS"]		= 0			## -v, -vv, -vvv
DEFAULT_CONF["PRETTY"]		= "pretty"	## --pretty=
DEFAULT_CONF["BUFSIZ"]		= 8196		## --bufsiz=
DEFAULT_CONF["PORT"]		= 80		## -p, --port=80
DEFAULT_CONF["ENCODE"]		= "utf-8"	## --encode=
DEFAULT_CONF["FORCE"]		= False		## --force

## CMS detection
DEFAULT_CONF["CMS_FILTER"]	= [
	r"<meta\s+name=[\"']generator[\"']\s+content=[\"'](.*?)['\"].*?/?>",## General contain for metadata
	r"<script.*?src=[\"'].*?(jquery.*?.js)['\"].*?>",					## Using JS script
	r"Powered by (.*?) ",												## Powered by
	r"['\"]([^\"']*\.css)[\"']",										## CSS style
	]
DEFAULT_CONF["CMS_TOKEN"]	= [
	r"Discuz!\s?\S?[0-9.]+",			## Discuz
	r"jquery(?:-?(?:\d*.)*\d*)?.js",	## jQuery
	r"No-CMS",							## NO-CMS
	r"CMSimple",						## CMSimple
	]

