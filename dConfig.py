# -*- coding: utf-8 -*-
from dCore import *
from dConstants import *
from dLog import *
from dSpawn import *
from dTubes import *
from dModules import *
import os
import shutil
import ConfigParser
import base64
class DamnPrefs: # Preference manager (backend, not GUI)
	def __init__(self):
		self.conf = {}
		f = DamnOpenFile(DV.conf_file, 'r')
		self.ini = ConfigParser.SafeConfigParser()
		self.ini.readfp(f)
		f.close()
		self.profiles = 0
		for i in self.ini.sections():
			if i[:16] == 'damnvid-profile-':
				self.profiles = self.profiles + 1
	def expandPath(self, value):
		value = DamnUnicode(value)
		value = REGEX_PATH_MULTI_SEPARATOR_CHECK.sub(u'/', value.replace(DV.sep, u'/').replace(u'?DAMNVID_MY_VIDEOS?', DV.my_videos_path.replace(DV.sep, u'/'))).replace(u'/', DV.sep)
		if value[-1:] != DV.sep:
			value += DV.sep
		return value
	def reducePath(self, value):
		value = DamnUnicode(value)
		value = REGEX_PATH_MULTI_SEPARATOR_CHECK.sub(u'/', value.replace(DV.sep, u'/').replace(DV.my_videos_path.replace(DV.sep, u'/'), u'?DAMNVID_MY_VIDEOS?')).replace(DV.sep, u'/')
		if value[-1:] != u'/':
			value += u'/'
		return value
	def gets(self, section, name):
		name = name.lower()
		shortsection = section
		if shortsection[:16] == 'damnvid-profile-':
			shortsection = 'damnvid-profile'
		if self.ini.has_section(section):
			if self.ini.has_option(section, name):
				value = DamnUnicode(self.ini.get(section, name))
			elif DV.defaultprefs.has_key(shortsection + ':' + name):
				value = DamnUnicode(DV.defaultprefs[shortsection + ':' + name])
				self.sets(section, name, value)
			else:
				value = u''
			if shortsection + ':' + name in DV.path_prefs:
				value = DamnUnicode(self.expandPath(value))
			return value
		if DV.defaultprefs.has_key(section + ':' + name):
			value = DamnUnicode(DV.defaultprefs[section + ':' + name])
			self.ini.add_section(section)
			self.sets(section, name, value)
			return DamnUnicode(self.gets(section, name))
		Damnlog('No such pref:', section + ':' + name)
	def sets(self, section, name, value):
		name = name.lower()
		value = DamnUnicode(value)
		if self.ini.has_section(section):
			if section + ':' + name in DV.path_prefs:
				value = self.reducePath(value)
			return self.ini.set(section, name, value.encode('utf8'))
		else:
			Damnlog('No such section:', section)
	def rems(self, section, name=None):
		try:
			if name is None:
				self.ini.remove_section(section)
			else:
				self.ini.remove_option(section, name)
		except:
			Damnlog('No such section/option:', section, '/', name)
	def lists(self, section):
		prefs = []
		if DV.preference_order.has_key(section):
			prefs.extend(DV.preference_order[section])
		if self.ini.has_section(section):
			for i in self.ini.options(section):
				if i not in prefs:
					prefs.append(i)
		if len(prefs):
			return prefs
		Damnlog('No such section:', section)
	def listsections(self):
		return self.ini.sections()
	def get(self, name):
		return self.gets('damnvid', name)
	def set(self, name, value):
		return self.sets('damnvid', name, value)
	def getp(self, profile, name):
		if int(profile) == -1:
			if name.lower() == 'name':
				return '(Do not encode)'
			if name.lower() == 'outdir':
				return self.get('defaultoutdir')
		return self.gets('damnvid-profile-' + str(profile), name)
	def setp(self, profile, name, value):
		return self.sets('damnvid-profile-' + str(profile), name, value)
	def listp(self, profile):
		return self.lists('damnvid-profile-' + str(profile))
	def getm(self, module, name):
		return self.gets('damnvid-module-' + module, name)
	def setm(self, module, name, value):
		return self.sets('damnvid-module-' + module, name, value)
	def addp(self):
		self.ini.add_section('damnvid-profile-' + str(self.profiles))
		for i in DV.defaultprefs.iterkeys():
			if i[0:16] == 'damnvid-profile:':
				self.setp(self.profiles, i[16:], DamnUnicode(DV.defaultprefs[i]))
		self.profiles += 1
	def remp(self, profile):
		if self.profiles > 1:
			for i in DV.preferences.iterkeys():
				section, option = (i[0:i.find(':')], i[i.find(':') + 1:])
				if DV.preferences[i]['kind'] == 'profile':
					if int(self.gets(section, option)) == int(profile):
						self.ini.set(section, option, '0') # Fall back to default profile
					elif int(self.gets(section, option)) > int(profile):
						self.ini.set(section, option, str(int(self.gets(section, option)) - 1))
			for i in DamnIterModules():
				for j in DV.modules[i]['preferences'].iterkeys():
					if DV.modules[i]['preferences'][j]['kind'] == 'profile':
						if int(self.getm(DV.modules[i]['name'], j)) == int(profile):
							self.setm(DV.modules[i]['name'], j, '0') # Fall back to default profile
						elif int(self.getm(DV.modules[i]['name'], j)) > int(profile):
							self.setm(DV.modules[i]['name'], j, str(int(self.getm(DV.modules[i]['name'], j)) - 1))
			for i in range(profile, self.profiles - 1):
				for j in self.ini.options('damnvid-profile-' + str(i)):
					self.ini.remove_option('damnvid-profile-' + str(i), j)
				for j in self.ini.options('damnvid-profile-' + str(i + 1)):
					self.ini.set('damnvid-profile-' + str(i), j, self.ini.get('damnvid-profile-' + str(i + 1), j))
			self.profiles -= 1
			self.ini.remove_section('damnvid-profile-' + str(self.profiles))
			return self.profiles
		return None
	def geta(self, section, name):
		try:
			array = eval(base64.b64decode(self.gets(section, name)))
		except:
			array = []
		unicodearray = []
		for i in array:
			unicodearray.append(DamnUnicode(i))
		return unicodearray
	def seta(self, section, name, value):
		return self.sets(section, name, base64.b64encode(DamnUnicode(value)))
	def save(self):
		f = DamnOpenFile(DV.conf_file, 'w')
		self.ini.write(f)
		f.close()
		DamnURLOpener()
