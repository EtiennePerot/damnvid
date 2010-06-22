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
def DamnExecFile(f, globs={}, addDV=True):
	if addDV:
		globs['DV'] = DV
	try:
		execfile(DamnUnicode(f), globs)
	except:
		try:
			execfile(DamnUnicode(f).encode('utf8'), globs)
		except:
			try:
				execfile(DamnUnicode(f).encode('windows-1252'), globs)
			except:
				print 'Could not execute file:', f
class DamnEmpty:
	pass
DV = DamnEmpty()
