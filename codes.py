# -*- coding: utf-8 -*-

from chardet import detect

def getEnc(bytes_in):
	rs = detect(bytes_in)
	return rs["encoding"], rs["confidence"]

def decBytes(bytes_in, pdec = 0.8, ignore_err = True):
	encm, p = getEnc(bytes_in)
	if p >= pdec:
		return bytes_in.decode(encm, ignore = ignore_err), True, encm, p
	else
		return bytes_in, False, encm, p
