# -*- coding: utf-8 -*-
from dCore import *
from dLog import *
import sys
try:
	import threading as thr
except:
	import dummy_threading as thr
class DamnThread(thr.Thread):
	counter = {}
	def __init__(self, autostart=False, name=None, log=True):
		thr.Thread.__init__(self)
		if name is None:
			classname = DamnUnicode(self.__class__.__name__)
		else:
			classname = DamnUnicode(name)
		if not DamnThread.counter.has_key(classname):
			DamnThread.counter[classname] = 0
		self.name = u'thr.' + classname + u'-' + DamnUnicode(DamnThread.counter[classname])
		self.canLog = log
		self.log('initializing. Autostart?', autostart)
		DamnThread.counter[classname] += 1
		self.done = False
		if autostart:
			self.start()
	def log(self, *args, **kwargs):
		if self.canLog:
			Damnlog(self, *args, **kwargs)
	def start(self):
		thr.Thread.start(self)
		return self # Allows chaining
	def run(self):
		try:
			self.done = False
			self.log('running.')
			self.go()
			self.log('finished,')
			self.done = True
		except:
			self.done = False
			DamnlogException(*(sys.exc_info()))
	def go(self): # To be overridden by subclasses
		pass
	def join(self, timeout=None):
		if self.isDone():
			self.log('joining with timeout', timeout, 'instantly because it is done already.')
			return None
		if timeout is None:
			self.log('joining with no timeout.')
			return thr.Thread.join(self)
		self.log('joining with timeout', timeout)
		result = thr.Thread.join(self, timeout)
		if self.isDone():
			self.log('successfully joined within timeout', timeout)
		else:
			self.log('couldn\'t join within timeout', timeout)
		return result
	def isDone(self):
		return self.done
	def __str__(self):
		return u'<' + self.name + u'>'
	def __repr__(self):
		return self.__str__()
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
	def __init__(self, func, autostart=False, log=True):
		self.func = func
		self.result = None
		self.exception = None
		DamnThread.__init__(self, autostart=autostart, name=u'func(' + DamnUnicode(self.func) + u')', log=log)
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
