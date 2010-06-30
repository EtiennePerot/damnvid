#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import shutil
import hashlib

os.chdir(os.path.abspath(os.path.dirname(sys.argv[0])))
if not len(sys.argv)!=1:
	print >> sys.stderr, 'Must include fork name.'
	sys.exit(1)
fork = sys.argv[1]
if not len(fork) or fork == os.sep:
	print >> sys.stderr, 'Must include fork name.'
	sys.exit(1)
if fork[-1] == os.sep:
	fork = fork[:-1]
if not os.path.isdir(fork):
	print >> sys.stderr, 'Invalid fork name:', fork
	sys.exit(1)
def md5sum(f):
	if not os.path.isfile(f):
		return None
	m = hashlib.md5()
	for i in open(f,'rb'):
		m.update(i)
	return m.hexdigest()

def syncTree(t1, t2, exc=None, ignore=[]):
	if not len(t1):
		t1 = '.'
	if not len(t2):
		t2 = '.'
	if not os.path.exists(t1):
		return
	if os.path.isdir(t1):
		if t1[-1] != os.sep:
			t1 += os.sep
		if t2[-1] != os.sep:
			t2 += os.sep
		if not os.path.exists(t2):
			print 'Creating', t2
			os.makedirs(t2)
		for f in os.listdir(t1):
			if f in ignore:
				print 'Ignoring', t1 + f
				continue
			if exc is None:
				syncTree(t1 + f, t2 + f, ignore=ignore)
			else:
				if not len(exc):
					exc = '.'
				if exc[-1] != os.sep:
					exc += os.sep
				syncTree(t1 + f, t2 + f, exc=exc + f, ignore=ignore)
	elif os.path.isfile(t1):
		if exc is not None:
			if os.path.exists(exc):
				print 'Excluding', exc
				return
		if md5sum(t1) != md5sum(t2):
			print 'Copying', t1, 'to', t2
			shutil.copyfile(t1, t2)
		else:
			print 'Same file:', t1, 'vs', t2
	else:
		print >> sys.stderr, 'Warning: Unknown file type:', t1
syncTree('..', 'package-'+fork, exc=fork, ignore=['forks', '.svn'])
syncTree(fork, 'package-'+fork, ignore=['.svn'])
