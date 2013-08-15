"""
Web Site

domain : {
		Get: {key:value}
		Posg: {key:value}
		child :[...]
	}
"""
import re
import requests

def PrettyPrint(ret):
	for n in ret:
		print n
		print "Get: %s" %(ret[n]['Get'])
		print "Post: %s" %(ret[n]['Post'])

		
def scanToken(url, token):
	req = requests.get(url)
	return re.findall(token, req.text)
def scanURL(url):
	token = [r"href=['\"](.*?)['\"]", r"a=['\"](.*?)['\"]"]
	token += [r"src=['\"](.*?)['\"]", r"action=['\"](.*?)['\"]"]
	ret = []
	for _ in token:
		ret += scanToken(url, _)
	return ret
