#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import shutil

def crush(f):
	while f[0:2]=='./' or f[0:2]=='.'+os.sep:
		f=f[2:]
	d=os.path.dirname('/pics/'+f)
	if not os.path.lexists(d):
		os.makedirs(d)
	shutil.copyfile('./'+f,'/pics/'+f)
	p=os.popen('pngcrush -rem gAMA -rem cHRM -rem iCCP -rem sRGB -brute "./'+f+'" "./'+f+'.crushed"')
	for i in p.readlines():
		pass#print i.strip()
	p.close()
	if os.path.lexists('./'+f+'.crushed'):
		os.remove('./'+f)
		os.rename('./'+f+'.crushed','./'+f)
def crushDir(d):
	print 'Parsing',d
	for f in os.listdir(d):
		f=d+os.sep+f
		if os.path.isdir(f) and f.find('.svn')==-1:
			crushDir(f)
		elif f[-4:].lower()=='.png' and f[-14:]!='.fireworks.png':
			print 'Crushing',f
			crush(f)
crushDir('.')
