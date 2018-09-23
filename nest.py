# -*- coding: utf-8 -*-

from sys import argv
from multiprocessing import Manager, Process
from urllib.parse import unquote

from os.path import exists as checkFS

from customer import seeds, num_Process, num_threads, pwork, logger, todoPoolf, donePoolf, cachePoolf, failPoolf

from spider import Spider

def dumpPool(dValue, dLock, lock_Timeout = 3.0):

	def write_iter(fname, it, lck, wrtm = "w"):
		if it:
			with open(fname, wrtm) as f:
				if lck.acquire(block=True, timeout = lock_Timeout):
					for tmp in it:
						f.write(tmp.encode("utf-8", "ignore"))
						f.write("\n")
					lck.release()
				else:
					logger.info("Nest: Fail to dump the Pool.")

	logger.info("Nest: dump to-do pool")
	write_iter(todoPoolf, dValue["todoPool"], dLock["todoPool"])
	logger.info("Nest: dump done pool")
	write_iter(donePoolf, dValue["donePool"], dLock["donePool"])
	logger.info("Nest: dump cache pool")
	write_iter(cachePoolf, dValue["cachePool"], dLock["cachePool"])
	logger.info("Nest: dump fail pool")
	write_iter(failPoolf, dValue["failPool"], dLock["failPool"], "a")

def loadPool(fname):

	rs = set()
	with open(fname) as f:
		for line in f:
			tmp = line.strip()
			if tmp:
				tmp = tmp.decode("utf-8", "ignore")
				if tmp not in rs:
					rs.add(tmp)

	return rs

def addPool(dValue, dLock, cmd):

	def add_iter(it, pool, lck):
		if lck.acquire(block=True, timeout = lock_Timeout):
			for tmp in it:
				if not tmp in pool:
					pool.add(tmp)
			lck.release()
		else:
			logger.info("Fail to update the Pool.")

	tmp = cmd.strip().split()
	al = [unquote(tmpu) for tmpu in tmp[1:]]
	key = tmp[0] + Pool
	if key in dValue:
		add_iter(al, dValue[key], dLock[key])
	else:
		logger.info("Illegal pool: " + tmp[0])

def delPool(dValue, dLock, cmd):

	def del_iter(it, pool, lck):
		if lck.acquire(block=True, timeout = lock_Timeout):
			for tmp in it:
				if tmp in pool:
					pool.remove(tmp)
			lck.release()
		else:
			logger.info("Fail to clean the Pool.")

	tmp = cmd.strip().split()
	al = [unquote(tmpu) for tmpu in tmp[1:]]
	key = tmp[0] + "Pool"
	if key in dValue:
		del_iter(al, dValue[key], dLock[key])
	else:
		logger.info("Illegal pool: " + tmp[0])

def mergePool(dValue, dLock, cmd):

	tmp = cmd.strip().split()
	srcPool = tmp[0] + "Pool"
	tgtPool = tmp[-1] + "Pool"
	if (srcPool != tgtPool) and (srcPool in dValue) and (tgtPool in dValue):
		if dLock[srcPool].acquire(block=True, timeout = lock_Timeout) and dLock[tgtPool].acquire(block=True, timeout = lock_Timeout):
			dValue[tgtPool] |= dValue[srcPool]
		else:
			logger.info("Fail to merge the Pool.")
	else:
		logger.info("Illegal command.")

class Nest():

	def __init__(self, dValue, dLock):

		self.dValue = dValue
		self.dLock = dLock
		self.spiders = []
		self.pl = []

	def launch_one(self, inds, dValue, dLock):

		tmp = Spider("p_"+str(inds))
		self.spiders.append(tmp)
		tmp.launch(dValue, dLock, num_threads = 2, t_check = 3.0)

	def launch(self):

		for i in range(num_Process):
			# not sure about whether self should be passed to the call to launch_core or not
			p = Process(target = self.launch_one, args = (i, self.dValue, self.dLock,))
			pl.append(p)
			p.start()

	def stop(self):

		for spider in self.spiders:
			spider.stop()
		for p in self.pl:
			p.join(timeout = 3.0)

	def interact(self):

		running = True
		while running:
			cmd = input().lower()
			if cmd.startswith("stop"):
				self.stop()
			elif cmd.startswith("start"):
				self.launch()
			elif cmd.startswith("dump pools"):
				dumpPool(self.dValue, self.dLock)
			elif cmd.startswith("add pool"):
				addPool(self.dValue, self.dLock, cmd[9:])
			elif cmd.startswith("del pool"):
				delPool(self.dValue, self.dLock, cmd[9:])
			elif cmd.startswith("merge pool"):
				mergePool(self.dValue, self.dLock, cmd[11:])
			elif (cmd == "exit") or (cmd == "q"):
				self.stop()
				dumpPool(self.dValue, self.dLock)

if __name__ == "__main__":
	if len(argv) > 1:
		for seed in argv[1]:
			if not seed in seeds:
				seeds.add(seed)
	if checkFS(todoPoolf):
		seeds |= loadPool(todoPoolf)
	if checkFS(cachePoolf):
		seeds |= loadPool(cachePoolf)
	if checkFS(donePoolf):
		doneP = loadPool(donePoolf)
	else:
		doneP = set()
	if checkFS(failPoolf):
		failP = loadPool(failPoolf)
	else:
		failP = set()
	with Manager() as manager:
		dValue = manager.dict()
		dValue["todoPool"] = seeds
		dValue["donePool"] = doneP
		dValue["cachePool"] = set()
		dValue["failPool"] = failP
		dLock = manager.dict()
		dLock["todoPool"] = manager.Lock()
		dLock["donePool"] = manager.Lock()
		dLock["cachePool"] = manager.Lock()
		dLock["failPool"] = manager.Lock()
		nest = Nest(dValue, dLock)
		nest.launch()
