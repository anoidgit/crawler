# -*- coding: utf-8 -*-

from html.parser import HTMLParser

from custom_filter import legal_Tag, is_OmmitedURL, legal_URL

class URLParser(HTMLParser):

	def __init__(self):
		super(URLExtractor, self).__init__()
		self.urls = set()

	def handle_starttag(self, tag, attrs):
		if legal_Tag(tag):
			for key, value in attrs:
				if (key == "href") and value not in self.urls:
					self.urls.add(value)

	def clear_urls(self):
		self.urls.clear()

class URLExtractor():

	def __init__(self):
		self.extractor = URLParser()

	def extract(self, data, proto_prefix, host):

		self.extractor.clear_urls()
		prefixes = proto_prefix + host

		rs = []

		self.extractor.feed(data)
		for url in self.extractor.urls:
			if is_OmmitedURL(url):
				url = prefixes + url
			if legal_URL(url, proto_prefix, host):
				rs.append(url)
