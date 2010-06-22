#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, sys
import shutil
import re

os.chdir(os.path.abspath(os.path.dirname(sys.argv[0]) + os.sep + '..'))
def shazarr(f):
	print 'Cleaning up:', f
	if os.path.isdir(f):
		pass#shutil.rmtree(f)
	else:
		pass#os.remove(f)
def cleanDir(d, deletables):
	if d[-1] == os.sep:
		d = d[:-1]
	for i in deletables:
		if i.find('*') != -1:
			r = re.compile(re.escape(i).replace('\\*', '.*'), re.IGNORECASE)
			for f in os.listdir(d):
				if r.match(f):
					shazarr(d + os.sep + f)
		elif os.path.lexists(d + os.sep + i):
			shazarr(d + os.sep + i)
def cleanAll(d, deletables):
	if d[-1] == os.sep:
		d = d[:-1]
	for i in os.listdir(d):
		if os.path.isdir(f):
			cleanAll(d + os.sep + f. deletables)
	cleanDir(d, deletables)
cleanDir('.', ['COPYING', 'DamnVid.exe.manifest', 'required-files.txt', 'damnvid.spec', 'package', 'usr', 'DamnVid.app', '*.module.damnvid', '*.so', '*.so.*', 'build.tar.gz', 'library.zip', 'py', 'NSIS-win32.nsi', 'DamnVid', '*.tmp', 'damnvid-locale-warnings.log'])
cleanDir('.' + os.sep + 'modules', ['*.module.damnvid'])
cleanAll('.', ['*.pyc', '*.pyo'])
