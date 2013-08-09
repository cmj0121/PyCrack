#! /usr/bin/env python
#! coding: utf-8

import time
import urllib2
import requests
import os

def _manhuaa(comic, lv , nr):
	orig = "http://www.manhuaa.com/comic/{comic}/{nr}.html?page={lv}"
	url = "http://imgs.manhuazhu.com/imgs/DM/F/fqczrj/{lv}/{nr}.jpg"
	tmp = url.format(lv=str(lv).zfill(3), nr=str(nr).zfill(3))
	try:
		req = urllib2.urlopen(orig.format(comic=comic, lv=496332 + lv, nr=nr)).read()
		req = urllib2.urlopen(tmp).read()
		print "%s/%s.jpg" %(str(lv), str(nr).zfill(3))
	except Exception, e:
		req = None
	return req
def manhuaa():
	""" Ref: http://www.manhuaa.com/comic/496328/ """
	orig = "http://www.manhuaa.com/comic/496328/{nr}.html?page={lv}"
	url = "http://imgs.manhuazhu.com/imgs/DM/F/fqczrj/{lv}/{nr}.jpg"

	for lv in xrange(45, 47):
		try:
			os.mkdir(str(lv))
		except:
			pass
		for nr in range(1, 200):
			tmp = url.format(lv=str(lv).zfill(3), nr=str(nr).zfill(3))
			try:
				req = urllib2.urlopen(orig.format(lv=496332 + lv, nr=nr))
				req = urllib2.urlopen(tmp).read()
				open( "%s/%s.jpg" %(str(lv), str(nr).zfill(3)), "w").write(req)
				print "%s/%s.jpg" %(str(lv), str(nr).zfill(3))
			except Exception, e:
				break

def re_manhuaa(path):
	done = True
	while done:
		done = False
		## Count nr of incurrect image
		cnt = 0
		base = "/mnt/photo/漫畫/夫妻成長日記/%s"
		for p in path:
			for img in [n for n in os.listdir(base %p) if n.endswith('.jpg')]:
				with open("/mnt/photo/漫畫/夫妻成長日記/%s/%s" %(p, img)) as f:
					ret = f.read()
				if 47177 == len(ret): cnt += 1
		print "Need to re-get %s the image" %cnt

		for p in path:
			for img in [n for n in os.listdir( base %p) if n.endswith('.jpg')]:
				with open("/mnt/photo/漫畫/夫妻成長日記/%s/%s" %(p, img))as f:
					ret = f.read()
				if 47177 != len(ret): continue

				ret = _manhuaa(496328, int(p), int(img.split('.')[0]))
				if not ret or 47177 == len(ret):
					print "Still cannot get currect image"
					done = True
				else:
					with open("/mnt/photo/漫畫/夫妻成長日記/%s/%s" %(p, img), "w") as f:
						f.write(ret)
		print "Wait 10 seconds"	
		time.sleep(10)

if __name__ == "__main__":
	re_manhuaa(range(45, 47))
