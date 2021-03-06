#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import platform
import shutil
import getopt
import subprocess
import py_compile

def procs(command):
	p = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	for l in p.stdout:
		print '>', l.strip()
	return p.communicate()

OSNAME=os.name
if OSNAME=='posix' and sys.platform=='darwin':
	OSNAME='mac'
os.chdir(os.path.abspath(os.path.dirname(sys.argv[0]) + os.sep + '..'))
try:
	procs(['python2', 'build-any' + os.sep + 'cleanup.py'])
except:
	procs(['python', 'build-any' + os.sep + 'cleanup.py'])
opts, args = getopt.getopt(sys.argv[1:], 'o:d:f:')
outputFile = 'required-files.txt'
destFolder = None
forkFolder = None
for option, argument in opts:
	if option == '-o':
		outputFile = argument
	elif option == '-d':
		destFolder = argument
		if destFolder[-1] != os.sep:
			destFolder += os.sep
	elif option == '-f':
		forkFolder = 'forks' + os.sep + argument
		if forkFolder[-1] != os.sep:
			forkFolder += os.sep
if os.path.exists(outputFile):
	os.remove(outputFile)
if os.path.exists('COPYING'):
	os.remove('COPYING')
def goodFile(f):
	return f.find('.svn')==-1 and f.find('LICENSE')==-1 and f.find('.psd')==-1 and f.find('.noinclude')==-1 and f.find('.bmp')==-1 and f.find('.ai')==-1 and f.find('.exe')==-1 and f.find('.zip')==-1 and f.find('fireworks.png')==-1
required_files=[]
absolute_files=[]
def appendToList(f):
	global required_files, absolute_files
	f = f.replace('.' + os.sep, '')
	a = os.path.abspath(f)
	if a not in absolute_files and goodFile(a):
		required_files.append(f)
		absolute_files.append(a)
def addFile(*args):
	global required_files, forkFolder
	for f in args:
		if forkFolder is not None:
			if os.path.exists(forkFolder + f):
				appendToList(forkFolder + ':' + f)
			else:
				appendToList(f)
		else:
			appendToList(f)
shutil.copyfile('build-any/COPYING','./COPYING')
addFile('version.d','COPYING')
if OSNAME=='nt':
	addFile('DamnVid.exe')
	shutil.copyfile('build-exe/DamnVid.exe.manifest','DamnVid.exe.manifest')
	addFile('DamnVid.exe.manifest')
required_dirs=['img', 'conf', 'locale']
required_modules=['socks', 'ui']
def addDir(d):
	for f in os.listdir(d):
		if goodFile(f):
			if os.path.isdir(d + os.sep + f):
				addDir(d + os.sep + f)
			else:
				addFile(d + os.sep + f)
def addModule(f, recursive=True):
	if OSNAME != 'posix' or not goodFile(f):
		return
	if os.path.isdir(f):
		for i in os.listdir(f):
			if os.path.isdir(f + os.sep + i) and recursive:
				addDir(f + os.sep + i)
				addModule(f + os.sep + i, recursive=recursive)
			elif i[-3:] == '.py':
				addModule(f + os.sep + i, recursive=recursive)
	elif f[-3:] == '.py':
		try:
			py_compile.compile(f)
			if os.path.exists(f+'o'):
				addFile(f+'o')
				addFile(f)
			elif os.path.exists(f+'c'):
				addFile(f+'c')
				addFile(f)
			addFile(f)
		except:
			print >> sys.stderr, 'Error while compyling', f
			addFile(f)
for d in required_dirs:
	addDir(d)
addModule('.', recursive=False)
for m in required_modules:
	addModule(m)
# Build DamnVid modules
for f in os.listdir('.'):
	if f[-15:]=='.module.damnvid':
		os.remove(f)
for f in os.listdir('modules'):
	if f[-15:]=='.module.damnvid':
		os.remove('modules' + os.sep + f)
for f in os.listdir('modules'):
	if os.path.isdir('modules' + os.sep + f) and goodFile(f):
		try:
			procs(['python2', 'build-any' + os.sep + 'module-package.py', 'modules' + os.sep + f])
		except:
			procs(['python', 'build-any' + os.sep + 'module-package.py', 'modules' + os.sep + f])
for f in os.listdir('.'):
	if f[-15:]=='.module.damnvid':
		if os.path.exists('modules' + os.sep + f):
			os.remove('modules' + os.sep + f)
		os.rename(f,'modules' + os.sep + f)
		addFile('modules' + os.sep + f)
specialfiles = {}
if OSNAME=='nt':
	addFile('bin' + os.sep + 'ffmpeg.exe','bin' + os.sep + 'taskkill.exe','bin' + os.sep + 'SDL.dll')
	specialfiles = {}
elif OSNAME=='mac':
	addFile('bin' + os.sep + 'ffmpegosx')
	specialfiles = {}
else:
	specialfiles = {
		'build-deb/damnvid.desktop': '/usr/share/applications/',
		'build-deb/damnvid': '/usr/bin/'
	}
required_file=open(outputFile,'w')
for f in required_files:
        print 'Required:', f
	required_file.write(f)
	if destFolder is not None:
		p = destFolder + os.path.dirname(f)
		if p[-1] != os.sep:
			p += os.sep
		required_file.write(' ' + p)
	required_file.write('\n')
for f in specialfiles.keys():
	required_file.write(f)
	if specialfiles[f] is not None:
		p = specialfiles[f]
		if p[-1] != os.sep:
			p += os.sep
		required_file.write(' ' + p)
	required_file.write('\n')
required_file.close()
