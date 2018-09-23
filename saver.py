# -*- coding: utf-8 -*-

from customer import URL2File

from os.path import exists as checkFS
from os import makedirs as mkdir

def prepare_path(path):
	if not checkFS(path):
		mkdir(path, 0o666)

def saveURL(url, data, encode_method = None, ignore_werr = True):
	path, fwrt = URL2File(url)
	prepare_path(path)
	with open(fwrt, "wb") as f:
		if encode_method is None:
			f.write(data)
		else:
			f.write(data.encode(encode_method, ignore = ignore_werr))
