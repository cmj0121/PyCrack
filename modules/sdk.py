class WebReq(object):
	"""
		[Int]		Status code
		[Dict]		Cookies
		[Dict]		HTTP Header
		[String]	Web Page
	"""
	def __init__(self, request, code, content, cookies={}, headers={}):
		self.request = request
		self.code    = code
		self.content = content
		self.cookies = cookies
		self.headers = headers
	def __str__(self):
		return """Request [%s]
    Status code: %.10s
    Cookie: %.40s
    Header: %.40s
    Content: %.40s
""" %(self.request, self.code, self.cookies, self.headers, self.content)
def wrapGetWebPage(url, port=80):
	"""
	Get the web page by wrap function.

	@PARAM:
		url			Target website url
		[port]		Default: 80

	@RETURN:
		[WebReq]	Wrapped request object
	"""
	import requests

	if not url.startswith("http://"): url = "http://%s" %url

	req = requests.get(url)
	return WebReq(url, req.status_code, req.content, req.cookies, req.headers)
