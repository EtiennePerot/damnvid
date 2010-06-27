# -*- coding: utf-8 -*-
from dCore import *
from dLog import DamnlogException
import sys
try:
	import threading as thr
except:
	import dummy_threading as thr
class DamnThread(thr.Thread):
	def __init__(self):
		thr.Thread.__init__(self)
		self.isDone = False
	def start(self):
		thr.Thread.start(self)
		return self # Allows chaining
	def run(self):
		self.isDone = False
		try:
			self.go()
		except:
			DamnlogException(*(sys.exc_info()))
		self.isDone = True
	def go(self):
		pass
	def join(self):
		if self.isDone:
			return None
		return thr.Thread.join(self)
def DamnTimerException(func):
	try:
		func()
	except:
		DamnlogException(*(sys.exc_info()))
def DamnTimer(timer, func):
	return thr.Timer(timer, DamnCurry(DamnTimerException, func))
class DamnThreadedFunction(DamnThread):
	def __init__(self, func):
		self.func = func
		DamnThread.__init__(self)
	def go(self):
		return self.func()
