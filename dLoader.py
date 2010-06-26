# -*- coding: utf-8 -*-
from dCore import *
from dConstants import *
from dLog import *
from dThread import *
from dModules import *
class DamnVideoLoader(DamnThread):
	def __init__(self, parent, uris, thengo=False, feedback=True, allownonmodules=True):
		DamnThread.__init__(self)
		self.uris = []
		if type(uris) not in (type(()), type([])):
			uris = [uris]
		for i in uris:
			self.uris.append(DamnUnicode(i))
		self.parent = parent
		self.thengo = thengo
		self.feedback = feedback
		self.done = False
		self.result = None
		self.allownonmodules = allownonmodules
		Damnlog('DamnVideoLoader spawned with parameters: parent =',parent,'; thengo?',thengo,'; feedback?',feedback,'; allow non-modules?',allownonmodules)
	def go(self):
		if self.feedback:
			self.parent.toggleLoading(True)
		self.vidLoop(self.uris)
		self.done = True
		if self.feedback:
			self.parent.toggleLoading(False)
		else:
			while self.done:
				time.sleep(.1)
	def postEvent(self, info):
		if self.feedback:
			DV.postEvent(self.parent, (DV.evt_loading, info))
	def getVidName(self, uri):
		return self.parent.getVidName(uri)
	def addValid(self, meta):
		meta['original'] = self.originaluri
		self.result = meta
		self.postEvent({'meta':meta, 'go':self.thengo})
	def SetStatusText(self, status):
		self.postEvent({'status':status})
	def showDialog(self, title, content, icon):
		self.postEvent({'dialog':(title, content, icon)})
	def vidLoop(self, uris):
		Damnlog('Starting vidLoop with URIs:',uris)
		for uri in uris:
			Damnlog('vidLoop considering URI:',uri)
			self.originaluri = uri
			bymodule = False
			for module in DamnIterModules(False):
				Damnlog('Trying module',module['class'],'for URI',uri)
				mod = module['class'](uri)
				if mod.validURI():
					Damnlog('Module has been chosen for URI',uri,':',mod)
					mod.addVid(self)
					bymodule = True
					break
			if not bymodule:
				Damnlog('No module found for URI:',uri)
				if not self.allownonmodules:
					Damnlog('DamnVideoLoader exitting because no module was found and non-modules are not allowed.')
					self.result = None
					return
				if REGEX_HTTP_GENERIC.match(uri):
					Damnlog('HTTP regex still matches URI:',uri)
					name = self.getVidName(uri)
					if name == DV.l('Unknown title'):
						name = REGEX_HTTP_EXTRACT_FILENAME.sub('', uri)
					self.addValid({'name':name, 'profile':DV.prefs.get('defaultwebprofile'), 'profilemodified':False, 'fromfile':name, 'dirname':REGEX_HTTP_EXTRACT_DIRNAME.sub('\\1/', uri), 'uri':uri, 'status':DV.l('Pending.'), 'icon':'generic'})
				else:
					# It's a file or a directory
					if os.path.isdir(uri):
						Damnlog('URI',uri,'is a directory.')
						if DV.prefs.get('DirRecursion') == 'True':
							for i in os.listdir(uri):
								self.vidLoop([uri + DV.sep + i]) # This is recursive; if i is a directory, this block will be executed for it too
						else:
							if len(uris) == 1: # Only one dir, so an alert here is tolerable
								self.showDialog(DV.l('Recursion is disabled.'), DV.l('This is a directory, but recursion is disabled in the preferences. Please enable it if you want DamnVid to go through directories.'), wx.OK | wx.ICON_EXCLAMATION)
							else:
								self.SetStatusText(DV.l('Skipped ') + uri + DV.l(' (directory recursion disabled).'))
					else:
						Damnlog('URI',uri,'is a file.')
						filename = os.path.basename(uri)
						if uri in self.parent.videos:
							self.SetStatusText(DV.l('Skipped ') + filename + DV.l(' (already in list).'))
							if len(uris) == 1: # There's only one file, so an alert here is tolerable
								self.showDialog(DV.l('Duplicate found'), DV.l('This video is already in the list!'), wx.ICON_EXCLAMATION | wx.OK)
						else:
							self.addValid({'name':filename[0:filename.rfind('.')], 'profile':DV.prefs.get('defaultprofile'), 'profilemodified':False, 'fromfile':filename, 'uri':uri, 'dirname':os.path.dirname(uri), 'status':DV.l('Pending.'), 'icon':'damnvid'})
DV.videoLoader = DamnVideoLoader
