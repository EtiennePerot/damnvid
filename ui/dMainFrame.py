# -*- coding: utf-8 -*-
from dUI import *
from dConverter import *
from dUpdater import *
from dPrefEditor import *
from dDoneDialog import *
from dAddURLDialog import *
from dAboutDialog import *
from dReportBug import *
from dBrowser import *
from dVideoHistory import *
class DamnMainMenubar(wx.MenuBar):
	def __init__(self, parent=None):
		self.parent = parent
		wx.MenuBar.__init__(self)
		filemenu = wx.Menu()
		menu_addfile = wx.MenuItem(filemenu, -1, DV.l('&Add files...'), DV.l('Adds damn videos from local files.'))
		filemenu.AppendItem(menu_addfile)
		self.parent.Bind(wx.EVT_MENU, self.parent.onAddFile, menu_addfile)
		menu_addurl = wx.MenuItem(filemenu, -1, DV.l('Add &URL...'), DV.l('Adds a damn video from a URL.'))
		filemenu.AppendItem(menu_addurl)
		self.parent.Bind(wx.EVT_MENU, self.parent.onAddURL, menu_addurl)
		menu_history = wx.MenuItem(filemenu, -1, DV.l('Video &history...'), DV.l('Opens DamnVid\'s video history.'))
		filemenu.AppendItem(menu_history)
		self.parent.Bind(wx.EVT_MENU, self.parent.onOpenHistory, menu_history)
		filemenu.AppendSeparator()
		filemenu.Append(wx.ID_EXIT, DV.l('E&xit'), DV.l('Terminates DamnVid.'))
		self.parent.Bind(wx.EVT_MENU, self.parent.onExit, id=wx.ID_EXIT)
		vidmenu = wx.Menu()
		menu_letsgo = wx.MenuItem(vidmenu, -1, DV.l('Start'), DV.l('Processes all the videos in the list.'))
		vidmenu.AppendItem(menu_letsgo)
		self.parent.Bind(wx.EVT_MENU, self.parent.onGo, menu_letsgo)
		vidmenu.AppendSeparator()
		self.parent.prefmenuitem = vidmenu.Append(wx.ID_PREFERENCES, DV.l('Preferences'), DV.l('Opens DamnVid\'s preferences, allowing you to customize its settings.'))
		self.parent.Bind(wx.EVT_MENU, self.parent.onPrefs, id=wx.ID_PREFERENCES)
		halpmenu = wx.Menu()
		halpmenu.Append(wx.ID_HELP, DV.l('&Help'), DV.l('Opens DamnVid\'s help.'))
		self.parent.Bind(wx.EVT_MENU, self.parent.onHalp, id=wx.ID_HELP)
		menu_reportbug = wx.MenuItem(halpmenu, -1, DV.l('Report a bug'), DV.l('Submit a new bug report.'))
		halpmenu.AppendItem(menu_reportbug)
		self.parent.Bind(wx.EVT_MENU, self.parent.onReportBug, menu_reportbug)
		menu_checkupdates = wx.MenuItem(halpmenu, -1, DV.l('Check for updates...'), DV.l('Checks if a new version of DamnVid is available.'))
		halpmenu.AppendItem(menu_checkupdates)
		self.parent.Bind(wx.EVT_MENU, self.parent.onCheckUpdates, menu_checkupdates)
		halpmenu.AppendSeparator()
		halpmenu.Append(wx.ID_ABOUT, DV.l('&About DamnVid ') + DV.version + '...', DV.l('Displays information about DamnVid.'))
		self.parent.Bind(wx.EVT_MENU, self.parent.onAboutDV, id=wx.ID_ABOUT)
		self.Append(filemenu, DV.l('&File'))
		self.Append(vidmenu, DV.l('&DamnVid'))
		self.Append(halpmenu, DV.l('&Help'))
