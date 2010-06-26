# -*- coding: utf-8 -*-
from dCore import *
from dLog import DamnlogException
import sys
try:
	import threading as thr
except:
	import dummy_threading as thr
class DamnThread(thr.Thread):
	def run(self):
		try:
			self.go()
		except:
			DamnlogException(*(sys.exc_info()))
	def go(self):
		pass
def DamnTimerException(func):
	try:
		func()
	except:
		DamnlogException(*(sys.exc_info()))
def DamnTimer(timer, func):
	return thr.Timer(timer, DamnCurry(DamnTimerException, func))
