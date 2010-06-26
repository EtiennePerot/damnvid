# -*- coding: utf-8 -*-
from dCore import *
from dSpawn import *
from dUI import *
from dWx import *
import random, hashlib
class DamnSplashScreen(wx.SplashScreen):
	def __init__(self):
		wx.SplashScreen.__init__(self, wx.Bitmap(DV.images_path + 'splashscreen.png', wx.BITMAP_TYPE_PNG), wx.SPLASH_CENTRE_ON_SCREEN | wx.STAY_ON_TOP, 10000, None)
		self.fadeIn()
	def fadeIn(self):
		DamnFadeIn(self)
	def fadeOut(self, destroy=True):
		DamnFadeOut(self, destroy)
class DamnListContextMenu(wx.Menu): # Context menu when right-clicking on the DamnList
	def __init__(self, parent):
		wx.Menu.__init__(self)
		self.parent = parent
		self.items = self.parent.getAllSelectedItems()
		if len(self.items): # If there's at least one item selected
			rename = wx.MenuItem(self, -1, DV.l('Rename'))
			self.AppendItem(rename)
			if len(self.items) != 1:
				rename.Enable(False)
			else:
				if self.items[0] == self.parent.parent.converting:
					rename.Enable(False)
			self.Bind(wx.EVT_MENU, self.parent.parent.onRename, rename)
			moveup = wx.MenuItem(self, -1, DV.l('Move up'))
			self.AppendItem(moveup)
			moveup.Enable(self.items[0] > 0)
			self.Bind(wx.EVT_MENU, self.parent.parent.onMoveUp, moveup)
			movedown = wx.MenuItem(self, -1, 'Move down')
			self.AppendItem(movedown)
			movedown.Enable(self.items[-1] < self.parent.GetItemCount() - 1)
			self.Bind(wx.EVT_MENU, self.parent.parent.onMoveDown, movedown)
			stop = wx.MenuItem(self, -1, DV.l('Stop'))
			self.AppendItem(stop)
			stop.Enable(self.parent.parent.converting in self.items)
			self.Bind(wx.EVT_MENU, self.parent.parent.onStop, stop)
			remove = wx.MenuItem(self, -1, DV.l('Remove from list'))
			self.AppendItem(remove)
			remove.Enable(self.parent.parent.converting not in self.items)
			self.Bind(wx.EVT_MENU, self.parent.parent.onDelSelection, remove)
			if self.parent.parent.converting not in self.items:
				onepending = False
				for i in self.items:
					if self.parent.parent.meta[self.parent.parent.videos[i]]['status'] == DV.l('Pending.'):
						onepending = True
				if not onepending:
					resetstatus = wx.MenuItem(self, -1, DV.l('Reset status'))
					self.Bind(wx.EVT_MENU,self.parent.parent.onResetStatus, resetstatus)
					self.AppendItem(resetstatus)
				profile = wx.Menu()
				uniprofile = int(self.parent.parent.meta[self.parent.parent.videos[self.items[0]]]['profile'])
				for i in self.items:
					if int(self.parent.parent.meta[self.parent.parent.videos[i]]['profile']) != uniprofile:
						uniprofile = -2
				for i in range(-1, DV.prefs.profiles):
					if uniprofile != -2:
						prof = wx.MenuItem(self, -1, DV.l(DV.prefs.getp(i, 'name'), warn=False), kind=wx.ITEM_RADIO)
						profile.AppendItem(prof) # Item has to be appended before being checked, otherwise error. Annoying code duplication.
						prof.Check(i == uniprofile)
					else:
						prof = wx.MenuItem(self, -1, DV.l(DV.prefs.getp(i, 'name'), warn=False))
						profile.AppendItem(prof)
					self.Bind(wx.EVT_MENU, DamnCurry(self.parent.parent.onChangeProfile, i), prof)    # Of course, on one platform it's self.Bind...
					profile.Bind(wx.EVT_MENU, DamnCurry(self.parent.parent.onChangeProfile, i), prof) # ... and on the other it's profile.Bind. *sigh*
				self.AppendMenu(-1, DV.l('Encoding profile'), profile)
			else:
				profile = wx.MenuItem(self, -1, 'Encoding profile')
				self.AppendItem(profile)
				profile.Enable(False)
		else: # Otherwise, display a different context menu
			addfile = wx.MenuItem(self, -1, DV.l('Add Files'))
			self.AppendItem(addfile)
			self.Bind(wx.EVT_MENU, self.parent.parent.onAddFile, addfile)
			addurl = wx.MenuItem(self, -1, DV.l('Add URL'))
			self.AppendItem(addurl)
			self.Bind(wx.EVT_MENU, self.parent.parent.onAddURL, addurl)
