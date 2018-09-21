# -*- coding: utf-8 -*-

import threading

from customer import logger, extract_Page

from retriever import getURL
from saver import saveURL
from extractor import URLExtractor

class Spider():

	def __init__(self, name):
		self.prompt = name + ": "
		self.working = False

	def launch(self, dValue, dLock, num_threads = 2, t_check = 3.0):

		self.working = True
		while self.working:
			if len(threading.enumerate()) < num_threads:
				# not sure about whether self should be passed to the call to t_core or not
				tmp = threading.Thread(target = t_core, args = (self, dValue, dLock,))
				tmp.start()
		for tmp in threading.enumerate():
			tmp.join(3.0)

	def stop(self):
		self.working = False

	def t_core(self, dValue, dLock, lock_Timeout = 3.0):

		url_ext = URLExtractor()
		while self.working:

			if dLock["todoPool"].acquire(block=True, timeout = lock_Timeout):
				url = None
				if len(dValue["todoPool"]) > 0:
					url = dValue["todoPool"].pop()
				dLock["todoPool"].release()
				if url is not None:
					if dLock["cachePool"].acquire(block=True, timeout = lock_Timeout):
						dValue.["cachePool"].add(url)
						dLock["cachePool"].release()
					else:
						logger.info(self.prompt + "Fail to add %s to cache Pool." % (url))
					if dLock["failPool"].acquire(block=True, timeout = lock_Timeout):
						dValue.["failPool"].add(url)
						dLock["failPool"].release()
					else:
						logger.info(self.prompt + "Fail to add %s to fail Pool." % (url))
					processURL(url, dValue, dLock, url_ext, lock_Timeout)

			else:
				logger.info(self.prompt + "Fail to get the lock of to-do Pool.")

	def processURL(url, dValue, dLock, exter, lck_timeout = 3.0):

		data, proto_prefix, host, real_url, http_code, infos, is_Decoded, encode_method, confidence = getURL(url)
		if data is not None:
			real_url = real_url
			if real_url != url:
				logger.info("%s%s was redirected to %s" % (self.prompt, url, real_url,))

			success_ext = True
			if extract_Page(url, host, real_url, proto_prefix, data, is_Decoded):
				urls = exter.extract(data, proto_prefix, host)
				if urls:
					todo = []
					if dLock["donePool"].acquire(block=True, timeout = lck_timeout):
						for url in urls:
							if not url in dValue["donePool"]:
								todo.append(url)
						dLock["donePool"].release()
						if todo:
							if dLock["todoPool"].acquire(block=True, timeout = lck_timeout):
								for url in urls:
									if not url in dValue["todoPool"]:
										dValue["todoPool"].add(url)
								dLock["todoPool"].release()
							else:
								logger.info(self.prompt + "Fail to get the lock of to-do Pool.")
								success_ext = False
					else:
						logger.info(self.prompt + "Fail to get the lock of done Pool.")
						success_ext = False

			saveURL(real_url, data, "utf-8")
			if success_ext:
				if dLock["donePool"].acquire(block=True, timeout = lck_timeout):
					dValue["donePool"].add(real_url)
					dLock["donePool"].release()
					if dLock["cachePool"].acquire(block=True, timeout = lock_Timeout):
						if url in dValue.["cachePool"]:
							dValue.["cachePool"].remove(url)
						dLock["cachePool"].release()
						if dLock["failPool"].acquire(block=True, timeout = lock_Timeout):
							if url in dValue.["failPool"]:
								dValue.["failPool"].remove(url)
							dLock["failPool"].release()
						else:
							logger.info(self.prompt + "Fail to remove %s from fail Pool." % (url))
					else:
						logger.info(self.prompt + "Fail to remove %s from cache Pool." % (url))
				else:
					logger.info(self.prompt + "Fail to get the lock of done Pool.")
