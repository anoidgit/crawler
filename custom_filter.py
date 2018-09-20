# -*- coding: utf-8 -*-

def is_WebPage(url, real_url):

	false_fil = [".jpg", ".png", ".ico", ".gz", ".xz", ".bzip2", ".zip", ".rar", ".7z", ".pdf", ".doc", ".docx", ".ppt", ".pptx", ".xls", ".xlsx", ".swf", ".mp3", ".mp4", ".mkv"]

	rs = True
	real_url = real_url.lower()

	for filter in false_fil:
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

	if url.startswith("/") and (url[1] != '/'):
		return True
	else:
		return False

# To limit the range of websites downloaded by re-implementing this function
# Every URL will be retrieved in current setting
def legal_URL(url, proto_prefix, host):

	return True
