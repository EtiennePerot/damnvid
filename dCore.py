# -*- coding: utf-8 -*-

def DamnUnicode(s):
	if type(s) is type(u''):
		return s
	if type(s) is type(''):
		try:
			return unicode(s)
		except:
			try:
				return unicode(s.decode('utf8'))
			except:
				try:
					return unicode(s.decode('windows-1252')) # Windows file paths with accents and weird characters
				except:
					return unicode(s, errors='ignore')
	try:
		return unicode(s)
	except:
		return s
def DamnOpenFile(f, m):
	f = DamnUnicode(f)
	try:
		return open(f, m)
	except:
		try:
			return open(f.encode('utf8'), m)
		except:
			try:
				return open(f.encode('windows-1252'), m)
			except:
				return open(f.encode('utf8', 'ignore'), m)
def DamnExecFile(f, globs={}, locs={}, addDV=True):
	if addDV:
		globs['DV'] = DV
		locs['DV'] = DV
	try:
		execfile(DamnUnicode(f), globs, locs)
	except:
		try:
			execfile(DamnUnicode(f).encode('utf8'), globs, locs)
		except:
			try:
				execfile(DamnUnicode(f).encode('windows-1252'), globs, locs)
			except:
				try:
					from dLog import Damnlog, DamnlogException
					import sys
					DamnlogException(*(sys.exc_info()))
					Damnlog('Could not execute file', f)
				except:
					pass
def DamnVersionCompare(v1, v2): # Returns 1 if v1 is newer, 0 if equal, -1 if v2 is newer.
	v1 = DamnUnicode(v1).split(u'.')
	v2 = DamnUnicode(v2).split(u'.')
	for i in range(len(v1)):
		if len(v2) <= i:
			return 1
		if v1[i] != v2[i]:
			return 2 * int(v1[i] > v2[i]) - 1
	if len(v1) != len(v2):
		return 2 * (len(v1) > len(v2)) - 1
	return 0
class DamnCurry:
	# From http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/52549
	def __init__(self, func, *args, **kwargs):
		self.func = func
		self.pending = args[:]
		self.kwargs = kwargs
	def __call__(self, *args, **kwargs):
		if kwargs and self.kwargs:
			kw = self.kwargs.copy()
			kw.update(kwargs)
		else:
			kw = kwargs or self.kwargs
		return self.func(*(self.pending + args), **kw)
def DamnTempFile():
	name = DV.tmp_path + DamnUnicode(random.random()) + '.tmp'
	while os.path.exists(name):
		name = DV.tmp_path + DamnUnicode(random.random()) + '.tmp'
	Damnlog('Temp file requested. Return:', name)
	return name
def DamnNothing(*args, **kwargs):
	return
class DamnEmpty:
	pass
DV = DamnEmpty()
def DamnOverridePath(prefix, otherwise=None):
	global DV
	prefix = DamnUnicode(prefix).lower()
	for i in DV.argv:
		if i[:len(prefix)].lower() == prefix:
			result = i[len(prefix):]
			if result[-1:] != DV.sep:
				result += DV.sep
			DV.argv = [x for x in DV.argv if x[:len(prefix)].lower() != prefix]
			return result
	if otherwise is not None:
		return DamnUnicode(otherwise)
DV.postEvent = DamnNothing # Will be replaced by wx's events