class DamnList(wx.ListCtrl, wx.ListCtrlAutoWidthMixin): # The ListCtrl, which inherits from the Mixin
	def __init__(self, parent, window):
		wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT)
		wx.ListCtrlAutoWidthMixin.__init__(self)
		self.parent = window # "parent" is the panel
	def onRightClick(self, event):
		p = self.HitTest(event.GetPosition())
		if p[0] != -1:
			if not self.IsSelected(p[0]):
				self.clearAllSelectedItems()
				self.Select(p[0], on=1) # Select pointed item
		else:
			self.clearAllSelectedItems()
		self.PopupMenu(DamnListContextMenu(self), event.GetPosition())
	def getAllSelectedItems(self):
		items = []
		i = self.GetFirstSelected()
		while i != -1:
			items.append(i)
			i = self.GetNextSelected(i)
		return items
	def clearAllSelectedItems(self):
		for i in self.getAllSelectedItems():
			self.Select(i, on=0)
	def invertItems(self, i1, i2):
		for i in range(self.GetColumnCount()):
			tmp = [self.GetItem(i1, i).GetText(), self.GetItem(i1, i).GetImage()]
			self.SetStringItem(i1, i, self.GetItem(i2, i).GetText(), self.GetItem(i2, i).GetImage())
			self.SetStringItem(i2, i, tmp[0], tmp[1])
class DamnDropHandler(wx.FileDropTarget): # Handles files dropped on the ListCtrl
	def __init__(self, parent):
		wx.FileDropTarget.__init__(self)
		self.parent = parent
	def OnDropFiles(self, x, y, filenames):
		self.parent.addVid(filenames)
class DamnBrowseDirButton(wx.Button): # "Browse..." button for directories
	def __init__(self, parent, id, label, control, title, callback):
		self.filefield = control
		self.title = title
		self.callback = callback
		wx.Button.__init__(self, parent, id, label)
	def onBrowse(self, event):
		dlg = wx.DirDialog(self, self.title, self.filefield.GetValue(), style=wx.DD_DEFAULT_STYLE | wx.DD_NEW_DIR_BUTTON)
		dlg.SetIcon(DV.icon)
		path = None
		if dlg.ShowModal() == wx.ID_OK:
			path = dlg.GetPath()
			self.filefield.SetValue(path)
		dlg.Destroy()
		if path != None:
			self.callback(self, path)
class DamnHyperlink(wx.HyperlinkCtrl):
	def __init__(self, parent, id, label, url, background=None, style=None):
		if style is None:
			wx.HyperlinkCtrl.__init__(self, parent, id, label, url)
		else:
			wx.HyperlinkCtrl.__init__(self, parent, id, label, url, style = style)
		if background is not None:
			self.SetBackgroundColour(background)
