#! /usr/bin/env python
#! coding: utf-8

from collections import namedtuple

PIPE = "/tmp/muq_pipe"
THRESHOLD = 100
QUEUE = []

DB = namedtuple('DB', ['usr', 'pwd', 'db', 'table'])

def main(usr, pwd, db, table):
	import os
	import socket

	if os.path.exists(PIPE): os.unlink(PIPE)
	_db_ = DB(usr, pwd, db, table)

	sk = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
	sk.bind(PIPE)

	try:
		loop(sk, _db_)
	except KeyboardInterrupt as e:
		store(_db_)
		exit(0)
def loop(sk, db):
	global QUEUE

	while True:
		msg, cli = sk.recvfrom(4096)
		if 0 == len(msg): break
		else: QUEUE += [msg]

		if THRESHOLD < len(QUEUE):
			store(db)
def store(db, sep="&&", term="\n"):
	import random
	import string
	import tempfile

	global QUEUE

	_ = "".join(["".join(_) for _ in QUEUE ])
	while True:
		if sep not in _: break
		sep = "".join([random.choice(string.letters) for n in range(6)])
	while True:
		if term not in _: break
		term = "".join([random.choice(string.letters) for n in range(6)])

	save = term.join([sep.join(_) for _ in QUEUE])

	with tempfile.NamedTemporaryFile() as f:
	shell = r"LOAD DATA LOCAL INFILE '%s' REPLACE into TABLE {table}"\
			r"character set utf8 " \
			r"fields terminated by '{sep}' lines terminated by '{term}'"
	shell = shell.format(table=db.table, sep=sep, term=term)
	cmd = 'mysql -h ds -u {usr} -D {db} --password={pwd} -e "{cmd}"'
	cmd = cmd.format(usr=db.usr, pwd=db.pwd, db=db.db, cmd=shell)
	st, ret = commands.getstatusoutput(cmd)
	if st:
		print "Save DB failed %s" %st
		exit(1)
	
if __name__ == "__main__":
	main()
