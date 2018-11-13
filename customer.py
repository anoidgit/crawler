# -*- coding: utf-8 -*-

from os import sep as path_sep
from urllib.parse import unquote

taskid = "debug"

seeds = set([])

todoPoolf = "todo.pool"
donePoolf = "done.pool"
cachePoolf = "cache.pool"
failPoolf = "fail.pool"

num_Process = 2
num_threads = 4

server_address = "tcp://*:5556"

pwork = "storage" + path_sep + taskid + path_sep

from multiprocessing import log_to_stderr as get_logger
import logging
logger = get_logger()
logger.setLevel(logging.INFO)

def URL2File(url):

	# following lines of code ignored protocol in file names,
	# if you need this information, this line of code could work instead of them:
	# url = url.replace("//", "/")

	ind = url.find("://") + 3
	# if http, https and ftp are the only options,
	# there should be larger than 2,
	# using 2 here for stronger code.
	if ind > 2:
		url = url[ind:]

	ind = url.rfind("/") + 1
	url = url.replace("/", path_sep)
	path = pwork + url[:ind]
	fwrt = pwork + url
	return path, fwrt + ".crawl"

def is_WebPage(url, real_url = None):

	true_filter = [".html", ".htm", ".php", ".asp"]
	false_filter = [".jpg", ".png", ".ico", ".gz", ".xz", ".bzip2", ".zip", ".rar", ".7z", ".pdf", ".doc", ".docx", ".ppt", ".pptx", ".xls", ".xlsx", ".swf", ".mp3", ".mp4", ".mkv"]

	rs = True
	if real_url is None:
		real_url = url
	real_url = real_url.lower()

	for filter in true_filter:
		if real_url.endswith(filter):
			return True

	for filter in false_filter:
		if real_url.endswith(filter):
			rs = False
			break

	return rs

def legal_Tag(tag):

	if tag == "a":
		return True
	#uncomment following two lines to allow grabing link tag
	#elif tag == "link":
		#return True
	else:
		return False

def is_OmmitedURL(url):
	if url.startswith("/"):
		if len(url) > 1:
			if url[1] != '/':
				return True
			else:
				return False
		return True
	else:
		return False

# To limit the range of websites downloaded by re-implementing this function
# Every URL will be retrieved in current setting
def legal_URL(url, proto_prefix, host):
	return True

# To limit the range of websites belong which the urls will be extracted
# URLs in decoded webpages will be extracted in current setting
def extract_Page(url, host, real_url, proto_prefix, data, decoded):

	if is_WebPage(real_url) and decoded:
		return True

def unquote_set(setin):
	rs = set()
	for u in setin:
		rs.add(unquote(u))
	return rs

seeds = unquote_set(seeds)

todoPoolf = pwork + todoPoolf
donePoolf = pwork + donePoolf
cachePoolf = pwork + cachePoolf
failPoolf = pwork + failPoolf