def DamnOmniElement(window, element, target, underline=False):
	Damnlog('Making DamnOmniElement with element', element, 'and target', target)
	bind = False
	if REGEX_HTTP_GENERIC.match(target):
		Damnlog('Target', target, 'is a URL.')
		bind = True
		element.Bind(wx.EVT_LEFT_UP, DamnCurry(DamnOpenWebbrowser, target))
	else:
		Damnlog('Target', target, 'is a file.')
		if os.path.exists(target):
			bind = True
			if os.path.isdir(target):
				element.Bind(wx.EVT_LEFT_UP, DamnCurry(DamnOpenFileManager, target))
			elif os.path.isfile(target):
				element.Bind(wx.EVT_LEFT_UP, DamnCurry(DamnLaunchFile, target))
	if bind:
		def handCursor(event=None):
			window.SetCursor(wx.StockCursor(wx.CURSOR_HAND))
			element.SetCursor(wx.StockCursor(wx.CURSOR_HAND))
		def normalCursor(event=None):
			window.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))
			element.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))
		element.Bind(wx.EVT_ENTER_WINDOW, handCursor)
		element.Bind(wx.EVT_LEAVE_WINDOW, normalCursor)
		if underline:
			underlined = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
			underlined.SetUnderlined(True)
			element.SetFont(underlined)
	return element
def DamnOmniLink(window, panel, text, target=None, underline=True):
	text = DamnUnicode(text)
	Damnlog('Making DamnOmniLink with text', text, 'with target', target)
	if target is None:
		target = text
	return DamnOmniElement(window, wx.lib.stattext.GenStaticText(panel, -1, text), target, underline=underline)
class DamnTrayIcon(wx.TaskBarIcon):
	def __init__(self, parent):
		wx.TaskBarIcon.__init__(self)
		Damnlog('DamnTrayIcon initialized with parent window',parent)
		self.parent = parent
		self.parent.Iconize(True) # Releases system memory
		self.parent.Hide()
		self.Bind(wx.EVT_TASKBAR_LEFT_DCLICK, self.raiseParent)
		self.Bind(wx.EVT_TASKBAR_CLICK, self.onMenu)
		if DV.os == 'nt':
			self.Bind(wx.EVT_TASKBAR_LEFT_UP, self.raiseParent)
		Damnlog('DamnTrayIcon ready.')
		self.timer = -1
		self.tooltip = DV.l('DamnVid')
		self.alternateIcons = False
		self.isDead = False
		self.icons = [DV.icon16]#, DV.icon2]
		self.iconindex = 0
		self.iconTimer = wx.Timer(self)
		self.Bind(wx.EVT_TIMER, self.onAlternateIcon, self.iconTimer)
		self.iconTimer.Start(500)
		self.updateIcon()
	def setTooltip(self, tooltip):
		self.tooltip = DamnUnicode(tooltip)
		self.updateIcon()
	def onAlternateIcon(self, event=None):
		if self.alternateIcons:
			self.iconindex = (self.iconindex + 1) % len(self.icons)
			self.updateIcon()
	def startAlternate(self):
		self.iconindex = 0
		self.updateIcon()
		self.alternateIcons = True
	def stopAlternate(self):
		self.startAlternate()
		self.alternateIcons = False
	def updateIcon(self):
		self.SetIcon(self.icons[self.iconindex], self.tooltip)
	def raiseParent(self, event=None):
		if time.time() - self.timer < 0.1:
			return
		self.timer=time.time()
		Damnlog('DamnTrayIcon raiseParent method called.')
		self.parent.trayicon = None
		self.parent.Iconize(False)
		self.parent.Show(True)
		self.parent.Raise() # Bring to front
		Damnlog('DamnTrayIcon parent shown and raised, destroying self.')
		self.destroyTimer = wx.Timer(self)
		self.Bind(wx.EVT_TIMER, self.selfDestruct, self.destroyTimer)
		self.destroyTimer.Start(5)
	def selfDestruct(self, *args):
		Damnlog('DamnTrayIcon self-destructing.')
		if self.isDead:
			return
		self.isDead = True
		self.destroyTimer.Stop()
		self.iconTimer.Stop()
		self.Destroy()
	def onMenu(self, event=None):
		menu = wx.Menu()
		show = wx.MenuItem(menu, -1, DV.l('Show DamnVid'))
		menu.AppendItem(show)
		menu.Bind(wx.EVT_MENU, self.raiseParent, show)
		if self.parent.converting == -1:
			go = wx.MenuItem(menu, -1, DV.l('Start'))
			menu.AppendItem(go)
			menu.Bind(wx.EVT_MENU, self.parent.onGo, go)
		else:
			stop = wx.MenuItem(menu, -1, DV.l('Stop'))
			menu.AppendItem(stop)
			menu.Bind(wx.EVT_MENU, self.parent.onStop, stop)
		exit = wx.MenuItem(menu, -1, DV.l('E&xit'))
		menu.AppendItem(exit)
		menu.Bind(wx.EVT_MENU, self.onClose, exit)
		self.PopupMenu(menu)
	def onClose(self, event=None):
		self.raiseParent()
		self.parent.onClose(event)
