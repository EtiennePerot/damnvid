# -*- coding: utf-8 -*-
from dCore import *
from dLog import *
import subprocess
def DamnFindBinary(binary):
	if type(binary) in (type(()), type([])):
		Damnlog('DamnFindBinary summoned for binaries', binary)
		if not len(binary):
			Damnlog('Binaries list is empty:', binary, '; returning empty string.')
			return ''
		for b in binary:
			searched = DamnFindBinary(b)
			if searched != b:
				return searched
		Damnlog('!! Found no suitable binary out of the list', binary, '; returning first element:', binary[0])
		return binary[0]
	Damnlog('DamnFindBinary summoned for binary', binary)
	for p in DV.bin_paths:
		if os.path.isdir(p):
			if os.path.isfile(p + binary):
				Damnlog('DamnFindBinary found suitable binary:', p + binary)
				return p + binary
		else:
			Damnlog('Warning: Binary path', p,'is not a directory.')
	Damnlog('!! Binary', binary, 'not found, returning simply', binary)
	return binary
def DamnSpawner(cmd, shell=False, stderr=None, stdout=None, stdin=None, cwd=None, bufsize=0):
	if cwd is None:
		cwd = DV.curdir
	cwd = DamnUnicode(cwd)
	if type(cmd) in (type(''), type(u'')):
		cmd = DamnUnicode(cmd)
	else:
		for i in range(len(cmd)):
			cmd[i] = DamnUnicode(cmd[i])
	if DV.os == 'nt':
		import win32process
		if type(cmd) in (type([]), type(())):
			tempcmd = []
			for i in cmd:
				tempcmd.append(DamnUnicode(i).encode('windows-1252'))
			Damnlog('Spawning subprocess on NT:', tempcmd)
			Damnlog('Actual command:', subprocess.list2cmdline(tempcmd))
			return subprocess.Popen(tempcmd, shell=shell, creationflags=win32process.CREATE_NO_WINDOW, stderr=subprocess.PIPE, stdout=subprocess.PIPE, stdin=subprocess.PIPE, cwd=cwd.encode('windows-1252'), executable=None, bufsize=bufsize) # Yes, ALL std's must be PIPEd, otherwise it doesn't work on win32 (see http://www.py2exe.org/index.cgi/Py2ExeSubprocessInteractions)
		else:
			Damnlog('Spawning subprocess on NT:', cmd)
			Damnlog('Actual command:', subprocess.list2cmdline(cmd))
			return subprocess.Popen(cmd.encode('windows-1252'), shell=shell, creationflags=win32process.CREATE_NO_WINDOW, stderr=subprocess.PIPE, stdout=subprocess.PIPE, stdin=subprocess.PIPE, cwd=cwd.encode('windows-1252'), executable=None, bufsize=bufsize)
	else:
		Damnlog('Spawning subprocess on UNIX:', cmd)
		Damnlog('Actual command:', subprocess.list2cmdline(cmd))
		return subprocess.Popen(cmd, shell=shell, stderr=stderr, stdout=stdout, stdin=stdin, cwd=cwd, executable=None, bufsize=bufsize)
def DamnOpenWebbrowser(url, *args):
	url = DamnUnicode(url)
	Damnlog('Opening URL in web browser:', url)
	webbrowser.open(url, 2)
def DamnOpenFileManager(directory, *args):
	if directory is not None:
		directory = DamnUnicode(directory)
	Damnlog('Opening default file manager at directory', directory)
	if DV.os == 'nt':
		DamnSpawner([u'explorer.exe', u'/e,', DamnUnicode(directory)])
	elif DV.os == 'mac':
		DamnSpawner([u'open', DamnUnicode(directory)])
	else:
		DamnSpawner([u'xdg-open', DamnUnicode(directory)])
def DamnLaunchFile(f, *args):
	f = DamnUnicode(f)
	if DV.os == 'nt':
		import win32api
		DamnSpawner([u'cmd', u'/c', u'start ' + DamnUnicode(win32api.GetShortPathName(f)).replace(u'"', u'\\"')])
	else:
		DamnOpenFileManager(f) # Hax! It works because 'open' or 'xdg-open' do not only open directories.
