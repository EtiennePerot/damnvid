# -*- coding: utf-8 -*-
import os, sys, platform
from dCore import *
def DamnSysinfo():
	try:
		sysinfo = u'DamnVid version: ' + DV.version + u'\nDamnVid mode: '
		if DV.bit64:
			sysinfo += u'64-bit'
		else:
			sysinfo += u'32-bit'
		sysinfo += u'\nDamnVid arguments: '
		if len(sys.argv[1:]):
			sysinfo += DamnUnicode(' '.join(sys.argv[1:]))
		else:
			sysinfo += u'(None)'
		sysinfo += u'\nMachine name: '
		if len(platform.node()):
			sysinfo += DamnUnicode(platform.node())
		else:
			sysinfo += u'Unknown'
		sysinfo += u'\nPlatform: '
		if len(platform.platform()):
			sysinfo += DamnUnicode(platform.platform())
		else:
			sysinfo += u'Unknown platform'
		if len(platform.release()):
			sysinfo += u' / ' + DamnUnicode(platform.release())
		else:
			sysinfo += u' / Unknown release'
		sysinfo += u'\nArchitecture: ' + DamnUnicode(' '.join(platform.architecture()))
		if len(platform.machine()):
			sysinfo += u' / ' + DamnUnicode(platform.machine())
		else:
			sysinfo += u' / Unknown machine type'
		sysinfo += u'\nPATH: '
		if os.environ.has_key('PATH'):
			sysinfo += DamnUnicode(os.environ['PATH'])
		else:
			sysinfo += u'(None)'
		return DamnUnicode(sysinfo)
	except:
		try:
			return u'System information collection failed. Got so far: ' + DamnUnicode(sysinfo)
		except:
			return u'System information collection failed.'