class DamnIconList(wx.ImageList): # An imagelist with dictionary-like association, not stupid IDs, and graceful failure. Can also be initialized with delay.
	def __init__(self, width=16, height=16, mask=True, initialCount=0, fail=None, initNow=False):
		self.list = {}
		self.args = (width, height, mask, initialCount)
		self.init = False
		self.fail = fail
		self.width = width
		self.height = height
		self.rawbitmaps = {}
		self.blankid = None
		self.blankbitmap = None
		if initNow:
			self.initWX()
	def initWX(self):
		wx.ImageList.__init__(self, self.args[0], self.args[1], self.args[2], self.args[3])
		self.init = True
		self.resetList(self.list)
	def add(self, bitmap, handle=None):
		Damnlog('Adding', bitmap, 'to icon list, with handle', handle)
		while handle is None or handle in self.list.keys():
			Damnlog('!Icon conflict found with handle', handle)
			handle = hashlib.md5(str(random.random()) + str(random.random())).hexdigest()
		if self.init:
			handle = DamnUnicode(handle)
			if type(bitmap) in (type(''), type(u'')):
				bitmap = wx.Bitmap(bitmap)
			self.list[handle] = self.Add(bitmap)
			self.rawbitmaps[handle] = bitmap
		else:
			self.list[handle] = bitmap
		return handle
	def getRawBitmap(self, handle):
		Damnlog('Getting raw bitmap for handle', handle)
		if type(handle) not in (type(''), type(u'')):
			for k in self.list.keys():
				if self.list[k] == handle:
					handle = k
		handle = DamnUnicode(handle)
		if handle not in self.list.keys() or handle == u'fail':
			Damnlog('Handle', handle, 'is invalid; returning default bitmap.')
			return self.blankbitmap
		return self.rawbitmaps[handle]
	def get(self, handle):
		Damnlog('Getting icon for handle', handle)
		if not self.init:
			return
		if type(handle) in (type(''), type(u'')):
			handle = DamnUnicode(handle)
			if handle == u'fail':
				Damnlog('Handle', handle, 'is fail; returning default bitmap.')
				handle = self.blankid
			elif handle in self.list.keys():
				handle = self.list[handle]
			else:
				Damnlog('Handle', handle, 'is invalid; returning default bitmap.')
				handle = self.blankid
		return handle
	def getHandle(self, img):
		Damnlog('Getting handle for image ID', img)
		if not self.init:
			return
		img = int(img)
		for i in self.list.keys():
			if self.list[i] == img:
				Damnlog('Found handle', i,'for ID', img)
				return DamnUnicode(i)
		Damnlog('Couldn\'t find handle for ID', img,'; returning fail.')
		return u'fail'
	def getBitmap(self, handle):
		Damnlog('Getting bitmap for handle', handle)
		return self.GetBitmap(self.get(handle))
	def resetList(self, items={}):
		self.list = {}
		if self.init:
			self.RemoveAll()
			if self.fail is None:
				blank = wx.EmptyBitmap(self.width, self.height)
			else:
				blank = wx.Bitmap(self.fail)
			self.blankid = self.Add(blank)
			self.blankbitmap = blank
		for i in items.keys():
			self.add(items[i], i)
DV.listicons = DamnIconList(16, 16, fail=DV.images_path + 'video.png')
def DamnGetListIcon(icon):
	return DV.listicons.get(icon)
