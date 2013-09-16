#! /usr/bin/env python
#! coding: utf-8

class TODO_LIST(object):
	def __init__(self, db="todo.db"):
		self._db_ = db
		self._job_ = self.db
	def __del__(self):
		if hasattr(self, "_job_") and self._job_:
			self.db = self._job_
	def __str__(self):
		return self.job
	def __repr__(self):
		return self.job
	def __getitem__(self, index):
		return self._job_[index]
	def __setitem__(self, key, value):
		self._job_[index] = value
	def __delitem__(self, index):
		del self._job_[index]

	## Data operations
	def _load_(self):
		import yaml

		try:
			with open(self._db_) as f:
				db = f.read()
			return yaml.load(db)
		except IOError, e:
			if 2 == e.errno:
				return None
			else:
				raise IOError(e)
	def _save_(self, data):
		import yaml

		db = yaml.dump(data)
		with open(self._db_, "w") as f:
			f.write(db)
	db = property(_load_, _save_, None)

	def _listJob_(self):
		if not hasattr(self, "_job_") or not self._job_:
			return "Idleing..."

		return "\n".join(["%2d- %s" %(n+1, self._job_[n]) for n in range(len(self._job_))])
	def _addJob_(self, job):
		import time
		if not hasattr(self, "_job_") or not self._job_:
			self._job_ = []

		self._job_ += ["[%s] %s" %(time.strftime("%m/%d %H:%M"), job)]
	job = property(_listJob_, _addJob_, None)

if __name__ == "__main__":
	List = TODO_LIST()
