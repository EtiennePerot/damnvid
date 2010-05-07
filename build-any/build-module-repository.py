#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
class DamnVideoModule:
	pass
DV=DamnVideoModule()
DV.preference_type_audio=None
DV.preference_type_video=None
DV.preference_type_profile=None
DV.preference_type_misc=None
modules=[]
def DamnRegisterModule(module):
	global modules
	modules.append('<tr><td>http://damnvid.googlecode.com/svn/trunk/modules/'+module['name']+'/'+module['icon']['large']+'</td>\n<td>'+module['title']+' module (`'+module['name']+'`):\n  * Latest version: `'+module['version']+'`.\n  * Available at: [http://damnvid.googlecode.com/files/'+module['name']+'-'+module['version']+'.module.damnvid http://damnvid.googlecode.com/files/'+module['name']+'-'+module['version']+'.module.damnvid].</td></tr>')
while not os.path.exists('DamnVid.py'):
	os.chdir('..')
moddirs = []
for m in os.listdir('modules'):
	moddirs.append(m)
moddirs.sort()
for m in moddirs:
	if os.path.isdir('modules'+os.sep+m):
		for f in os.listdir('modules'+os.sep+m):
			if f[-8:]=='.damnvid':
				execfile('modules'+os.sep+m+os.sep+f)
print """#summary DamnVid's wiki-based module repository.

= Introduction =

Modules are little pieces of code that add functionality to DamnVid. This page is basically a list of the modules available for DamnVid, and acts as their repository.

= Details =

The following modules are available:
<table border="0">
""" + '\n'.join(modules) + """
</table>"""