def DamnLoadConfig(forcemodules=False):
	Damnlog('Loading config.')
	DV.preferences = None
	DamnExecFile(DV.curdir + u'conf' + DV.sep + u'preferences.d', globs=globals())
	DV.path_prefs = []
	DV.defaultprefs = {
	}
	for i in DV.preferences.iterkeys():
		if DV.preferences[i].has_key('default'):
			DV.defaultprefs[i] = DV.preferences[i]['default']
		else:
			DV.defaultprefs[i] = None
		if DV.preferences[i]['kind'] == 'dir':
			DV.path_prefs.append(i)
	DV.prefs = None # Will be loaded later
	# Load modules
	Damnlog('Loading modules.')
	DV.modules_path = DV.conf_file_directory + 'modules' + DV.sep
	if not os.path.exists(DV.modules_path):
		os.makedirs(DV.modules_path)
	DV.modules = {}
	DV.modulesstorage = {}
	DV.generic_title_extract = re.compile('<title>\s*([^<>]+?)\s*</title>', re.IGNORECASE)
	DV.listicons.resetList({
		'damnvid':DV.images_path + 'video.png',
		'generic':DV.images_path + 'online.png'
	})
	if forcemodules or '--rebuild-modules' in DV.argv:
		Damnlog('forcemodules is on; resetting modules.')
		shutil.rmtree(DV.modules_path)
		os.makedirs(DV.modules_path)
		if '--rebuild-modules' in DV.argv: # DEBUG ONLY; rebuilds all modules
			Damnlog('Careful, rebuilding all modules!')
			DV.argv = [x for x in DV.argv if x != '--rebuild-modules']
			for i in os.listdir('.'):
				if i.lower().endswith(u'.module.' + DV.safeProduct):
					os.remove(i)
			for i in os.listdir(DV.curdir + 'modules/'):
				if i.lower().endswith(u'.module.' + DV.safeProduct):
					os.remove(DV.curdir + 'modules/' + i)
			for i in os.listdir(DV.curdir + 'modules'):
				if os.path.isdir(DV.curdir + 'modules/' + i) and i.find('svn') == -1:
					Damnlog('Building module ' + i)
					try:
						DamnSpawner(['python2', 'build-any/module-package.py', DV.curdir + 'modules/' + i ], cwd=DV.curdir).wait()
					except:
						DamnSpawner(['python', 'build-any/module-package.py', DV.curdir + 'modules/' + i ], cwd=DV.curdir).wait()
			for i in os.listdir(DV.curdir):
				if i.lower().endswith(u'.module.' + DV.safeProduct):
					os.rename(DV.curdir + i, DV.curdir + 'modules/' + i)
		for i in os.listdir(DV.curdir + 'modules'):
			if i.lower().endswith(u'.module.' + DV.safeProduct):
				Damnlog('Installing', i)
				DamnInstallModule(DV.curdir + 'modules' + DV.sep + i)
	for i in os.listdir(DV.modules_path):
		if os.path.isdir(DV.modules_path + i):
			DamnLoadModule(DV.modules_path + i)
	# End load modules
