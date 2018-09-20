# -*- coding: utf-8 -*-

from urllib.request import Request, urlopen

from gzip import decompress as ungzip

from custom_filter import is_WebPage

from coder import decBytes

def getHost(url):

	proto_prefix = ""
	ind = url.find("://") + 3
	# if http, https and ftp are the only options,
	# there should be larger than 2,
	# using 2 here for stronger code.
	if ind > 2:
		proto_prefix = url[:ind]
		url = url[ind:]
	ind = url.find("/")
	if ind >= 0:
		url = url[:ind]
	ind = url.find(":")
	if ind >= 0:
		url = url[:ind]

	return url, proto_prefix

def getHeaders(url):

	host, proto_prefix = getHost(url)
	return {"Host": host, \
		"Connection": "keep-alive", \
		"Upgrade-Insecure-Requests": 1, \
		"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.81 Safari/537.36", \
		"DNT": 1, \
		"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8", \
		"Accept-Encoding": "gzip, deflate, br" \
		"Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"}, proto_prefix, host

def getData(url, timeout = 3, retry = 1):
	heads, proto_prefix, host = getHeaders(url)
	req = Request(url, headers = heads)
	real_url = url
	infos = None
	http_code = 600
	data = None
	for i in xrange(retry):
		with urlopen(req, timeout = timeout) as f:
			real_url = f.geturl()
			infos = f.info()
			http_code = f.getcode()
			data = f.read()
			if infos.get("Content-Encoding", "deflate") == "gzip":
				data = ungzip(data)
			# http_code is assumed to be an integer
			# redirection is not implemented for http_code between 300 and 400
			if (data is not None) and (http_code < 400):
				break

	return data, proto_prefix, host, real_url, http_code, infos

def getURL(url):

	data, proto_prefix, host, real_url, http_code, infos = getData(url)

	is_Decoded = False
	encode_method = None
	confidence = 0.0

	if is_WebPage(url, real_url):
		data, is_Decoded, encode_method, confidence = decBytes(data)

	return data, proto_prefix, host, real_url, http_code, infos, is_Decoded, encode_method, confidence
