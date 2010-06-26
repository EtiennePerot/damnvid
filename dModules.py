# -*- coding: utf-8 -*-
from dCore import *
from dLog import *
from dTubes import *
import time
import tarfile
import shutil
class DamnVideoModule:
	def __init__(self, uri):
		self.name = 'generic'
		self.uri = uri
		self.link = None
		self.id = None
		self.valid = None
		self.title = None
		self.ticket = None
		self.ticketdate = 0
		self.regex = {
			'title':DV.generic_title_extract
		}
	def isUp(self):
		return True
	def validURI(self):
		return not not self.valid
	def getLink(self):
		return DamnUnicode(self.link)
	def getURI(self):
		return DamnUnicode(self.uri)
	def getID(self):
		return self.id
	def getStorage(self):
		return DV.modulesstorage[self.name]
	def getTitle(self):
		if self.title is None:
			total = DamnURLGetAll(self.link, onerror='')
			search = self.regex['title']
			if type(self.regex['title']) not in (type(()),type([])):
				search = (self.regex['title'],)
			for i in search:
				res = i.search(total)
				if res:
					self.title = DamnHtmlEntities(res.group(1))
					break
		if self.title is not None:
			return DamnUnicode(self.title)
		return DV.l('Unknown title')
	def getIcon(self):
		return self.name
	def pref(self, pref, value=None):
		if value is None:
			return DV.prefs.getm(self.name, pref)
		return DV.prefs.setm(self.name, pref, value)
	def newTicket(self, ticket):
		self.ticket = ticket
		self.ticketdate = time.time()
	def getProfile(self):
		return self.pref('profile')
	def getOutdir(self):
		return self.pref('outdir')
	def renewTicket(self):
		if self.ticket is None:
			self.newTicket(self.uri)
	def getDownload(self):
		self.renewTicket()
		return self.ticket
	def getFFmpegArgs(self):
		return []
	def getDownloadGetter(self):
		return self.getDownload
	def addVid(self, parent):
		parent.addValid(self.getVidObject())
	def getVidObject(self):
		obj = {'name':DamnUnicode(self.getTitle()), 'profile':self.getProfile(), 'profilemodified':False, 'fromfile':DamnUnicode(self.getTitle()), 'dirname':DamnUnicode(self.getLink()), 'uri':DamnUnicode(self.getID()), 'status':DV.l('Pending.'), 'icon':self.getIcon(), 'module':self, 'downloadgetter':self.getDownloadGetter()}
		Damnlog('Module', self.name, 'returning video object:', obj)
		return obj
def DamnInstallModule(module):
	Damnlog('Attempting to install module', module)
	if not os.path.exists(module):
		return 'nofile'
	if not tarfile.is_tarfile(module):
		return 'nomodule'
	mod = tarfile.open(module, 'r')
	files = mod.getnames()
	if not len(files):
		return 'nomodule'
	if files[0].find('/') in (-1, 0):
		return 'nomodule'
	prefix = files[0][0:files[0].find('/') + 1]
	for i in files:
		if i.find('/') in (-1, 0):
			return 'nomodule'
		if i[0:i.find('/') + 1] != prefix:
			return 'nomodule'
	if os.path.exists(DV.modules_path + prefix):
		if os.path.isdir(DV.modules_path + prefix):
			shutil.rmtree(DV.modules_path + prefix)
		else:
			os.remove(DV.modules_path + prefix)
	mod.extractall(DV.modules_path)
	try:
		DV.prefs.rems('damnvid-module-' + prefix[0:-1]) # Reset module preferences when installing it.
		DV.prefs.save()
	except:
		Damnlog('Resetting module preferences for module', module, '(probably not installed or left default before)')
	DamnLoadModule(DV.modules_path + prefix[0:-1])
	Damnlog('Success installing module', module)
	return 'success'
def DamnIterModules(keys=True): # Lawl, this spells "DamnIt"
	mods = DV.modules.keys()
	mods.sort()
	if keys:
		return mods
	ret = []
	for i in mods:
		ret.append(DV.modules[i])
	return ret
def DamnRegisterModule(module):
	Damnlog('Attempting to register module', module)
	if module.has_key('minversion'):
		if DamnVersionCompare(module['minversion'], DV.version)==1:
			return 'minversion'
	DV.modules[module['name']] = module
	DV.modulesstorage[module['name']] = {}
	if module.has_key('register'):
		module['class'].register = {}
		if module['register'].has_key('listicons'):
			module['class'].register['listicons'] = {}
			for icon in module['register']['listicons'].iterkeys():
				DV.listicons.add(DV.modules_path + module['name'] + DV.sep + module['register']['listicons'][icon], icon)
	if module.has_key('preferences'):
		for pref in module['preferences'].iterkeys():
			DV.preferences['damnvid-module-' + module['name'] + ':' + pref] = module['preferences'][pref]
			DV.defaultprefs['damnvid-module-' + module['name'] + ':' + pref] = module['preferences'][pref]['default']
			if module['preferences'][pref]['kind'] == 'dir':
				DV.path_prefs.append('damnvid-module-' + module['name'] + ':' + pref)
		if module.has_key('preferences_order'):
			DV.preference_order['damnvid-module-' + module['name']] = module['preferences_order']
		else:
			DV.preference_order['damnvid-module-' + module['name']] = module['preferences'].keys()
	Damnlog('Module registered:', module)
def DamnGetAlternateModule(uri):
	Damnlog('Got request to get new module for URI:', uri)
	urlgrabber = DamnVideoLoader(None, [uri], feedback=False, allownonmodules=False)
	urlgrabber.start()
	time.sleep(.1)
	while not urlgrabber.done:
		time.sleep(.05)
	res = urlgrabber.result
	urlgrabber.done = False
	if res is None:
		Damnlog('No module found for URI:',uri,'; DamnGetAlternateModule returning None.')
		return None
	Damnlog('Module found for URI:',uri,'; returning', res['module'])
	return res['module']
from dIsolatedModule import *
