# -*- coding: utf-8 -*-
from dCore import *
from dConstants import *
from dLog import *
from dThread import *
from dTubes import *
from dModules import *
import re
class DamnModuleUpdateCheck(DamnThread):
	def __init__(self, parent, modules, byevent=True):
		Damnlog('Spawned module update checker for modules', modules, 'by event:', byevent)
		self.parent = parent
		if type(modules) is not type([]):
			modules = [modules]
		self.modules = modules
		self.done = {}
		self.downloaded = []
		self.byevent = byevent
		DamnThread.__init__(self)
	def postEvent(self, module, result):
		info = {'module':module, 'result':result}
		Damnlog('Update checker sending event:', info, 'by event:', self.byevent)
		if self.byevent:
			DV.postEvent(self.parent, (DV.evt_loading, -1, info))
		else:
			self.parent.onLoad(info)
	def go(self):
		for module in self.modules:
			if not module['about'].has_key('url'):
				self.postEvent(module, 'cannot')
			elif module['about']['url'] not in self.downloaded:
				self.downloaded.append(module['about']['url'])
				checkingfor = [module]
				try:
					http = DamnURLOpen(module['about']['url'])
					for module2 in self.modules:
						if module2['about'].has_key('url'):
							if module2['about']['url'] == module['about']['url'] and module2 not in checkingfor:
								checkingfor.append(module2)
					html = ''
					for i in http:
						html += i
				except:
					html = ''
				for module2 in checkingfor:
					res = re.search('<tt>' + re.escape(module2['name']) + '</tt>.*?Latest\s+version\s*:\s*<tt>([^<>]+)</tt>.*?Available\s+at\s*:\s*<a href="([^"]+)"', html, re.IGNORECASE)
					if not res:
						self.postEvent(module2, 'error')
					else:
						vers = DamnHtmlEntities(res.group(1))
						if DamnVersionCompare(vers,DamnUnicode(module2['version']))==1:
							url = DamnHtmlEntities(res.group(2)).strip()
							if not REGEX_HTTP_GENERIC.match(url):
								self.postEvent(module2, 'error')
							else:
								try:
									http = DamnURLOpen(url)
									tmpname = DamnTempFile()
									tmp = DamnOpenFile(tmpname, 'wb')
									for i in http:
										tmp.write(i)
									tmp.close()
									http.close()
									DamnInstallModule(tmpname)
									self.postEvent(module2, (vers, url))
								except:
									self.postEvent(module2, 'error')
						else:
							self.postEvent(module2, 'uptodate')
class DamnVidUpdater(DamnThread):
	def __init__(self, parent, verbose=False, main=True, modules=True):
		Damnlog('Spawned main updater thread')
		self.parent = parent
		self.todo = {'main':main, 'modules':modules}
		self.info = {'main':None, 'modules':{}, 'verbose':verbose}
		DamnThread.__init__(self)
	def postEvent(self):
		Damnlog('Main updated thread sending event', self.info)
		DV.postEvent(self.parent, (DV.evt_loading, -1, {'updateinfo':self.info}))
	def onLoad(self, info):
		if not info.has_key('module'):
			return
		self.info['modules'][info['module']['name']] = info['result']
	def go(self):
		if self.todo['main']:
			regex = re.compile('<tt>([^<>]+)</tt>', re.IGNORECASE)
			try:
				html = DamnURLOpen(DV.url_update)
				for i in html:
					if regex.search(i):
						self.info['main'] = regex.search(i).group(1).strip()
			except:
				pass
		if self.todo['modules']:
			updater = DamnModuleUpdateCheck(self, DamnIterModules(False), False)
			updater.run() # Yes, run(), not start(), this way we're waiting for it to complete.
		self.postEvent()