class DamnMainFrame(DamnFrame): # The main window
	def __init__(self, parent, id, title):
		Damnlog('DamnMainFrame GUI building starting.')
		DamnFrame.__init__(self, parent, wx.ID_ANY, title, size=(780, 580), style=wx.DEFAULT_FRAME_STYLE)
		self.CreateStatusBar()
		self.SetMenuBar(DamnMainMenubar(self))
		Damnlog('DamnMainFrame menu bar is up.')
		vbox = wx.BoxSizer(wx.VERTICAL)
		self.SetSizer(vbox)
		#vbox.Add((0,DV.border_padding)) #Actually, do NOT add a padding there, it looks better when stuck on the edge
		panel = wx.Panel(self, -1)
		vbox.Add(panel, 1, wx.EXPAND)
		grid = wx.FlexGridSizer(2, 2, 8, 8)
		panel1 = wx.Panel(panel, -1)
		grid.Add(panel1, 1, wx.EXPAND)
		panel2 = wx.Panel(panel, -1)
		grid.Add(panel2, 0, wx.EXPAND)
		panel3 = wx.Panel(panel, -1)
		grid.Add(panel3, 0, wx.EXPAND)
		panel4 = wx.Panel(panel, -1)
		grid.Add(panel4, 0, wx.EXPAND)
		panel.SetSizer(grid)
		hbox1 = wx.BoxSizer(wx.HORIZONTAL)
		#hbox1.Add((DV.border_padding,0)) Ditto
		panel1.SetSizer(hbox1)
		self.list = DamnList(panel1, window=self)
		self.list.InsertColumn(ID_COL_VIDNAME, DV.l('Video name'))
		self.list.SetColumnWidth(ID_COL_VIDNAME, width=180)
		self.list.InsertColumn(ID_COL_VIDPROFILE, DV.l('Encoding profile'))
		self.list.SetColumnWidth(ID_COL_VIDPROFILE, width=120)
		self.list.InsertColumn(ID_COL_VIDSTAT, DV.l('Status'))
		self.list.SetColumnWidth(ID_COL_VIDSTAT, width=120)
		self.list.InsertColumn(ID_COL_VIDPATH, DV.l('Source'))
		self.list.SetColumnWidth(ID_COL_VIDPATH, wx.LIST_AUTOSIZE)
		self.list.Bind(wx.EVT_KEY_DOWN, self.onListKeyDown)
		self.list.Bind(wx.EVT_LIST_ITEM_SELECTED, self.onListSelect)
		self.list.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.onListSelect)
		DV.listicons.initWX()
		self.list.AssignImageList(DV.listicons, wx.IMAGE_LIST_SMALL)
		self.list.SetDropTarget(DamnDropHandler(self))
		self.list.Bind(wx.EVT_RIGHT_DOWN, self.list.onRightClick)
		hbox1.Add(self.list, 1, wx.EXPAND)
		Damnlog('DamnMainFrame MainList is up.')
		vboxwrap2 = wx.BoxSizer(wx.HORIZONTAL)
		sizer2 = wx.BoxSizer(wx.VERTICAL)
		vboxwrap2.Add(sizer2)
		vboxwrap2.Add((DV.border_padding, 0))
		sizer2.Add((0, DV.border_padding))
		panel2.SetSizer(vboxwrap2)
		self.droptarget = wx.animate.GIFAnimationCtrl(panel2, -1, DV.images_path + 'droptarget.gif')
		self.droptarget.Bind(wx.EVT_LEFT_UP, self.onDropTargetClick)
		sizer2.Add(self.droptarget, 0, wx.ALIGN_CENTER)
		self.droptarget.SetDropTarget(DamnDropHandler(self))
		# Extra forced gap here
		sizer2.Add((0, DV.control_vgap + 4))
		self.addByFile = wx.Button(panel2, -1, DV.l('Add Files'))
		sizer2.Add(self.addByFile, 0, wx.ALIGN_CENTER)
		sizer2.Add((0, DV.control_vgap))
		self.Bind(wx.EVT_BUTTON, self.onAddFile, self.addByFile)
		self.addByURL = wx.Button(panel2, -1, DV.l('Add URL'))
		sizer2.Add(self.addByURL, 0, wx.ALIGN_CENTER)
		sizer2.Add((0, DV.control_vgap))
		self.Bind(wx.EVT_BUTTON, self.onAddURL, self.addByURL)
		self.btnSearch = wx.Button(panel2, -1, DV.l('Search...'))
		sizer2.Add(self.btnSearch, 0, wx.ALIGN_CENTER)
		sizer2.Add((0, DV.control_vgap))
		self.Bind(wx.EVT_BUTTON, self.onSearch, self.btnSearch)
		self.btnRename = wx.Button(panel2, -1, DV.l('Rename'))
		sizer2.Add(self.btnRename, 0, wx.ALIGN_CENTER)
		sizer2.Add((0, DV.control_vgap))
		self.Bind(wx.EVT_BUTTON, self.onRename, self.btnRename)
		self.profilepanel = wx.Panel(panel2, -1)
		profilepanelsizer = wx.BoxSizer(wx.VERTICAL)
		self.profilepanel.SetSizer(profilepanelsizer)
		profilepanelsizer.Add(wx.StaticText(self.profilepanel, -1, DV.l('Profile:')), 0, wx.ALIGN_CENTER)
		self.profiledropdown = wx.Choice(self.profilepanel, -1, choices=[DV.l('(None)')])
		profilepanelsizer.Add((0, DV.control_vgap))
		profilepanelsizer.Add(self.profiledropdown, 0, wx.ALIGN_CENTER)
		sizer2.Add(self.profilepanel)
		tmplistheight = self.profiledropdown.GetSizeTuple()[1]
		self.profilepanel.Hide()
		sizer2.Add((0, DV.control_vgap))
		self.btnMoveUp = wx.Button(panel2, -1, DV.l('Move up'))
		sizer2.Add(self.btnMoveUp, 0, wx.ALIGN_CENTER)
		sizer2.Add((0, DV.control_vgap))
		self.Bind(wx.EVT_BUTTON, self.onMoveUp, self.btnMoveUp)
		self.btnMoveDown = wx.Button(panel2, -1, DV.l('Move down'))
		sizer2.Add(self.btnMoveDown, 0, wx.ALIGN_CENTER)
		sizer2.Add((0, DV.control_vgap))
		self.Bind(wx.EVT_BUTTON, self.onMoveDown, self.btnMoveDown)
		self.deletebutton = wx.Button(panel2, -1, DV.l('Remove'))
		sizer2.Add(self.deletebutton, 0, wx.ALIGN_CENTER)
		sizer2.Add((0, DV.control_vgap))
		self.Bind(wx.EVT_BUTTON, self.onDelete, self.deletebutton)
		self.gobutton1 = wx.Button(panel2, -1, DV.l('Start'))
		sizer2.Add(self.gobutton1, 0, wx.ALIGN_CENTER)
		sizer2.Add((0, DV.border_padding))
		buttonwidth = sizer2.GetMinSizeTuple()[0]
		self.Bind(wx.EVT_BUTTON, self.onGo, self.gobutton1)
		hbox3 = wx.BoxSizer(wx.HORIZONTAL)
		hbox3.Add((DV.border_padding, 0))
		panel3.SetSizer(hbox3)
		hbox3.Add(wx.StaticText(panel3, -1, DV.l('Current video: ')), 0, wx.ALIGN_CENTER_VERTICAL)
		self.gauge1 = wx.Gauge(panel3, -1)
		hbox3.Add(self.gauge1, 1, wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)
		#self.gobutton2=wx.Button(bottompanel,-1,'Let\'s go!')
		#self.Bind(wx.EVT_BUTTON,self.onGo,self.gobutton2)
		#grid.Add(wx.StaticText(bottompanel,-1,''),0)
		#grid.Add(self.gobutton2,0)
		#grid.Add(wx.StaticText(bottompanel,-1,'Total progress:'),0)
		#self.gauge2=wx.Gauge(bottompanel,-1)
		#grid.Add(self.gauge2,1,wx.EXPAND)
		hboxwrapper4 = wx.BoxSizer(wx.HORIZONTAL)
		hbox4 = wx.BoxSizer(wx.VERTICAL)
		hboxwrapper4.Add(hbox4)
		hboxwrapper4.Add((0, DV.border_padding))
		panel4.SetSizer(hboxwrapper4)
		self.stopbutton = wx.Button(panel4, -1, DV.l('Stop'))
		for button in (self.addByFile, self.addByURL, self.btnRename, self.btnMoveUp, self.btnMoveDown, self.deletebutton, self.gobutton1, self.stopbutton, self.btnSearch):
			button.SetMinSize((buttonwidth, button.GetSizeTuple()[1]))
		self.gauge1.SetMaxSize((-1, self.stopbutton.GetSizeTuple()[1]))
		self.profiledropdown.SetMinSize((buttonwidth, tmplistheight))
		self.profiledropdown.Bind(wx.EVT_CHOICE, self.onChangeProfileDropdown)
		self.profilepanel.Show()
		hbox4.Add(self.stopbutton)
		hbox4.Add((0, DV.border_padding))
		#vbox.Add((0,DV.border_padding)) Ditto
		self.stopbutton.Disable()
		self.Bind(wx.EVT_BUTTON, self.onStop, self.stopbutton)
		grid.AddGrowableRow(0, 1)
		grid.AddGrowableCol(0, 1)
		self.Bind(wx.EVT_CLOSE, self.onClose, self)
		self.Bind(wx.EVT_SIZE, self.onResize, self)
		self.Bind(wx.EVT_ICONIZE, self.onMinimize)
		self.Bind(DV.evt_prog, self.onProgress)
		self.Bind(DV.evt_load, self.onLoading)
		Damnlog('DamnMainFrame: All GUI is up.')
		self.clipboardtimer = wx.Timer(self, -1)
		self.clipboardtimer.Start(1000)
		self.Bind(wx.EVT_TIMER, self.onClipboardTimer, self.clipboardtimer)
		Damnlog('DaminMainFrame: Clipboard timer started.')
		DV.icon = wx.Icon(DV.images_path + 'icon.ico', wx.BITMAP_TYPE_ICO)
		#DV.icon2 = wx.Icon(DV.images_path + 'icon-alt.ico', wx.BITMAP_TYPE_ICO)
		DV.icon16 = wx.Icon(DV.images_path + 'icon16.ico', wx.BITMAP_TYPE_ICO)
		self.SetIcon(DV.icon)
		Damnlog('DamnMainFrame: init stage 1 done.')
	def init2(self):
		Damnlog('Starting DamnMainFrame init stage 2.')
		if os.path.exists(DV.conf_file_directory + 'lastversion.damnvid'):
			lastversion = DamnOpenFile(DV.conf_file_directory + 'lastversion.damnvid', 'r')
			dvversion = lastversion.readline().strip()
			lastversion.close()
			del lastversion
			Damnlog('Version file found; version number read:',dvversion)
		else:
			dvversion = 'old' # This is not just an arbitrary erroneous value, it's actually handy in the concatenation on the wx.FileDialog line below
			Damnlog('No version file found.')
		Damnlog('Read version:',dvversion,';running version:',DV.version)
		if dvversion != DV.version: # Just updated to new version, ask what to do about the preferences
			#dlg = wx.MessageDialog(self, DV.l('DamnVid was updated to ') + DV.version + '.\n' + DV.l('locale:damnvid-updated-export-prefs'), DV.l('DamnVid was successfully updated'), wx.YES | wx.NO | wx.ICON_QUESTION)
			tmpprefs = DamnVidPrefs()
			try:
				checkupdates = tmpprefs.get('CheckForUpdates')
				locale = tmpprefs.get('locale')
			except:
				pass
			Damnlog('Check for updates preference is',checkupdates)
			if False: #dlg.ShowModal() == wx.ID_YES:
				dlg.Destroy()
				dlg = wx.FileDialog(self, DV.l('Where do you want to export DamnVid\'s configuration?'), tmpprefs.get('lastprefdir'), 'DamnVid-' + dvversion + '-configuration.ini', DV.l('locale:browse-ini-files'), wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
				if dlg.ShowModal() == wx.ID_OK:
					path = dlg.GetPath()
					f = DamnOpenFile(path, 'w')
					tmpprefs.ini.write(f)
					f.close()
				dlg.Destroy()
			else:
				pass
			# Now, overwrite the preferences!
			del tmpprefs
			os.remove(DV.conf_file)
			shutil.copyfile(DV.curdir + 'conf' + DV.sep + 'conf.ini', DV.conf_file)
			lastversion = DamnOpenFile(DV.conf_file_directory + 'lastversion.damnvid', 'w')
			lastversion.write(DV.version.encode('utf8'))
			lastversion.close()
			del lastversion
			tmpprefs = DamnVidPrefs()
			try:
				tmpprefs.set('CheckForUpdates', checkupdates)
				tmpprefs.set('locale', locale)
			except:
				pass
			tmpprefs.save()
			del tmpprefs
		Damnlog('Local version check done, initializing DamnMainFrame properties.')
		self.videos = []
		self.clippedvideos = []
		self.resultlist = []
		self.thisbatch = 0
		self.thisvideo = []
		self.meta = {}
		DV.prefs = DamnVidPrefs()
		self.converting = -1
		self.isclosing = False
		self.searchopen = False
		self.addurl = None
		self.loadingvisible = 0
		self.trayicon = None
		self.historyDialog = None
		self.onListSelect()
		Damnlog('DamnMainFrame properties OK, first run?',DV.first_run)
		if DV.first_run:
			if DV.os == 'mac':
				DV.prefs.set('CheckForUpdates', 'True')
				Damnlog('Skipping asking user for updates because this is a Mac and Mac users don\'t want to configure stuff.')
			else:
				dlg = wx.MessageDialog(self, DV.l('Welcome to DamnVid ') + DV.version + '!\n' + DV.l('Would you like DamnVid to check for updates every time it starts?'), DV.l('Welcome to DamnVid ') + DV.version + '!', wx.YES | wx.NO | wx.ICON_QUESTION)
				if dlg.ShowModal() == wx.ID_YES:
					DV.prefs.set('CheckForUpdates', 'True')
				else:
					DV.prefs.set('CheckForUpdates', 'False')
		if DV.prefs.get('CheckForUpdates') == 'True':
			Damnlog('DamnMainFrame checking for updates.')
			self.onCheckUpdates(None)
		self.SetStatusText(DV.l('DamnVid ready.'))
		windowpolicy = DV.prefs.get('windowpolicy')
		if not len(windowpolicy) or windowpolicy=='center':
			Damnlog('Window policy is centering.')
			self.Center()
		elif windowpolicy=='remember':
			Damnlog('Window policy is remember; trying to load saved window geometry.')
			allstuff=(
				DV.prefs.gets('damnvid-mainwindow','lastx'), DV.prefs.gets('damnvid-mainwindow','lasty'),
				DV.prefs.gets('damnvid-mainwindow','lastw'), DV.prefs.gets('damnvid-mainwindow','lasth'),
				DV.prefs.gets('damnvid-mainwindow','lastresw'), DV.prefs.gets('damnvid-mainwindow','lastresh')
			)
			Damnlog('Old window geometry information:',allstuff)
			allstuff2=[]
			for i in allstuff:
				try:
					allstuff2.append(int(i))
				except:
					allstuff2.append(-1)
			if -1 in allstuff2:
				Damnlog('Invalid information in old window geometry information; giving up on restoring window geometry.')
			else:
				try:
					screen = wx.Display().GetGeometry()[2:]
					if allstuff2[4] != screen[0] or allstuff2[5]!= screen[1]:
						Damnlog('Resolution information is different:',allstuff2[4:5],'vs',screen,'(current); giving up on restoring window geometry.')
					elif allstuff2[0] < 0 or allstuff2[0] + allstuff2[2] >= allstuff2[4] or allstuff2[1] < 0 or allstuff2[1] + allstuff2[3] >= allstuff2[5]:
						Damnlog('Window position is out of bounds; giving up.')
					else:
						Damnlog('All window geometry tests passed, attempting to restore window geometry.')
						try:
							self.SetSizeWH(allstuff2[2],allstuff2[3])
							self.MoveXY(allstuff2[0],allstuff2[1])
							Damnlog('Window geometry restored successfully.')
						except:
							Damnlog('Window manager refused to change window geometry.')
				except:
					Damnlog('Could not get screen resolution; giving up on restoring window geometry.')
		else:
			Damnlog('Window policy is',windowpolicy,'; doing nothing.')
		self.updateHistory()
		Damnlog('DamnMainFrame: Main window all ready,')
	def onMinimize(self, event):
		if DV.os == 'posix':
			return # Do not do anything on Linux, let the window manager handle it
		Damnlog('DamnMainFrame iconize event fired. Is being minimized?', event.Iconized())
		if self.isclosing:
			Damnlog('DamnMainFrame being closed, not interfering.')
			return
		if not event.Iconized():
			Damnlog('DamnMainFrame being restored, doing nothing.')
			return
		if DV.prefs.get('minimizetotray')=='True':
			Damnlog('Minimize to tray preference is True, creating tray icon.')
			self.trayicon = DamnTrayIcon(self)
		else:
			Damnlog('Minimize to tray preference is False, doing nothing.')
	def onExit(self, event):
		self.Close(True)
	def onListSelect(self, event=None):
		sel = self.list.getAllSelectedItems()
		gotstuff = bool(len(sel))
		count = self.list.GetItemCount()
		self.btnRename.Enable(len(sel) == 1)
		self.profiledropdown.Enable(bool(count))
		if not count:
			self.profiledropdown.SetItems([DV.l('(None)')])
		videosAffected = range(count)
		if gotstuff:
			videosAffected = sel
			self.deletebutton.SetLabel(DV.l('Remove'))
			self.deletebutton.Enable(self.converting not in sel)
			self.btnMoveUp.Enable(sel[0])
			self.btnMoveDown.Enable(sel[-1] != self.list.GetItemCount() - 1)
		else:
			self.deletebutton.SetLabel(DV.l('Remove all'))
			self.deletebutton.Enable(self.converting == -1)
			self.btnMoveUp.Disable()
			self.btnMoveDown.Disable()
		if len(videosAffected):
			choices = []
			uniprofile = int(self.meta[self.videos[videosAffected[0]]]['profile'])
			for i in videosAffected:
				if int(self.meta[self.videos[i]]['profile']) != uniprofile:
					uniprofile = -2
			for p in range(-1, DV.prefs.profiles):
				choices.append(DV.l(DV.prefs.getp(p, 'name'), warn=False))
			if uniprofile == -2:
				choices.insert(0, DV.l('(Multiple)'))
			self.profiledropdown.SetItems(choices)
			if uniprofile == -2:
				self.profiledropdown.SetSelection(0)
			else:
				self.profiledropdown.SetSelection(uniprofile + 1)
	def onListKeyDown(self, event):
		keycode = event.GetKeyCode()
		if (keycode == wx.WXK_BACK or keycode == wx.WXK_DELETE) and self.list.GetSelectedItemCount():
			self.onDelSelection(event)
		elif (keycode == wx.WXK_F2 or keycode == wx.WXK_NUMPAD_F2) and self.list.GetSelectedItemCount() == 1:
			self.onRename(event)
	def onAddFile(self, event):
		d = os.getcwd()
		if os.path.exists(DV.prefs.get('LastFileDir')):
			if os.path.isdir(DV.prefs.get('LastFileDir')):
				d = DV.prefs.get('LastFileDir')
		elif os.path.exists(DV.prefs.expandPath('?DAMNVID_MY_VIDEOS?')):
			if os.path.isdir(DV.prefs.expandPath('?DAMNVID_MY_VIDEOS?')):
				d = DV.prefs.expandPath('?DAMNVID_MY_VIDEOS?')
		dlg = wx.FileDialog(self, DV.l('Choose a damn video.'), d, '', DV.l('locale:browse-video-files'), wx.OPEN | wx.FD_MULTIPLE)
		dlg.SetIcon(DV.icon)
		if dlg.ShowModal() == wx.ID_OK:
			vids = dlg.GetPaths()
			DV.prefs.set('LastFileDir', os.path.dirname(vids[0]))
			DV.prefs.save()
			self.addVid(vids)
		dlg.Destroy()
	def onOpenHistory(self, event=None):
		Damnlog('onOpenHistory event fired:', event)
		if self.historyDialog is None:
			self.historyDialog = DamnHistoryViewer(self)
		self.historyDialog.Show()
	def onCloseHistory(self, event=None):
		Damnlog('onCloseHistory event fired:', event)
		self.historyDialog = None
	def onAddURL(self, event=None):
		Damnlog('onAddURL event fired:',event)
		default = ''
		try:
			if not wx.TheClipboard.IsOpened():
				if wx.TheClipboard.Open():
					dataobject = wx.TextDataObject()
					wx.TheClipboard.GetData(dataobject)
					default = dataobject.GetText()
					wx.TheClipboard.Close()
					Damnlog('Text scavenged from clipboard:',default)
					if not self.validURI(default):
						default = '' # Only set that as default text if the clipboard's text content is not a URL
		except:
			default = ''
		try:
			wx.TheClipboard.Close() # In case there's been an error before the clipboard could be closed, try to close it now
		except:
			pass # There's probably wasn't any error, just pass
		self.addurl = DamnAddURLDialog(self, default)
		self.addurl.SetIcon(DV.icon)
		self.addurl.ShowModal()
		try:
			self.addurl.Destroy()
		except:
			pass # The addurl destroys itself, supposedly, and doing it again sometimes (sometimes!) generates errors.
		self.addurl = None
	def validURI(self, uri):
		if REGEX_HTTP_GENERIC.match(uri):
			for i in DamnIterModules(False):
				if i['class'](uri).validURI():
					return 'Video site'
			return 'Online video' # Not necessarily true, but ffmpeg will tell
		elif os.path.exists(uri):
			return 'Local file'
		return None
	def getVidName(self, uri):
		try:
			html = DamnURLOpen(uri[3:])
			for i in html:
				res = REGEX_HTTP_GENERIC_TITLE_EXTRACT.search(i)
				if res:
					return DamnHtmlEntities(res.group(1)).strip()
		except:
			pass # Can't grab this? Return Unknown title
		return DV.l('Unknown title')
	def onDropTargetClick(self, event):
		dlg = wx.MessageDialog(self, DV.l('This is a droptarget: You may drop video files and folders here (or in the big list as well).'), DV.l('DamnVid Droptarget'), wx.ICON_INFORMATION)
		dlg.SetIcon(DV.icon)
		dlg.ShowModal()
		dlg.Destroy()
	def toggleLoading(self, show):
		isvisible = self.loadingvisible > 0
		self.loadingvisible = max((0, self.loadingvisible + int(show) * 2 - 1))
		if (isvisible and not self.loadingvisible) or (not isvisible and self.loadingvisible):
			DV.postEvent(self, DamnLoadingEvent(DV.evt_loading, -1, {'show':bool(self.loadingvisible)}))
	def onLoading(self, event):
		info = event.GetInfo()
		if info.has_key('show'):
			if info['show']:
				self.droptarget.LoadFile(DV.images_path + 'droptargetloading.gif')
				self.droptarget.Play()
			else:
				self.droptarget.Stop()
				self.droptarget.LoadFile(DV.images_path + 'droptarget.gif')
		if info.has_key('status'):
			self.SetStatusText(info['status'])
		if info.has_key('dialog'):
			dlg = wx.MessageDialog(self, info['dialog'][1], info['dialog'][0], info['dialog'][2])
			dlg.SetIcon(DV.icon)
			dlg.ShowModal()
			dlg.Destroy()
		if info.has_key('meta'):
			self.addValid(info['meta'])
		if info.has_key('go') and self.converting == -1:
			if info['go']:
				self.onGo()
		if info.has_key('updateinfo'):
			if info['updateinfo'].has_key('verbose'):
				verbose = info['updateinfo']['verbose']
			else:
				verbose = True
			if info['updateinfo'].has_key('main'):
				if info['updateinfo']['main'] is not None:
					msg = None
					if DamnVersionCompare(info['updateinfo']['main'], DV.version) == 1 and type(info['updateinfo']['main']) is type(''):
						if DV.os != 'posix':
							dlg = wx.MessageDialog(self, DV.l('A new version (') + info['updateinfo']['main'] + DV.l(') is available! You are running DamnVid ') + DV.version + '.\n' + DV.l('Want to go to the download page and download the update?'), DV.l('Update available!'), wx.YES | wx.NO | wx.YES_DEFAULT | wx.ICON_INFORMATION)
							dlg.SetIcon(DV.icon)
							if dlg.ShowModal() == wx.ID_YES:
								webbrowser.open(DV.url_download, 2)
							dlg.Destroy()
					elif verbose and type(info['updateinfo']['main']) is type(''):
						if DV.version != info['updateinfo']['main']:
							versionwarning = DV.l(' However, your version (') + DV.version + DV.l(') seems different than the latest version available online. Where would you get that?')
						else:
							versionwarning = ''
						msg = (DV.l('DamnVid is up-to-date.'), DV.l('DamnVid is up-to-date! The latest version is ') + info['updateinfo']['main'] + '.' + versionwarning, wx.ICON_INFORMATION)
					elif verbose:
						msg = (DV.l('Error!'), DV.l('There was a problem while checking for updates. You are running DamnVid ') + DV.version + '.\n' + DV.l('Make sure you are connected to the Internet, and that no firewall is blocking DamnVid.'), wx.ICON_INFORMATION)
					if msg is not None:
						dlg = wx.MessageDialog(self, msg[1], msg[0], msg[2])
						dlg.SetIcon(DV.icon)
						dlg.ShowModal()
						dlg.Destroy()
			if info['updateinfo'].has_key('modules'):
				msg = []
				for i in info['updateinfo']['modules'].iterkeys():
					if type(info['updateinfo']['modules'][i]) is type(()):
						msg.append((True, DV.modules[i]['title'] + DV.l(' was updated to version ') + info['updateinfo']['modules'][i][0] + '.'))
					elif type(info['updateinfo']['modules'][i]) is type('') and verbose:
						if info['updateinfo']['modules'][i] == 'error':
							msg.append((False, DV.modules[i]['title'] + DV.l(' is up-to-date (version ') + DV.modules[i]['version'] + ').'))
				if len(msg):
					msgs = []
					for i in msg:
						if i[0]:
							msgs.append(i[1])
					if not len(msg) and verbose:
						msgs = msg
					if len(msgs):
						msg = DV.l('DamnVid also checked for updates to its modules.') + '\n'
						for i in msgs:
							msg += '\n' + i
						dlg = wx.MessageDialog(self, msg, DV.l('Module updates'), wx.ICON_INFORMATION)
						dlg.SetIcon(DV.icon)
						dlg.ShowModal()
						dlg.Destroy()
	def updateHistory(self):
		if self.historyDialog is not None:
			self.historyDialog.update()
	def onAddHistoryVideo(self, uri, event=None):
		Damnlog('History video add event fired:', event,'with URI', uri)
		self.addVid([uri], DV.prefs.get('autoconvert') == 'True')
	def addVid(self, uris, thengo=False):
		DV.videoLoader(self, uris, thengo).start()
	def addTohistory(self, uri, title, icon=None):
		uri = DamnUnicode(uri)
		title = DamnUnicode(title)
		icon = DamnUnicode(icon)
		Damnlog('Adding video to history:', uri, 'with title', title, 'and icon', icon)
		history = DV.prefs.geta('damnvid-videohistory', 'videos')
		histsize = int(DV.prefs.get('videohistorysize'))
		if not histsize:
			Damnlog('Histsize is zero, not touching anything.')
			return
		for i in history:
			tempvideo = i.split(DV.history_split)
			if len(tempvideo) != 3:
				Damnlog('Invalid entry in history:', i)
				continue
			if tempvideo[0].strip().lower() == uri.strip().lower():
				Damnlog('URI',uri,'is already in history, not adding it to history again.')
				return
		history.reverse()
		while len(history) >= histsize:
			history = history[1:]
		history.append(DV.history_split.join([uri,title,icon]))
		history.reverse()
		DV.prefs.seta('damnvid-videohistory','videos',history)
		Damnlog('Video added successfully, rebuilding history menu.')
		self.updateHistory()
	def addValid(self, meta):
		Damnlog('Adding video to DamnList with meta:',meta)
		if type(meta['icon']) in (type(''), type(u'')):
			meta['icon'] = DamnGetListIcon(meta['icon'])
		self.addTohistory(meta['original'], meta['name'], DV.listicons.getHandle(meta['icon']))
		curvid = len(self.videos)
		self.list.InsertStringItem(curvid, meta['name'])
		self.list.SetStringItem(curvid, ID_COL_VIDPROFILE, DV.l(DV.prefs.getp(meta['profile'], 'name')))
		self.list.SetStringItem(curvid, ID_COL_VIDPATH, meta['dirname'])
		self.list.SetStringItem(curvid, ID_COL_VIDSTAT, meta['status'])
		self.list.SetItemImage(curvid, meta['icon'], meta['icon'])
		self.videos.append(meta['uri'])
		self.meta[meta['uri']] = meta
		self.SetStatusText(DV.l('Added ') + meta['name'] + '.')
		if self.addurl is not None:
			self.addurl.update(meta['original'], meta['name'], meta['icon'])
		self.onListSelect()
	def onProgress(self, event):
		info = event.GetInfo()
		if info.has_key('progress'):
			self.gauge1.SetValue(info['progress'])
		if info.has_key('statustext'):
			self.SetStatusText(info['statustext'])
		if info.has_key('status'):
			self.list.SetStringItem(self.converting, ID_COL_VIDSTAT, info['status'])
			if self.trayicon is not None:
				self.trayicon.setTooltip(DamnUnicode(self.meta[self.videos[self.converting]]['name'])+u': '+info['status'])
		if info.has_key('dialog'):
			dlg = wx.MessageDialog(self, info['dialog'][0], info['dialog'][1], info['dialog'][2])
			dlg.SetIcon(DV.icon)
			dlg.ShowModal()
			dlg.Destroy()
		if info.has_key('go'):
			self.go(info['go'])
	def go(self, aborted=False):
		self.converting = -1
		for i in range(len(self.videos)):
			if self.videos[i] not in self.thisvideo and self.meta[self.videos[i]]['status'] != DV.l('Success!'):
				self.converting = i
				break
		if self.converting != -1 and not aborted: # Let's go for the actual conversion...
			self.meta[self.videos[self.converting]]['status'] = DV.l('In progress...')
			self.list.SetStringItem(self.converting, ID_COL_VIDSTAT, DV.l('In progress...'))
			self.thisbatch = self.thisbatch + 1
			self.thread = DamnConverter(parent=self)
			if self.trayicon is not None:
				self.trayicon.startAlternate()
			self.thread.start()
		else:
			if self.trayicon is not None:
				self.trayicon.stopAlternate()
			if not self.isclosing:
				self.SetStatusText(DV.l('DamnVid, waiting for instructions.'))
				dlg = DamnDoneDialog(content=self.resultlist, aborted=aborted, main=self)
				dlg.SetIcon(DV.icon)
				dlg.ShowModal()
				dlg.Destroy()
				self.converting = -1
				self.stopbutton.Disable()
				self.gobutton1.Enable()
				self.gauge1.SetValue(0.0)
		self.onListSelect()
	def onGo(self, event=None):
		if not len(self.videos):
			dlg = wx.MessageDialog(None, DV.l('Put some videos in the list first!'), DV.l('No videos!'), wx.ICON_EXCLAMATION | wx.OK)
			dlg.SetIcon(DV.icon)
			dlg.ShowModal()
			dlg.Destroy()
		elif self.converting != -1:
			dlg = wx.MessageDialog(None, DV.l('DamnVid is already converting!'), DV.l('Already converting!'), wx.ICON_EXCLAMATION | wx.OK)
			dlg.SetIcon(DV.icon)
			dlg.ShowModal()
			dlg.Destroy()
		else:
			success = 0
			for i in self.videos:
				if self.meta[i]['status'] == DV.l('Success!'):
					success = success + 1
			if success == len(self.videos):
				dlg = wx.MessageDialog(None, DV.l('All videos in the list have already been processed!'), DV.l('Already done'), wx.OK | wx.ICON_INFORMATION)
				dlg.SetIcon(DV.icon)
				dlg.ShowModal()
				dlg.Destroy()
			else:
				self.thisbatch = 0
				self.thisvideo = []
				self.resultlist = []
				self.stopbutton.Enable()
				self.gobutton1.Disable()
				self.go()
		self.onListSelect()
	def onStop(self, event):
		self.thread.abortProcess()
	def onRename(self, event):
		item = self.list.getAllSelectedItems()
		if len(item) > 1:
			dlg = wx.MessageDialog(None, DV.l('You can only rename one video at a time.'), DV.l('Multiple videos selected.'), wx.ICON_EXCLAMATION | wx.OK)
			dlg.SetIcon(DV.icon)
			dlg.ShowModal()
			dlg.Destroy()
		elif not len(item):
			dlg = wx.MessageDialog(None, DV.l('Select a video in order to rename it.'), DV.l('No videos selected'), wx.ICON_EXCLAMATION | wx.OK)
			dlg.SetIcon(DV.icon)
			dlg.ShowModal()
			dlg.Destroy()
		else:
			item = item[0]
			dlg = wx.TextEntryDialog(None, DV.l('Enter the new name for "') + self.meta[self.videos[item]]['name'] + '".', DV.l('Rename'), self.meta[self.videos[item]]['name'])
			dlg.SetIcon(DV.icon)
			dlg.ShowModal()
			newname = dlg.GetValue()
			self.meta[self.videos[item]]['name'] = newname
			self.list.SetStringItem(item, ID_COL_VIDNAME, newname)
			dlg.Destroy()
			history = DV.prefs.geta('damnvid-videohistory','videos')
			for i in range(len(history)):
				video = history[i].split(DV.history_split)
				if len(video) != 3:
					continue
				if video[0] == self.meta[self.videos[item]]['original']:
					video[1] = newname
					history[i] = DV.history_split.join(video)
			DV.prefs.seta('damnvid-videohistory','videos',history)
			DV.prefs.save()
			self.updateHistory()
	def onSearch(self, event):
		if not self.searchopen:
			self.searchopen = True
			self.searchdialog = DamnVidBrowser(self)
			self.searchdialog.Show()
		else:
			self.searchdialog.Raise()
	def invertVids(self, i1, i2):
		tmp = self.videos[i1]
		self.videos[i1] = self.videos[i2]
		self.videos[i2] = tmp
		tmp = self.list.IsSelected(i2)
		self.list.Select(i2, on=self.list.IsSelected(i1))
		self.list.Select(i1, on=tmp)
		self.list.invertItems(i1, i2)
		if i1 == self.converting:
			self.converting = i2
		elif i2 == self.converting:
			self.converting = i1
		self.onListSelect()
	def onMoveUp(self, event):
		items = self.list.getAllSelectedItems()
		if len(items):
			if items[0]:
				for i in items:
					self.invertVids(i, i - 1)
			else:
				dlg = wx.MessageDialog(None, DV.l('You\'ve selected the first item in the list, which cannot be moved further up!'), DV.l('Invalid selection'), wx.OK | wx.ICON_EXCLAMATION)
				dlg.SetIcon(DV.icon)
				dlg.ShowModal()
				dlg.Destroy()
		else:
			dlg = wx.MessageDialog(None, DV.l('Select some videos in the list first.'), DV.l('No videos selected!'), wx.OK | wx.ICON_EXCLAMATION)
			dlg.SetIcon(DV.icon)
			dlg.ShowModal()
			dlg.Destroy()
		self.onListSelect()
	def onMoveDown(self, event):
		items = self.list.getAllSelectedItems()
		if len(items):
			if items[-1] < self.list.GetItemCount() - 1:
				for i in reversed(self.list.getAllSelectedItems()):
					self.invertVids(i, i + 1)
			else:
				dlg = wx.MessageDialog(None, DV.l('You\'ve selected the last item in the list, which cannot be moved further down!'), DV.l('Invalid selection'), wx.OK | wx.ICON_EXCLAMATION)
				dlg.SetIcon(DV.icon)
				dlg.ShowModal()
				dlg.Destroy()
		else:
			dlg = wx.MessageDialog(None, DV.l('Select some videos in the list first.'), DV.l('No videos selected!'), wx.OK | wx.ICON_EXCLAMATION)
			dlg.SetIcon(DV.icon)
			dlg.ShowModal()
			dlg.Destroy()
		self.onListSelect()
	def onChangeProfileDropdown(self, event):
		sel = self.profiledropdown.GetCurrentSelection()
		if self.profiledropdown.GetItems()[0] == '(Multiple)':
			sel -= 1
		if sel != -1:
			self.onChangeProfile(sel - 1, event)
	def onChangeProfile(self, profile, event):
		items = self.list.getAllSelectedItems()
		if not len(items):
			items = range(self.list.GetItemCount())
		for i in items:
			if self.meta[self.videos[i]]['profile'] != profile:
				self.meta[self.videos[i]]['profile'] = profile
				self.meta[self.videos[i]]['profilemodified'] = True
				self.list.SetStringItem(i, ID_COL_VIDPROFILE, DV.l(DV.prefs.getp(profile, 'name')))
		self.onListSelect()
	def onResetStatus(self, event=None):
		items = self.list.getAllSelectedItems()
		for i in items:
			self.meta[self.videos[i]]['status'] = DV.l('Pending.')
			self.list.SetStringItem(i, ID_COL_VIDSTAT, DV.l('Pending.'))
	def onPrefs(self, event):
		self.reopenprefs = False
		prefs = DamnPrefEditor(self, -1, DV.l('DamnVid preferences'), main=self)
		prefs.ShowModal()
		prefs.Destroy()
		if self.reopenprefs:
			self.onPrefs(event)
		else:
			for i in range(len(self.videos)):
				if self.meta[self.videos[i]]['profile'] >= DV.prefs.profiles or not self.meta[self.videos[i]]['profilemodified']:
					# Yes, using icons as source identifiers, why not? Lol
					if self.meta[self.videos[i]].has_key('module'):
						self.meta[self.videos[i]]['profile'] = self.meta[self.videos[i]]['module'].getProfile()
					elif self.meta[self.videos[i]]['icon'] == DamnGetListIcon('damnvid'):
						self.meta[self.videos[i]]['profile'] = DV.prefs.get('defaultprofile')
					elif self.meta[self.videos[i]]['icon'] == DamnGetListIcon('generic'):
						self.meta[self.videos[i]]['profile'] = DV.prefs.get('defaultwebprofile')
				self.list.SetStringItem(i, ID_COL_VIDPROFILE, DV.l(DV.prefs.getp(self.meta[self.videos[i]]['profile'], 'name')))
		try:
			del self.reopenprefs
		except:
			pass
		self.updateHistory() # In case history size changed
		self.onListSelect()
	def onOpenOutDir(self, event):
		if DV.os == 'nt':
			os.system('explorer.exe "' + DV.prefs.get('outdir') + '"')
		else:
			pass # Halp here?
	def onHalp(self, event):
		webbrowser.open(DV.url_halp, 2)
	def onReportBug(self, event):
		dlg = DamnReportBug(None, -1, main=self)
		dlg.SetIcon(DV.icon)
		dlg.ShowModal()
		dlg.Destroy()
	def onCheckUpdates(self, event=None):
		updater = DamnVidUpdater(self, verbose=event is not None)
		updater.start()
	def onAboutDV(self, event):
		dlg = DamnAboutDamnVid(None, -1, main=self)
		dlg.SetIcon(DV.icon)
		dlg.ShowModal()
		dlg.Destroy()
	def delVid(self, i):
		self.list.DeleteItem(i)
		for vid in range(len(self.thisvideo)):
			if self.thisvideo[vid] == self.videos[i]:
				self.thisvideo.pop(vid)
				self.thisbatch = self.thisbatch - 1
		del self.meta[self.videos[i]]
		self.videos.pop(i)
		if self.converting > i:
			self.converting -= 1
	def onDelete(self, event):
		Damnlog('onDelete event fired:', event)
		if len(self.list.getAllSelectedItems()):
			self.onDelSelection(event)
		else:
			self.onDelAll(event)
	def confirmDeletion(self):
		if DV.prefs.get('warnremove')!='True':
			return True
		dlg = wx.MessageDialog(self, DV.l('Are you sure? (This will not delete any files, it will just remove them from the list.)'), DV.l('Confirmation'), wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION)
		dlg.SetIcon(DV.icon)
		return dlg.ShowModal() == wx.ID_YES
	def onDelSelection(self, event):
		items = self.list.getAllSelectedItems()
		if len(items):
			if self.converting in items:
				dlg = wx.MessageDialog(None, DV.l('Stop the video conversion before deleting the video being converted.'), DV.l('Cannot delete this video'), wx.ICON_EXCLAMATION | wx.OK)
				dlg.SetIcon(DV.icon)
				dlg.ShowModal()
				dlg.Destroy()
			elif self.confirmDeletion():
				for i in reversed(items): # Sequence MUST be reversed, otherwise the first items get deleted first, which changes the indexes of the following items
					self.delVid(i)
			self.onListSelect()
		else:
			dlg = wx.MessageDialog(None, DV.l('You must select some videos from the list first!'), DV.l('Select some videos!'), wx.ICON_EXCLAMATION | wx.OK)
			dlg.SetIcon(DV.icon)
			dlg.ShowModal()
			dlg.Destroy()
	def onDelAll(self, event):
		if len(self.videos):
			if self.confirmDeletion():
				if self.converting != -1:
					self.onStop(None) # Stop conversion if it's in progress
				self.list.DeleteAllItems()
				self.videos = []
				self.thisvideo = []
				self.thisbatch = 0
				self.meta = {}
		else:
			dlg = wx.MessageDialog(None, DV.l('Add some videos in the list first.'), DV.l('No videos!'), wx.OK | wx.ICON_EXCLAMATION)
			dlg.SetIcon(DV.icon)
			dlg.Destroy()
	def onResize(self, event):
		self.Layout()
	def onClipboardTimer(self, event):
		self.clipboardtimer.Stop()
		try:
			if DV.gui_ok and DV.prefs.get('clipboard') == 'True' and not wx.TheClipboard.IsOpened():
				if wx.TheClipboard.Open():
					dataobject = wx.TextDataObject()
					wx.TheClipboard.GetData(dataobject)
					clip = dataobject.GetText()
					wx.TheClipboard.Close()
					clip = DamnUnicode(clip)
					if DV.oldclipboard != clip:
						DV.oldclipboard = clip
						Damnlog('Text scavenged from clipboard (in loop):', clip)
						if self.validURI(clip) == 'Video site' and clip not in self.clippedvideos:
							self.clippedvideos.append(clip)
							if self.addurl is not None:
								self.addurl.onAdd(val=clip)
							else:
								self.addVid([clip], DV.prefs.get('autoconvert') == 'True')
		except:
			Damnlog('Failed to open clipboard.') # The clipboard might not get opened properly, or the prefs object might not exist yet. Just silently pass, gonna catch up at next timer event.
		try:
			wx.TheClipboard.Close() # Try to close it, just in case it's left open.
		except:
			pass
		try:
			self.clipboardtimer.Start(1000)
		except:
			pass # Sometimes the timer can still live while DamnMainFrame is closed, and if EVT_TIMER is then raised, error!
	def onClose(self, event):
		Damnlog('Main window onClose event fired. Converting?', self.converting, '; Is already closing?', self.isclosing)
		if self.converting != -1:
			dlg = wx.MessageDialog(None, DV.l('DamnVid is currently converting a video! Closing DamnVid will cause it to abort the conversion.') + '\r\n' + DV.l('Continue?'), DV.l('Conversion in progress'), wx.YES_NO | wx.NO_DEFAULT | wx.ICON_EXCLAMATION)
			dlg.SetIcon(DV.icon)
			if dlg.ShowModal() == wx.ID_YES:
				Damnlog('User forced shutdown!')
				self.shutdown()
		else:
			self.shutdown()
	def shutdown(self):
		Damnlog('Main window got shutdown() call')
		if self.historyDialog is not None:
			self.historyDialog.onClose()
		try:
			Damnlog('Attempting to get window position/size information.')
			position = self.GetPositionTuple()
			size = self.GetSize()
			screen = wx.Display().GetGeometry()[2:]
			Damnlog('Position is',position,'; size is',size,'; resolution is',screen)
			DV.prefs.sets('damnvid-mainwindow','lastx',position[0])
			DV.prefs.sets('damnvid-mainwindow','lasty',position[1])
			DV.prefs.sets('damnvid-mainwindow','lastw',size[0])
			DV.prefs.sets('damnvid-mainwindow','lasth',size[1])
			DV.prefs.sets('damnvid-mainwindow','lastresw',screen[0])
			DV.prefs.sets('damnvid-mainwindow','lastresh',screen[1])
		except:
			Damnlog('Error while trying to grab position/size information.')
		self.isclosing = True
		self.clipboardtimer.Stop()
		self.Destroy()
