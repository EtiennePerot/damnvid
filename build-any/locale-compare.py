#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, sys

class dummy:
	pass
def escape(s):
	if type(s) is not type(u''):
		s = unicode(s)
	return s.replace(u'\\', u'\\\\').replace(u'\'', u'\\\'')
DV = dummy()
DV.languages = {}
locales = sys.argv[1:]
if len(locales) != 2:
	print 'Can only compare two .locale files.'
	sys.exit(1)
if not os.path.exists(locales[0]):
	print locales[0], 'does not exist.'
	sys.exit(1)
if not os.path.exists(locales[1]):
	print locales[1], 'does not exist.'
	sys.exit(1)
try:
	execfile(locales[0])
	firstKey = DV.languages.keys()[0]
	first = DV.languages[firstKey]
except:
	print locales[0], 'is not a valid locale file.'
	sys.exit(1)
try:
	execfile(locales[1])
	secondKey = DV.languages.keys()[1]
	if secondKey == firstKey:
		secondKey = DV.languages.keys()[0]
	second = DV.languages[secondKey]
except:
	print locales[1], 'is not a valid locale file.'
	sys.exit(1)
missing1 = []
missing2 = []
for k in first['strings'].keys():
	if k not in second['strings'].keys():
		missing2.append(k)
if len(missing2):
	print locales[1], 'is missing the following', len(missing2), 'strings:'
	for k in range(len(missing2)):
		if k < len(missing2) - 1:
			print '\t\t\'' + escape(missing2[k]) + '\': u\'' + escape(first['strings'][missing2[k]]) + '\','
		else:
			print '\t\t\'' + escape(missing2[k]) + '\': u\'' + escape(first['strings'][missing2[k]]) + '\''
	print 'Don\'t forget to add a comma at the end of the last line before adding those lines in.'
else:
	print locales[1], 'is not missing anything.'
for k in second['strings'].keys():
	if k not in first['strings'].keys():
		missing1.append(k)
if len(missing1):
	print locales[0], 'is missing the following', len(missing1), 'strings:'
	for k in range(len(missing1)):
		if k < len(missing1) - 1:
			print '\t\t\'' + escape(missing1[k]) + '\': u\'' + escape(second['strings'][missing1[k]]) + '\','
		else:
			print '\t\t\'' + escape(missing1[k]) + '\': u\'' + escape(second['strings'][missing1[k]]) + '\''
	print 'Don\'t forget to add a comma at the end of the last line before adding those lines in.'
else:
	print locales[0], 'is not missing anything.'