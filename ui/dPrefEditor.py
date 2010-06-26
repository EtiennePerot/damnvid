# -*- coding: utf-8 -*-
from dUI import *
from dModules import *
class DamnPrefEditor(wx.Dialog): # Preference dialog (not manager)
	def __init__(self, parent, id, title, main):
		# Dialog init
		wx.Dialog.__init__(self, parent, id, title, style=wx.RESIZE_BORDER)
		self.parent = main
		DV.prefs.save() # Save just in case, we're gonna modify stuff!
		self.toppanel = wx.Panel(self, -1)
		self.bestsize = [0, 0]
		self.defaultvalue = DV.l('(default)')
		# Top part of the toppanel
		self.topsizer = wx.BoxSizer(wx.VERTICAL)
		self.topsizer.Add((0, DV.border_padding))
		self.uppersizer = wx.BoxSizer(wx.HORIZONTAL)
		self.uppersizer.Add((DV.border_padding, 0))
		self.topsizer.Add(self.uppersizer, 1, wx.EXPAND)
		# -> Left part of the upperpanel
		self.upperleftpanel = wx.Panel(self.toppanel, -1)
		self.uppersizer.Add(self.upperleftpanel, 0)
		self.uppersizer.Add((DV.control_hgap, 0))
		self.upperleftsizer = wx.BoxSizer(wx.VERTICAL)
		self.tree = wx.TreeCtrl(self.upperleftpanel, -1, size=(260, 280), style=wx.TR_LINES_AT_ROOT | wx.TR_HAS_BUTTONS | wx.TR_FULL_ROW_HIGHLIGHT)
		self.upperleftsizer.Add(self.tree, 1, wx.EXPAND)
		self.upperleftsizer.Add((0, DV.control_vgap))
		self.buildTree()
		self.addProfileButton = wx.Button(self.upperleftpanel, -1, DV.l('Add profile'))
		self.upperleftsizer.Add(self.addProfileButton, 0, wx.EXPAND)
		self.upperleftsizer.Add((0, DV.control_vgap))
		self.deleteProfileButton = wx.Button(self.upperleftpanel, -1, DV.l('Delete profile'))
		self.upperleftsizer.Add(self.deleteProfileButton, 0, wx.EXPAND)
		self.upperleftsizer.Add((0, DV.control_vgap))
		self.importButton = wx.Button(self.upperleftpanel, -1, DV.l('Import preferences'))
		self.upperleftsizer.Add(self.importButton, 0, wx.EXPAND)
		self.upperleftsizer.Add((0, DV.control_vgap))
		self.exportButton = wx.Button(self.upperleftpanel, -1, DV.l('Export preferences'))
		self.upperleftsizer.Add(self.exportButton, 0, wx.EXPAND)
		self.upperleftsizer.Add((0, DV.control_vgap))
		self.resetButton = wx.Button(self.upperleftpanel, -1, DV.l('Reset all'))
		self.upperleftsizer.Add(self.resetButton, 0, wx.EXPAND)
		self.upperleftsizer.Add((0, DV.border_padding))
		self.upperleftpanel.SetSizer(self.upperleftsizer)
		# -> Right part of the upperpanel
		self.upperrightpanel = wx.Panel(self.toppanel, -1)
		self.uppersizer.Add(self.upperrightpanel, 1, wx.EXPAND)
		self.prefpanelabel = wx.StaticBox(self.upperrightpanel, -1, '')
		self.upperrightsizer = wx.StaticBoxSizer(self.prefpanelabel, wx.VERTICAL)
		# -> -> Preference pane creation
		self.prefpane = wx.Panel(self.upperrightpanel, -1)
		self.prefpanesizer = wx.GridBagSizer(DV.control_vgap, DV.control_hgap) # Yes, it's vgap then hgap
		self.prefpane.SetSizer(self.prefpanesizer)
		# -> -> End preference pane creation
		self.upperrightsizer.Add(self.prefpane, 1, wx.EXPAND)
		self.uppersizer.Add((DV.border_padding, 0))
		self.upperrightpanel.SetSizer(self.upperrightsizer)
		self.topsizer.Add((0, DV.control_vgap))
		# Bottom part of the toppanel
		self.lowersizer = wx.BoxSizer(wx.HORIZONTAL)
		self.topsizer.Add(self.lowersizer, 0, wx.EXPAND)
		self.lowersizer.AddStretchSpacer(1)
		self.okButton = wx.Button(self.toppanel, wx.ID_OK, DV.l('OK'))
		self.lowersizer.Add(self.okButton, 0, wx.ALIGN_RIGHT)
		self.lowersizer.Add((DV.control_hgap, 0))
		self.closeButton = wx.Button(self.toppanel, wx.ID_CLOSE, DV.l('Cancel'))
		self.lowersizer.Add(self.closeButton, 0, wx.ALIGN_RIGHT)
		self.lowersizer.Add((DV.border_padding, 0))
		self.topsizer.Add((0, DV.border_padding))
		# Final touches, binds, etc.
		self.toppanel.SetSizer(self.topsizer)
		self.Bind(wx.EVT_BUTTON, self.onAddProfile, self.addProfileButton)
		self.Bind(wx.EVT_BUTTON, self.onDeleteProfile, self.deleteProfileButton)
		self.Bind(wx.EVT_BUTTON, self.onOK, self.okButton)
		self.Bind(wx.EVT_BUTTON, self.onImport, self.importButton)
		self.Bind(wx.EVT_BUTTON, self.onExport, self.exportButton)
		self.Bind(wx.EVT_BUTTON, self.onReset, self.resetButton)
		self.Bind(wx.EVT_BUTTON, self.onClose, self.closeButton)
		self.Bind(wx.EVT_TREE_SEL_CHANGED, self.onTreeSelectionChanged, self.tree)
		self.Bind(wx.EVT_KEY_DOWN, self.onKeyDown, self.toppanel)
		self.Bind(DV.evt_load, self.onLoad)
		self.toppanel.SetFocus()
		self.forceSelect(self.treeroot) # Will also resize the window on certain platforms since it fires the selection events, but not on Linux it seems, so...
		self.updatePrefPane('damnvid')
		self.Center()
	def buildTree(self):
		self.tree.DeleteAllItems()
		self.treeimages = wx.ImageList(16, 16, True)
		self.tree.AssignImageList(self.treeimages)
		self.treeroot = self.tree.AddRoot(DV.l('DamnVid Preferences'))
		self.tree.SetItemImage(self.treeroot, self.treeimages.Add(wx.Bitmap(DV.images_path + 'icon16.png')))
		self.proxyprefs = self.tree.AppendItem(self.treeroot, DV.l('Proxy'))
		self.tree.SetItemImage(self.proxyprefs, self.treeimages.Add(wx.Bitmap(DV.images_path + 'web-16.png')))
		self.searchprefs = self.tree.AppendItem(self.treeroot, DV.l('YouTube browser'))
		self.tree.SetItemImage(self.searchprefs, self.treeimages.Add(wx.Bitmap(DV.images_path + 'youtubebrowser.png')))
		self.modulelistitem = self.tree.AppendItem(self.treeroot, DV.l('Modules'))
		self.tree.SetItemImage(self.modulelistitem, self.treeimages.Add(wx.Bitmap(DV.images_path + 'modules.png')))
		self.modules = {}
		self.moduledescs = {}
		for i in DamnIterModules():
			self.modules[i] = self.tree.AppendItem(self.modulelistitem, DV.modules[i]['title'])
			self.tree.SetItemImage(self.modules[i], self.treeimages.Add(wx.Bitmap(DV.modules_path + DV.modules[i]['name'] + DV.sep + DV.modules[i]['icon']['small'])))
		self.profileroot = self.tree.AppendItem(self.treeroot, DV.l('Encoding profiles'))
		self.tree.SetItemImage(self.profileroot, self.treeimages.Add(wx.Bitmap(DV.images_path + 'profiles.png')))
		self.profiles = []
		for i in range(DV.prefs.profiles):
			treeitem = self.tree.AppendItem(self.profileroot, DV.l(DV.prefs.getp(i, 'name'), warn=False))
			self.profiles.append(treeitem)
			self.tree.SetItemImage(treeitem, self.treeimages.Add(wx.Bitmap(DV.images_path + 'profile.png')))
		self.tree.ExpandAll()
		self.forceSelect(self.treeroot)
	def forceSelect(self, item, event=None):
		self.tree.SelectItem(item, True)
	def onTreeSelectionChanged(self, event):
		item = event.GetItem()
		self.prefpanelabel.SetLabel(self.tree.GetItemText(item))
		if item == self.treeroot:
			self.updatePrefPane('damnvid')
		elif item == self.searchprefs:
			self.updatePrefPane('damnvid-search')
		elif item == self.proxyprefs:
			self.updatePrefPane('damnvid-proxy')
		elif item == self.modulelistitem:
			self.updatePrefPane('special:modules')
		elif item == self.profileroot:
			self.updatePrefPane('special:profileroot')
		elif item in self.profiles:
			self.updatePrefPane('damnvid-profile-' + str(self.profiles.index(item)))
		elif item in self.modules.values():
			for i in DamnIterModules():
				if self.modules[i] == item:
					self.updatePrefPane('damnvid-module-' + i)
					break
		else:
			self.updatePrefPane('special:error')
	def getLabel(self, panel, label, color='#000000', bold=False, hyperlink=None, background=None):
		if hyperlink is None:
			lbl = wx.StaticText(panel, -1, label)
		else:
			lbl = DamnHyperlink(panel, -1, label, hyperlink)
		lbl.SetBackgroundColour(wx.WHITE)
		if bold:
			sysfont = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
			boldfont = wx.Font(sysfont.GetPointSize(), sysfont.GetFamily(), sysfont.GetStyle(), wx.FONTWEIGHT_BOLD)
			lbl.SetFont(boldfont)
		if hyperlink is None and color is not None:
			lbl.SetForegroundColour(color)
		return lbl
	def buildModulePanel(self, parent, module, extended=False, buttons=True, withscrollbars=False):
		mod = DV.modules[module]
		tmppanel = wx.Panel(parent, -1, style=wx.SIMPLE_BORDER)
		tmppanel.SetBackgroundColour(wx.WHITE)
		panelwidth = parent.GetSizeTuple()[0]
		if withscrollbars:
			tmpscroll = wx.ScrollBar(tmppanel, -1, style=wx.SB_VERTICAL)
			panelwidth -= tmpscroll.GetSizeTuple()[0]
			tmpscroll.Destroy()
			del tmpscroll
		tmptop3sizer = wx.BoxSizer(wx.VERTICAL)
		tmppanel.SetSizer(tmptop3sizer)
		tmptop3sizer.Add((0, DV.border_padding))
		tmptop2sizer = wx.BoxSizer(wx.HORIZONTAL)
		tmptop3sizer.Add(tmptop2sizer, 1, wx.EXPAND)
		tmptop3sizer.Add((0, DV.border_padding))
		tmptop2sizer.Add((DV.border_padding, 0))
		tmptopsizer = wx.BoxSizer(wx.VERTICAL)
		tmptop2sizer.Add(tmptopsizer, 1, wx.EXPAND)
		tmptop2sizer.Add((DV.border_padding, 0))
		# Construct top row of the module item
		tehrow = wx.BoxSizer(wx.HORIZONTAL)
		tmptopsizer.Add(tehrow, 1, wx.EXPAND)
		tehrow.Add(wx.StaticBitmap(tmppanel, -1, wx.Bitmap(DV.modules_path + module + DV.sep + mod['icon']['large'])))
		tehrow.Add((DV.control_hgap, 0))
		rightcol = wx.BoxSizer(wx.VERTICAL)
		tehrow.Add(rightcol, 1, wx.EXPAND)
		toprow = wx.BoxSizer(wx.HORIZONTAL)
		rightcol.Add(toprow)
		if mod['about'].has_key('url'):
			toprow.Add(self.getLabel(tmppanel, mod['title'], hyperlink=mod['about']['url'], bold=True))
		else:
			toprow.Add(self.getLabel(tmppanel, mod['title'], bold=True))
		toprow.Add(self.getLabel(tmppanel, DV.l(' (version ')))
		toprow.Add(self.getLabel(tmppanel, mod['version'], bold=True))
		toprow.Add(self.getLabel(tmppanel, ')'))
		toprow.Add(self.getLabel(tmppanel, DV.l(' by '), color='#707070'))
		if mod['author'].has_key('url'):
			toprow.Add(self.getLabel(tmppanel, mod['author']['name'], hyperlink=mod['author']['url'], bold=True))
		else:
			toprow.Add(self.getLabel(tmppanel, mod['author']['name'], bold=True))
		toprow.Add(self.getLabel(tmppanel, '.'))
		descwidth = parent.GetSizeTuple()[0] - 2 * DV.border_padding - 72 - DV.control_hgap
		if extended:
			rightcol.Add(self.getLabel(tmppanel, DV.l('Author:'), bold=True))
			authorsizer = wx.BoxSizer(wx.HORIZONTAL)
			rightcol.Add(authorsizer)
			authorsizer.Add((DV.control_hgap * 2, 0)) # Indent a bit
			if mod['author'].has_key('url'):
				authorsizer.Add(self.getLabel(tmppanel, mod['author']['name'], bold=True, hyperlink=mod['author']['url']))
			else:
				authorsizer.Add(self.getLabel(tmppanel, mod['author']['name'], bold=True))
			if mod['author'].has_key('email'):
				authorsizer.Add(self.getLabel(tmppanel, DV.l(' <'), color='#707070'))
				authorsizer.Add(self.getLabel(tmppanel, mod['author']['email'], hyperlink='mailto:' + mod['author']['email']))
				authorsizer.Add(self.getLabel(tmppanel, DV.l('>'), color='#707070'))
			desc = self.getLabel(tmppanel, mod['about']['long'])
		else:
			desc = self.getLabel(tmppanel, mod['about']['short'])
		desc.Wrap(descwidth)
		self.moduledescs[mod['name']] = (desc, descwidth)
		rightcol.Add((0, DV.control_vgap))
		rightcol.Add(desc)
		if buttons:
			rightcol.Add((0, DV.control_vgap))
			tmpbuttonsizer = wx.BoxSizer(wx.HORIZONTAL)
			rightcol.Add(tmpbuttonsizer, 0, wx.ALIGN_RIGHT)
			config = wx.Button(tmppanel, -1, DV.l('Configure'))
			config.Bind(wx.EVT_BUTTON, DamnCurry(self.forceSelect, self.modules[module]))
			tmpbuttonsizer.Add(config)
			tmpbuttonsizer.Add((DV.control_hgap, 0))
			update = wx.Button(tmppanel, -1, DV.l('Update'))
			update.Bind(wx.EVT_BUTTON, DamnCurry(self.onModuleUpdate, module))
			tmpbuttonsizer.Add(update)
			tmpbuttonsizer.Add((DV.control_hgap, 0))
			uninstall = wx.Button(tmppanel, -1, DV.l('Uninstall'))
			uninstall.Bind(wx.EVT_BUTTON, DamnCurry(self.onModuleUninstall, module))
			tmpbuttonsizer.Add(uninstall)
		return tmppanel
	def updatePrefPane(self, pane):
		self.prefpanesizer.Clear(True) # Delete all controls in prefpane
		for i in range(self.prefpanesizer.GetCols()):
			try:
				self.prefpanesizer.RemoveGrowableCol(i)
			except:
				pass
		for i in range(self.prefpanesizer.GetRows()):
			try:
				self.prefpanesizer.RemoveGrowableRow(i)
			except:
				pass
		self.pane = pane
		if pane[0:8].lower() == 'special:':
			pane = pane[8:]
			if pane == 'profileroot':
				txt = wx.StaticText(self.prefpane, -1, DV.l('locale:damnvid-profile-explanation'))
				txt.Wrap(max(self.prefpane.GetSize()[0], 300))
				self.prefpanesizer.Add(txt, (0, 0), (1, 1))
			elif pane == 'error':
				txt = wx.StaticText(self.prefpane, -1, DV.l('Error!'))
				txt.Wrap(max(self.prefpane.GetSize()[0], 300))
				self.prefpanesizer.Add(txt, (0, 0), (1, 1))
			elif pane == 'modules':
				topsizer = wx.BoxSizer(wx.VERTICAL)
				self.prefpanesizer.Add(topsizer, (0, 0), (1, 1), wx.EXPAND)
				self.prefpanesizer.AddGrowableCol(0, 1)
				self.prefpanesizer.AddGrowableRow(0, 1)
				# Construct module list
				self.modulelist = wx.ScrolledWindow(self.prefpane, -1, size=(460, 3 * (72 + 2 * DV.border_padding)))
				self.modulelist.SetMinSize((460, 3 * (72 + 2 * DV.border_padding)))
				modlistsizer = wx.BoxSizer(wx.VERTICAL)
				self.modulelist.SetSizer(modlistsizer)
				topsizer.Add(self.modulelist, 1, wx.EXPAND)
				topsizer.Add((0, DV.control_vgap))
				buttonsizer = wx.BoxSizer(wx.HORIZONTAL)
				topsizer.Add(buttonsizer, 0, wx.ALIGN_RIGHT, border=1)
				if DV.os == 'mac':
					topsizer.Add((0, 2)) # Annoying glitch with the buttons
				# Construct module list scrollable window
				for mod in DamnIterModules():
					modlistsizer.Add(self.buildModulePanel(self.modulelist, mod, withscrollbars=True), 0, wx.EXPAND)
				self.modulelist.SetScrollbars(0, DV.control_vgap * DV.scroll_factor, 0, 0)
				# Construct buttons under module list
				install = wx.Button(self.prefpane, -1, DV.l('Install...'))
				install.Bind(wx.EVT_BUTTON, self.onModuleInstall)
				buttonsizer.Add(install)
				buttonsizer.Add((DV.control_hgap, 0))
				reset = wx.Button(self.prefpane, -1, DV.l('Reset all...'))
				reset.Bind(wx.EVT_BUTTON, self.onModuleAllReset)
				buttonsizer.Add(reset)
				buttonsizer.Add((DV.control_hgap, 0))
				update = wx.Button(self.prefpane, -1, DV.l('Check for updates'))
				update.Bind(wx.EVT_BUTTON, self.onModuleAllUpdate)
				buttonsizer.Add(update)
		else:
			prefprefix = pane
			profile = None
			module = None
			if prefprefix[0:16].lower() == 'damnvid-profile-':
				prefprefix = prefprefix[0:15]
				profile = int(pane[16:])
			elif prefprefix[0:15].lower() == 'damnvid-module-':
				module = prefprefix[15:]
			prefprefix += ':'
			self.controls = {}
			currentprefs = []
			maxheight = {str(DV.preference_type_video):0, str(DV.preference_type_audio):0, str(DV.preference_type_profile):0, str(DV.preference_type_misc):0}
			maxwidth = {str(DV.preference_type_video):0, str(DV.preference_type_audio):0, str(DV.preference_type_profile):0, str(DV.preference_type_misc):0}
			count = 0
			availprefs = DV.prefs.lists(pane)
			for i in DV.preference_order[prefprefix[0:-1]]:
				if prefprefix + i in DV.preferences.keys() and i in availprefs:
					if not DV.preferences[prefprefix + i].has_key('noedit'):
						currentprefs.append(prefprefix + i)
			for i in availprefs:
				if prefprefix + i in DV.preferences.keys():
					desc = DV.preferences[prefprefix + i]
					if not desc.has_key('noedit'):
						if prefprefix + i not in currentprefs:
							currentprefs.append(prefprefix + i)
						maxheight[str(desc['type'])] += 1
						maxwidth[str(desc['type'])] = max((maxwidth[str(desc['type'])], self.getPrefWidth(prefprefix + i)))
			maxwidth[str(DV.preference_type_profile)] = max((maxwidth[str(DV.preference_type_misc)], maxwidth[str(DV.preference_type_profile)], maxwidth[str(DV.preference_type_video)] + maxwidth[str(DV.preference_type_audio)]))
			maxwidth[str(DV.preference_type_misc)] = maxwidth[str(DV.preference_type_profile)]
			count = 0
			currentprefsinsection = {str(DV.preference_type_video):0, str(DV.preference_type_audio):0, str(DV.preference_type_profile):0, str(DV.preference_type_misc):0}
			for i in currentprefs:
				shortprefname = i[i.find(':') + 1:]
				if profile == None:
					val = DV.prefs.gets(pane, shortprefname)
				else:
					val = DV.prefs.getp(profile, shortprefname)
				position = [int(module is not None), 0]
				if DV.preferences[i]['type'] == DV.preference_type_audio:
					position[1] += maxwidth[str(DV.preference_type_video)]
				elif DV.preferences[i]['type'] == DV.preference_type_profile:
					position[0] += max((maxheight[str(DV.preference_type_video)], maxheight[str(DV.preference_type_audio)]))
				elif DV.preferences[i]['type'] == DV.preference_type_misc:
					position[0] += maxheight[str(DV.preference_type_profile)] + max((maxheight[str(DV.preference_type_video)], maxheight[str(DV.preference_type_audio)]))
				position[0] += currentprefsinsection[str(DV.preferences[i]['type'])]
				controlposition = (position[0], position[1] + 1)
				controlspan = (1, maxwidth[str(DV.preferences[i]['type'])] - 1)
				currentprefsinsection[str(DV.preferences[i]['type'])] += 1
				if DV.preferences[i]['kind'] != 'bool':
					label = wx.StaticText(self.prefpane, -1, DV.l(DV.preferences[i]['name']) + ':')
					self.prefpanesizer.Add(label, (position[0], position[1]), (1, 1), wx.ALIGN_CENTER_VERTICAL | wx.ALIGN_RIGHT)
				if type(DV.preferences[i]['kind']) is type({}):
					choices = [self.defaultvalue]
					for f in DV.preferences[i]['order']:
						choices.append(DV.preferences[i]['kind'][f])
					if not val:
						val = self.defaultvalue
					else:
						if val in DV.preferences[i]['kind']:
							val = DV.preferences[i]['kind'][val]
					self.controls[i] = self.makeList(DV.preferences[i]['strict'], choices, self.prefpane, val) # makeList takes care of the event binding
					self.prefpanesizer.Add(self.controls[i], controlposition, controlspan, wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)
				elif DV.preferences[i]['kind'][0] == '%':
					self.controls[i] = self.makeSlider(self.prefpane, self.prefpanesizer, (controlposition, controlspan), int(100.0 * float(val) / float(str(DV.preferences[i]['kind'][1:]))), 0, 200)
				elif DV.preferences[i]['kind'] == 'bool':
					if DV.preferences[i]['align']:
						self.controls[i] = wx.CheckBox(self.prefpane, -1)
						label = wx.StaticText(self.prefpane, -1, DV.l(DV.preferences[i]['name']))
						label.Bind(wx.EVT_LEFT_UP, DamnCurry(self.onFakeCheckboxLabelClick, self.controls[i]))
						self.prefpanesizer.Add(self.controls[i], (position[0], position[1]), (1, 1), wx.ALIGN_RIGHT)
						self.prefpanesizer.Add(label, (position[0], position[1] + 1), (1, 1), wx.EXPAND)
					else:
						self.controls[i] = wx.CheckBox(self.prefpane, -1, DV.l(DV.preferences[i]['name']))
						self.prefpanesizer.Add(self.controls[i], (position[0], position[1]), (1, maxwidth[str(DV.preferences[i]['type'])]), wx.EXPAND)
					self.controls[i].SetValue(val == 'True')
					self.Bind(wx.EVT_CHECKBOX, self.onPrefChange, self.controls[i])
				elif DV.preferences[i]['kind'][:3] == 'int':
					choices = [self.defaultvalue]
					if DV.preferences[i]['kind'][:5] == 'intk:':
						for f in range(int(DV.preferences[i]['kind'][DV.preferences[i]['kind'].find(':') + 1:DV.preferences[i]['kind'].find('-')]), int(DV.preferences[i]['kind'][DV.preferences[i]['kind'].find('-') + 1:])):
							choices.append(str(pow(2, f)) + 'k')
						if not val:
							val = self.defaultvalue
						self.controls[i] = self.makeList(DV.preferences[i]['strict'], choices, self.prefpane, val) # makeList takes care of the event binding
						self.prefpanesizer.Add(self.controls[i], controlposition, controlspan, wx.EXPAND)
					elif DV.preferences[i]['kind'][:4] == 'int:':
						interval = (int(DV.preferences[i]['kind'][DV.preferences[i]['kind'].find(':') + 1:DV.preferences[i]['kind'].find('-')]), int(DV.preferences[i]['kind'][DV.preferences[i]['kind'].find('-') + 1:]))
						if not val:
							val = '0'
						self.controls[i] = self.makeSlider(self.prefpane, self.prefpanesizer, (controlposition, controlspan), int(val), min(interval), max(interval))
					elif DV.preferences[i]['kind'] == 'int':
						if not val:
							val = self.defaultvalue
						self.controls[i] = self.makeList(False, [self.defaultvalue], self.prefpane, val)
						self.prefpanesizer.Add(self.controls[i], controlposition, controlspan, wx.EXPAND)
				elif DV.preferences[i]['kind'] == 'dir':
					pathpanel = wx.Panel(self.prefpane, -1)
					pathsizer = wx.BoxSizer(wx.HORIZONTAL)
					pathpanel.SetSizer(pathsizer)
					self.prefpanesizer.Add(pathpanel, controlposition, controlspan, wx.EXPAND)
					self.controls[i] = wx.TextCtrl(pathpanel, -1, val)
					self.Bind(wx.EVT_TEXT, self.onPrefChange, self.controls[i])
					pathsizer.Add(self.controls[i], 1, wx.EXPAND)
					pathsizer.Add((DV.control_hgap, 0))
					browseButton = DamnBrowseDirButton(pathpanel, -1, DV.l('Browse...'), control=self.controls[i], title=DV.l('Select DamnVid\'s output directory.'), callback=self.onBrowseDir)
					self.Bind(wx.EVT_BUTTON, browseButton.onBrowse, browseButton)
					pathsizer.Add(browseButton, 0)
				elif DV.preferences[i]['kind'] == 'text':
					self.controls[i] = wx.TextCtrl(self.prefpane, -1, DV.l(val, warn=False))
					self.Bind(wx.EVT_TEXT, self.onPrefChange, self.controls[i])
					self.prefpanesizer.Add(self.controls[i], controlposition, controlspan, wx.EXPAND)
				elif DV.preferences[i]['kind'] == 'locale':
					langs = []
					c = 0
					lang = 0
					for l in DV.languages.iterkeys():
						if DV.lang == l:
							lang = c
						c += 1
						langs.append(DV.languages[l]['title']) # Eventually translate here, but I'm not sure. Maybe both translated and untranslated?
					self.controls[i] = self.makeList(DV.preferences[i]['strict'], langs, self.prefpane, None, localize=False) # makeList takes care of the event binding
					self.controls[i].SetSelection(lang)
					self.prefpanesizer.Add(self.controls[i], controlposition, controlspan, wx.EXPAND)
				elif DV.preferences[i]['kind'] == 'profile':
					if DV.prefs.profiles:
						choices = []
						for p in range(-1, DV.prefs.profiles):
							choices.append(DV.prefs.getp(p, 'name'))
						self.controls[i] = self.makeList(DV.preferences[i]['strict'], choices, self.prefpane, None) # makeList takes care of the event binding
						self.controls[i].SetSelection(int(val) + 1) # +1 to compensate for -1 -> (Do not encode)
					else:
						self.controls[i] = wx.StaticText(self.prefpane, -1, DV.l('No encoding profiles found!'))
					self.prefpanesizer.Add(self.controls[i], controlposition, controlspan, wx.EXPAND)
				count = count + 1
			self.prefpanesizer.Layout()
			cols = self.prefpanesizer.GetCols()
			totalwidth = float(self.prefpanesizer.GetMinSize()[0] - (cols - 1) * self.prefpanesizer.GetHGap())
			splitwidth = round(totalwidth / float(cols) - .5)
			lastrow = self.prefpanesizer.GetRows()
			for i in range(cols):
				try:
					self.prefpanesizer.AddGrowableCol(i)
				except:
					pass
				curwidth = splitwidth
				if i == cols - 1:
					curwidth += totalwidth - splitwidth * cols
				self.prefpanesizer.Add((int(curwidth), 0), (lastrow, i), (1, 1))
			if module is not None:
				self.prefpanesizer.Add(self.buildModulePanel(self.prefpane, module, extended=True, buttons=False), (0, 0), (1, self.prefpanesizer.GetCols()), wx.EXPAND)
		self.prefpanesizer.Layout() # Mandatory
		newsize = self.toppanel.GetBestSize()
		if newsize[0] > self.bestsize[0]:
			self.bestsize[0] = newsize[0]
		if newsize[1] > self.bestsize[1]:
			self.bestsize[1] = newsize[1]
		self.SetClientSize(newsize)
		self.SetClientSize(self.bestsize)
		self.Center()
	def getPrefWidth(self, pref):
		if type(DV.preferences[pref]['kind']) is type({}):
			return 2
		if DV.preferences[pref]['kind'][0:3] == 'int':
			return 2
		if DV.preferences[pref]['kind'] == 'profile':
			return 2
		if DV.preferences[pref]['kind'] == 'locale':
			return 2
		if DV.preferences[pref]['kind'][0] == '%':
			return 2
		if DV.preferences[pref]['kind'] == 'text':
			return 2
		if DV.preferences[pref]['kind'] == 'dir':
			return 2 # Label + Panel{TextCtrl + Button} = 2
		if DV.preferences[pref]['kind'] == 'bool':
			return 1
		return 0
	def onFakeCheckboxLabelClick(self, checkbox, event):
		checkbox.SetValue(not checkbox.IsChecked())
	def splitLongPref(self, pref):
		if pref.find(':') == -1:
			return pref
		return (pref[0:pref.find(':')], pref[pref.find(':') + 1:])
	def onPrefChange(self, event):
		Damnlog('Preference changed event caught.')
		name = None
		for i in self.controls.iterkeys():
			pref = self.splitLongPref(i)
			prefname = pref[1]
			if pref[0][0:16] == 'damnvid-profile-':
				genericpref = pref[0][0:15]
			else:
				genericpref = pref[0]
			genericpref += ':' + pref[1]
			val = None
			if type(DV.preferences[genericpref]['kind']) is type({}) or (DV.preferences[genericpref]['kind'][0:3] == 'int' and DV.preferences[genericpref]['kind'][0:4] != 'int:'):
				if DV.preferences[genericpref]['strict']:
					val = self.controls[i].GetSelection()
					if val:
						val = DV.preferences[genericpref]['order'][val - 1]
					else:
						val = ''
				else:
					val = self.controls[i].GetValue()
					if val == self.defaultvalue or val == '(default)':
						val = ''
					elif type(DV.preferences[genericpref]['kind']) is type({}) and val in DV.preferences[genericpref]['kind'].values():
						for j in DV.preferences[genericpref]['kind'].iterkeys():
							if val == DV.preferences[genericpref]['kind'][j]:
								val = j
			elif DV.preferences[genericpref]['kind'] == 'profile':
				val = self.controls[i].GetSelection() - 1
			elif DV.preferences[genericpref]['kind'] == 'locale':
				val = self.controls[i].GetString(self.controls[i].GetSelection())
				for loc in DV.languages.iterkeys():
					if DV.languages[loc]['title'] == val:
						val = loc
						break
			elif DV.preferences[genericpref]['kind'][0:4] == 'int:':
				val = int(self.controls[i].GetValue())
			elif DV.preferences[genericpref]['kind'][0] == '%':
				val = float(float(self.controls[i].GetValue())*float(int(DV.preferences[genericpref]['kind'][1:])) / 100.0)
			elif DV.preferences[genericpref]['kind'] == 'text':
				val = DV.l(self.controls[i].GetValue(), warn=False, reverse=True)
				if genericpref == 'damnvid-profile:name':
					name = val
			elif DV.preferences[genericpref]['kind'] == 'dir':
				val = self.controls[i].GetValue()
			elif DV.preferences[genericpref]['kind'] == 'bool':
				val = self.controls[i].IsChecked() # The str() representation takes care of True/False
			if val is not None:
				DV.prefs.sets(self.pane, prefname, DamnUnicode(val))
		if name != None and self.tree.GetSelection() != self.treeroot and self.tree.GetItemParent(self.tree.GetSelection()) == self.profileroot:
			self.tree.SetItemText(self.tree.GetSelection(), DV.l(name, warn=False))
			self.prefpanelabel.SetLabel(name)
	def onBrowseDir(self, button, path):
		for i in self.controls.iterkeys():
			if self.controls[i] == button.filefield:
				DV.prefs.sets(self.pane, self.splitLongPref(i)[1], path)
	def onAddProfile(self, event):
		DV.prefs.addp()
		prof = self.tree.AppendItem(self.profileroot, DV.prefs.getp(DV.prefs.profiles - 1, 'name'))
		self.tree.SetItemImage(prof, self.treeimages.Add(wx.Bitmap(DV.images_path + 'profile.png')))
		self.profiles.append(prof)
		self.tree.SelectItem(self.profiles[-1], True)
	def onDeleteProfile(self, event):
		if self.tree.GetSelection() != self.treeroot and self.tree.GetItemParent(self.tree.GetSelection()) == self.profileroot:
			if len(self.profiles) > 1:
				profile = int(self.pane[16:])
				DV.prefs.remp(profile)
				curprofile = self.tree.GetSelection()
				if not profile:
					# User is deleting first profile
					newprofile = self.tree.GetNextSibling(curprofile)
				else:
					# User is not deleting first profile, all right
					newprofile = self.tree.GetPrevSibling(curprofile)
				self.profiles.remove(curprofile)
				try:
					self.tree.SelectItem(newprofile)
				except:
					self.tree.SelectItem(self.profileroot)
				self.tree.Delete(curprofile)
			else:
				dlg = wx.MessageDialog(None, DV.l('Cannot delete all encoding profiles!'), DV.l('Cannot delete all profiles'), wx.OK | wx.ICON_EXCLAMATION)
				dlg.SetIcon(DV.icon)
				dlg.ShowModal()
				dlg.Destroy()
		else:
			dlg = wx.MessageDialog(None, DV.l('Please choose a profile to delete from the profile list.'), DV.l('No profile selected'), wx.OK | wx.ICON_EXCLAMATION)
			dlg.SetIcon(DV.icon)
			dlg.ShowModal()
			dlg.Destroy()
	def onLoad(self, event):
		if self.tree.GetSelection() != self.modulelistitem:
			return
		info = event.GetInfo()
		mod = info['module']['name']
		modtitle = info['module']['title']
		desc = self.moduledescs[mod]
		if type(info['result']) is type(''):
			if info['result'] == 'error':
				desc[0].SetLabel(DV.l('There was an error while checking for updates to ') + modtitle + '.')
				desc[0].Wrap(desc[1])
			elif info['result'] == 'uptodate':
				desc[0].SetLabel(modtitle + DV.l(' is up-to-date.'))
				desc[0].Wrap(desc[1])
			elif info['result'] == 'cannot':
				desc[0].SetLabel(modtitle + DV.l(' has no update mechanism.'))
				desc[0].Wrap(desc[1])
		elif type(info['result']) is type(()):
			self.buildTree()
			self.forceSelect(self.modulelistitem)
			desc = self.moduledescs[mod]
			desc[0].SetLabel(modtitle + DV.l(' has been updated to version ') + str(info['result'][0]) + '.')
			desc[0].Wrap(desc[1])
		self.modulelist.Layout()
		self.modulelist.AdjustScrollbars()
	def onModuleUpdate(self, module=None, event=None):
		if not DV.modules.has_key(module):
			return
		module = DV.modules[module]
		desc = self.moduledescs[module['name']]
		if not module['about'].has_key('url'):
			desc[0].SetLabel(module['title'] + DV.l(' has no update mechanism.'))
			desc[0].Wrap(desc[1])
			return
		desc[0].SetLabel(DV.l('Checking for updates...'))
		desc[0].Wrap(desc[1])
		updatecheck = DamnModuleUpdateCheck(self, module)
		updatecheck.start()
	def onModuleAllUpdate(self, event):
		modlist = []
		for i in self.moduledescs.iterkeys():
			if DV.modules.has_key(i):
				modlist.append(DV.modules[i])
				self.moduledescs[i][0].SetLabel(DV.l('Checking for updates...'))
				self.moduledescs[i][0].Wrap(self.moduledescs[i][1])
		updatecheck = DamnModuleUpdateCheck(self, modlist)
		updatecheck.start()
	def onModuleAllReset(self, event):
		dlg = wx.MessageDialog(None, DV.l('Are you sure you want to reset all the default modules and their preferences?'), DV.l('Are you sure?'), wx.YES_NO | wx.ICON_QUESTION)
		dlg.SetIcon(DV.icon)
		if dlg.ShowModal() == wx.ID_YES:
			for i in DV.prefs.listsections():
				if i[0:15] == 'damnvid-module-':
					DV.prefs.rems(i)
			DV.prefs.save()
			DamnLoadConfig(forcemodules=True)
			DV.prefs = DamnVidPrefs()
			self.buildTree()
			self.forceSelect(self.modulelistitem)
		dlg.Destroy()
	def onModuleInstall(self, event=None):
		dlg = wx.FileDialog(None, DV.l('Where is located the module to install?'), DV.prefs.get('lastmoduledir'), '', DV.l('locale:browse-damnvid-modules'), wx.FD_OPEN)
		dlg.SetIcon(DV.icon)
		result = None
		if dlg.ShowModal() == wx.ID_OK:
			path = dlg.GetPath()
			DV.prefs.set('lastmoduledir', os.path.dirname(path))
			result = DamnInstallModule(path)
		dlg.Destroy()
		message = None
		if result is not None:
			if result == 'success':
				message = (DV.l('Success!'), DV.l('The module was successfully installed.'), wx.ICON_INFORMATION)
			elif result == 'nofile':
				message = (DV.l('Error'), DV.l('Error: Could not find the module file.'), wx.ICON_ERROR)
			elif result == 'nomodule':
				message = (DV.l('Error'), DV.l('Error: This file is not a valid DamnVid module.'), wx.ICON_ERROR)
			else:
				message = (DV.l('Error'), DV.l('Error: Unknown error while installing module.'), wx.ICON_ERROR)
		if message is not None:
			DamnLoadConfig()
			DV.prefs = DamnVidPrefs()
			self.buildTree()
			self.forceSelect(self.modulelistitem)
			dlg = wx.MessageDialog(None, message[1], message[0], message[2])
			dlg.SetIcon(DV.icon)
			dlg.ShowModal()
			dlg.Destroy()
	def onModuleUninstall(self, module=None, event=None):
		if not DV.modules.has_key(module):
			return
		dlg = wx.MessageDialog(None, DV.l('Are you sure you want to uninstall the module: ') + DV.modules[module]['title'] + '?', DV.l('Are you sure?'), wx.YES_NO | wx.ICON_QUESTION)
		dlg.SetIcon(DV.icon)
		if dlg.ShowModal() == wx.ID_YES:
			del DV.modules[module]
			try:
				shutil.rmtree(DV.modules_path + module)
			except:
				pass
			DV.prefs.rems('damnvid-module-' + module)
			self.buildTree()
			self.forceSelect(self.modulelistitem)
		dlg.Destroy()
	def makeList(self, strict, choices, panel, value, localize=True):
		Damnlog('makeList called with choices', choices,'; value', value,'; localized:', localize)
		choices2 = []
		for c in choices:
			if not localize or c == self.defaultvalue:
				choices2.append(c)
			else:
				choices2.append(DV.l(c))
		if localize and value not in choices2:
			value = DV.l(value)
		if strict:
			cont = wx.Choice(panel, -1, choices=choices2)
			if value == self.defaultvalue or value == '(default)' or value not in choices2:
				cont.SetSelection(0)
			else:
				for f in range(len(choices2)):
					if choices[f] == value:
						cont.SetSelection(f)
			self.Bind(wx.EVT_CHOICE, self.onPrefChange, cont)
		else:
			cont = wx.ComboBox(panel, -1, choices=choices2, value=value)
			cont.SetValue(value) # Fixes bug on OS X where the value wouldn't be set if it's not one of the choices
			self.Bind(wx.EVT_TEXT, self.onPrefChange, cont)
		return cont
	def makeSlider(self, panel, sizer, position, value, minval, maxval):
		value = min((maxval, max((int(minval), int(value)))))
		tmppanel = wx.Panel(panel, -1)
		tmpsizer = wx.BoxSizer(wx.HORIZONTAL)
		tmppanel.SetSizer(tmpsizer)
		containersizer = wx.BoxSizer(wx.VERTICAL)
		tmpsizer.Add(containersizer, 7, wx.ALIGN_CENTER_VERTICAL)
		containersizer.Add((0, 1))
		slider = wx.Slider(tmppanel, -1, value=value, minValue=minval, maxValue=maxval, style=wx.SL_HORIZONTAL)
		containersizer.Add(slider, 1, wx.EXPAND)
		containersizer.Add((0, 1))
		tmplabel = wx.StaticText(tmppanel, -1, str(value))
		tmpsizer.Add(tmplabel, 1, wx.ALIGN_CENTER_VERTICAL)
		self.Bind(wx.EVT_SLIDER, DamnCurry(self.updateSlider, slider, tmplabel), slider)
		sizer.Add(tmppanel, position[0], position[1], wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)
		return slider
	def updateSlider(self, slider, label, event=None):
		label.SetLabel(str(slider.GetValue()))
		self.onPrefChange(event)
	def getListValue(self, name, strict):
		if strict:
			val = self.listvalues[name][self.controls[name].GetSelection()]
		else:
			val = self.controls[name].GetValue()
		if val == self.defaultvalue or val == '(default)':
			val = ''
		elif type(DV.preference_type[name]['kind']) is type({}):
			for key, i in DV.preference_type[name]['kind'].iteritems():
				if i == val or DV.l(i, warn=False) == val:
					return key
		return val
	def setListValue(self, name, strict, value):
		if not value:
			if strict:
				self.controls[name].SetSelection(0)
			else:
				self.controls[name].SetValue(self.defaultvalue)
		else:
			if strict:
				if type(DV.preference_type[name]['kind']) is type({}):
					value = DV.l(DV.preference_type[name]['kind'][value])
				c = 0
				for i in self.listvalues[name]:
					if i == value:
						self.controls[name].SetSelection(c)
					c = c + 1
			else:
				self.controls[name].SetValue(value)
	def onOK(self, event):
		DV.prefs.save()
		self.Close(True)
	def onReset(self, event):
		dlg = wx.MessageDialog(None, DV.l('All changes to DamnVid\'s configuration will be lost. Continue?'), DV.l('Are you sure?'), wx.YES_NO | wx.ICON_QUESTION)
		dlg.SetIcon(DV.icon)
		if dlg.ShowModal() == wx.ID_YES:
			dlg.Destroy()
			checkupdates = DV.prefs.get('checkforupdates')
			DV.prefs = None
			os.remove(DV.conf_file)
			shutil.copyfile(DV.curdir + 'conf' + DV.sep + 'conf.ini', DV.conf_file)
			DamnLoadConfig(forcemodules=True)
			DV.prefs = DamnVidPrefs()
			DV.prefs.set('checkforupdates', checkupdates)
			DV.prefs.save()
			self.buildTree()
			dlg = wx.MessageDialog(None, DV.l('DamnVid\'s configuration has been successfully reset.'), DV.l('Configuration reset'), wx.OK | wx.ICON_INFORMATION)
			dlg.SetIcon(DV.icon)
			dlg.ShowModal()
		dlg.Destroy()
	def onImport(self, event):
		dlg = wx.FileDialog(None, DV.l('Where is located the configuration file to import?'), DV.prefs.get('lastprefdir'), 'DamnVid-' + DV.version + '-configuration.ini', DV.l('locale:browse-ini-files'), wx.FD_OPEN)
		dlg.SetIcon(DV.icon)
		if dlg.ShowModal() == wx.ID_OK:
			self.tree.SelectItem(self.treeroot, True)
			path = dlg.GetPath()
			dlg.Destroy()
			DV.prefs.set('lastprefdir', path)
			f = DamnOpenFile(path, 'r')
			testprefs = ConfigParser.SafeConfigParser()
			allOK = False
			try:
				testprefs.readfp(f)
				f.close()
				allOK = True
			except:
				try:
					f.close()
				except:
					pass
				dlg = wx.MessageDialog(None, DV.l('Invalid configuration file.'), DV.l('Invalid file'), wx.OK | wx.ICON_ERROR)
				dlg.SetIcon(DV.icon)
				dlg.ShowModal()
				dlg.Destroy()
			if allOK:
				keepgoing = True
				while keepgoing:
					keepgoing = DV.prefs.remp(0) is not None
				for i in testprefs.sections():
					try:
						DV.prefs.ini.add_section(i)
					except:
						pass
					for j in testprefs.options(i):
						DV.prefs.sets(i, j, testprefs.get(i, j))
				self.parent.reopenprefs = True
				self.onOK(None)
		else:
			dlg.Destroy()
	def onExport(self, event):
		dlg = wx.FileDialog(None, DV.l('Where do you want to export DamnVid\'s configuration?'), DV.prefs.get('lastprefdir'), 'DamnVid-' + DV.version + '-configuration.ini', DV.l('locale:browse-ini-files'), wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
		dlg.SetIcon(DV.icon)
		if dlg.ShowModal() == wx.ID_OK:
			path = dlg.GetPath()
			DV.prefs.set('lastprefdir', path)
			f = DamnOpenFile(path, 'w')
			DV.prefs.ini.write(f)
			f.close()
		dlg.Destroy()
	def onKeyDown(self, event):
		if event.GetKeyCode() in (wx.WXK_ESCAPE, wx.WXK_CANCEL):
			self.onClose(event)
		elif event.GetKeyCode() in (wx.WXK_NUMPAD_ENTER, wx.WXK_RETURN, wx.WXK_EXECUTE):
			self.onOK(event)
	def onClose(self, event):
		DV.prefs = DamnVidPrefs() # Reload from ini
		self.Close(True)
