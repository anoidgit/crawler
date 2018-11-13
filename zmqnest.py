# -*- coding: utf-8 -*-

from sys import argv
from multiprocessing import Lock, Process
from urllib.parse import unquote

import zmq

from time import sleep

from os.path import exists as checkFS

from customer import seeds, num_Process, num_threads, pwork, logger, todoPoolf, donePoolf, cachePoolf, failPoolf, server_address

from spider import Spider

def dumpPool(dValue, dLock, lock_Timeout = 3.0):

	def write_iter(fname, it, lck, wrtm = "w"):
		if it:
			with open(fname, wrtm) as f:
				if lck.acquire(timeout = lock_Timeout):
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
		if lck.acquire(timeout = lock_Timeout):
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
		if lck.acquire(timeout = lock_Timeout):
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
		if dLock[srcPool].acquire(timeout = lock_Timeout) and dLock[tgtPool].acquire(timeout = lock_Timeout):
			dValue[tgtPool] |= dValue[srcPool]
		else:
			logger.info("Fail to merge the Pool.")
	else:
		logger.info("Illegal command.")

class Nest():

	def __init__(self, dValue, dLock, saddr):

		self.dValue = dValue
		self.dLock = dLock
		self.spiders = []
		self.pl = []
		self.addr = saddr

	def launch_one(self, inds):

		tmp = Spider("p_"+str(inds))
		self.spiders.append(tmp)
		tmp.launch(num_threads = num_threads + 1, t_check = 3.0)

	def launch_server(self):
		context = zmq.Context()
		socket = context.socket(zmq.PUB)
		socket.bind(self.addr)
		while self.run:
			try:
				req = socket.recv_json()
			except Exception as e:
				logger.info(e)
			socket.send_json(self.handle(req))
		socket.close()

	def launch(self):
		self.run = True
		p = Process(target = self.launch_one)
		p.start()
		self.pl.append(p)
		for i in range(num_Process):
			p = Process(target = self.launch_one, args = (i,))
			self.pl.append(p)
			p.start()
			sleep(3.0)
		for p in self.pl:
			p.join()

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
		for seed in argv[1:]:
			ind = seed.find("://")
			if ind < 0:
				seed = "http://" + seed
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
	dValue = {}
	dValue["todoPool"] = seeds
	dValue["donePool"] = doneP
	dValue["cachePool"] = set()
	dValue["failPool"] = failP
	dLock = {}
	dLock["todoPool"] = Lock()
	dLock["donePool"] = Lock()
	dLock["cachePool"] = Lock()
	dLock["failPool"] = Lock()
	nest = Nest(dValue, dLock, server_address)
	nest.launch()
