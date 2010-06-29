# -*- coding: utf-8 -*-
from dCore import *
from dLog import DamnlogException
import sys
try:
	import threading as thr
except:
	import dummy_threading as thr
class DamnThread(thr.Thread):
	def __init__(self, autostart=False):
		thr.Thread.__init__(self)
		self.done = False
		if autostart:
			self.start()
	def start(self):
		thr.Thread.start(self)
		return self # Allows chaining
	def run(self):
		self.done = False
		try:
			self.go()
		except:
			DamnlogException(*(sys.exc_info()))
		self.done = True
	def go(self):
		pass
	def join(self, timeout=None):
		if self.isDone():
			return None
		if timeout is None:
			return thr.Thread.join(self)
		return thr.Thread.join(self, timeout)
	def isDone(self):
		return self.done
def DamnTimerException(func):
	try:
		func()
	except:
		DamnlogException(*(sys.exc_info()))
def DamnTimer(timer, func):
	return thr.Timer(timer, DamnCurry(DamnTimerException, func))
class DamnThreadedFunctionNotDoneException(Exception):
	pass
class DamnThreadedFunction(DamnThread):
	def __init__(self, func, autostart=False):
		self.func = func
		self.result = None
		self.exception = None
		DamnThread.__init__(self, autostart=autostart)
	def getResult(self):
		if self.isDone():
			if self.exception is not None:
				raise self.exception
			return self.result
		raise DamnThreadedFunctionNotDoneException()
	def go(self):
		try:
			self.result = self.func()
		except Exception, e:
			self.exception = e
