# -*- coding: utf-8 -*-
# This defined all the functions and modules that each module has access to.

from dCore import *
import os

def DamnLoadModuleFile(f):
	f = DamnUnicode(f)
	import dCore, dConstants, dLocale, dTubes, dThread, dSpawn, dLoader, dModules
	globalModules = [dCore, dConstants, dLocale, dTubes, dThread, dSpawn, dLoader, dModules] # Modules in global namespace
	import os, sys, time, traceback, re, urllib, urllib2, BeautifulSoup, xmlrpclib, hashlib, unicodedata, random, signal, base64, gdata.youtube.service
	env = globals()
	locs = locals()
	for l in locs.iterkeys():
		env[l] = locs[l]
	for m in globalModules:
		for v in dir(m):
			env[v] = m.__dict__[v]
	print '----'
	print env.keys()
	print '------'
	DamnExecFile(f, globs=env, locs=env)

def DamnLoadModule(module):
	module = DamnUnicode(module)
	for i in os.listdir(module):
		i = DamnUnicode(i)
		if not os.path.isdir(module + DV.sep + i) and i[-8:] == u'.damnvid':
			DamnLoadModuleFile(module + DV.sep + i)
