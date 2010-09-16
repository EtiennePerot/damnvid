# -*- coding: utf-8 -*-
from dUI import *
class DamnAddURLDialog(wx.Dialog):
	def __init__(self, parent, default):
		self.parent = parent
		wx.Dialog.__init__(self, parent, -1, DV.l('Add videos by URL...'))
		absolutetopsizer = wx.BoxSizer(wx.HORIZONTAL)
		self.SetSizer(absolutetopsizer)
		innertopsizer = wx.BoxSizer(wx.HORIZONTAL)
		innertopsizer2 = wx.BoxSizer(wx.VERTICAL)
		self.toppanel = wx.Panel(self, -1)
		absolutetopsizer.Add(self.toppanel, 1, wx.EXPAND)
		self.toppanel.SetSizer(innertopsizer)
		topsizer = wx.BoxSizer(wx.VERTICAL)
		innertopsizer.Add((DV.border_padding, 0))
		innertopsizer.Add(innertopsizer2, 1, wx.EXPAND)
		innertopsizer.Add((DV.border_padding, 0))
		innertopsizer2.Add((0, DV.border_padding))
		innertopsizer2.Add(topsizer, 1, wx.EXPAND)
		innertopsizer2.Add((0, DV.border_padding))
		# Finished paddings and stuff, now for the actual dialog construction
		topsizer.Add(wx.StaticText(self.toppanel, -1, DV.l('Enter the URL of the video you wish to download.')))
		topsizer.Add((0, DV.control_vgap))
		urlboxsizer = wx.BoxSizer(wx.HORIZONTAL)
		topsizer.Add(urlboxsizer, 0, wx.EXPAND)
		urllabel = wx.StaticText(self.toppanel, -1, DV.l('URL:'))
		urlboxsizer.Add(urllabel, 0, wx.ALIGN_CENTER_VERTICAL)
		urlboxsizer.Add((DV.control_hgap, 0))
		self.urlbox = wx.TextCtrl(self.toppanel, -1, default, style=wx.TE_PROCESS_ENTER)
		urlboxsizer.Add(self.urlbox, 1, wx.EXPAND)
		self.urlbox.Bind(wx.EVT_TEXT_ENTER, self.onAdd)
		self.urlbox.Bind(wx.EVT_KEY_DOWN, self.onKeyDown)
		urlboxsizer.Add((DV.control_hgap, 0))
		self.addButton = wx.Button(self.toppanel, -1, '+')
		urlboxsizer.Add(self.addButton, 0)
		btnheight = self.addButton.GetSizeTuple()[1]
		self.addButton.SetMinSize((btnheight, btnheight)) # Makes the button have a 1:1 aspect ratio
		self.addButton.Bind(wx.EVT_BUTTON, self.onAdd)
		topsizer.Add((0, DV.control_vgap))
		autoconvertchecksizer = wx.BoxSizer(wx.HORIZONTAL)
		self.autoconvertcheck = wx.CheckBox(self.toppanel, -1, DV.l('Automatically download and convert right away'))
		self.autoconvertcheck.SetValue(DV.prefs.get('autoconvert') == 'True')
		self.autoconvertcheck.Bind(wx.EVT_CHECKBOX, self.onAutoconvertCheck)
		autoconvertchecksizer.Add((DV.control_hgap + urllabel.GetSizeTuple()[0], 0))
		autoconvertchecksizer.Add(self.autoconvertcheck)
		topsizer.Add(autoconvertchecksizer, 0, wx.EXPAND)
		topsizer.Add((0, DV.control_vgap))
		topsizer.Add(wx.StaticLine(self.toppanel, -1, style=wx.HORIZONTAL), 0, wx.EXPAND)
		topsizer.Add((0, DV.control_vgap))
		# Start building the bottom part, put sizers in place...
		bottomhorizontalsizer = wx.BoxSizer(wx.HORIZONTAL)
		topsizer.Add(bottomhorizontalsizer, 1, wx.EXPAND)
		bottomleftsizer = wx.BoxSizer(wx.VERTICAL)
		bottomhorizontalsizer.Add(bottomleftsizer, 1, wx.EXPAND | wx.ALIGN_TOP)
		bottomhorizontalsizer.Add((DV.control_hgap, 0))
		bottomhorizontalsizer.Add(wx.StaticLine(self.toppanel, -1, style=wx.VERTICAL), 0, wx.EXPAND | wx.ALIGN_TOP)
		bottomhorizontalsizer.Add((DV.control_hgap, 0))
		bottomrightsizer = wx.BoxSizer(wx.VERTICAL)
		bottomhorizontalsizer.Add(bottomrightsizer, 1, wx.EXPAND | wx.ALIGN_TOP)
		# Now start building the bottom-left part
		bottomleftsizer.Add(wx.StaticText(self.toppanel, -1, DV.l('Go ahead, add some videos!')))
		bottomleftsizer.Add((0, DV.control_vgap))
		bottomleftsizer.Add(wx.StaticText(self.toppanel, -1, DV.l('The following sites are supported:')))
		scrollinglist = wx.ScrolledWindow(self.toppanel, -1)
		scrollinglistsizer = wx.BoxSizer(wx.VERTICAL)
		scrollinglist.SetSizer(scrollinglistsizer)
		bottomleftsizer.Add(scrollinglist, 1, wx.EXPAND)
		for i in DamnIterModules(False):
			if i.has_key('sites'):
				for site in i['sites']:
					scrollinglistsizer.Add((0, DV.control_vgap))
					sitesizer = wx.BoxSizer(wx.HORIZONTAL)
					scrollinglistsizer.Add(sitesizer)
					sitesizer.Add(wx.StaticBitmap(scrollinglist, -1, wx.Bitmap(DV.modules_path + i['name'] + DV.sep + site['icon'])), 0, wx.ALIGN_CENTER_VERTICAL)
					sitesizer.Add((DV.control_hgap, 0))
					sitesizer.Add(DamnHyperlink(scrollinglist, -1, site['title'], site['url']), 0, wx.ALIGN_CENTER_VERTICAL)
		scrollinglist.SetMinSize((-1, 220))
		scrollinglist.SetScrollbars(0, DV.control_vgap * DV.scroll_factor, 0, 0)
		# Now start building the bottom-right part
		self.monitorcheck = wx.CheckBox(self.toppanel, -1, DV.l('Monitor clipboard for new URLs'))
		self.monitorcheck.Bind(wx.EVT_CHECKBOX, self.onMonitorCheck)
		self.monitorcheck.SetValue(DV.prefs.get('clipboard') == 'True')
		bottomrightsizer.Add(self.monitorcheck)
		bottomrightsizer.Add((0, DV.control_vgap))
		self.monitorlabel = wx.StaticText(self.toppanel, -1, '')
		bottomrightsizer.Add(self.monitorlabel)
		bottomrightsizer.Add((0, DV.control_vgap))
		self.monitorlabel2 = wx.StaticText(self.toppanel, -1, '')
		bottomrightsizer.Add(self.monitorlabel2)
		self.onMonitorCheck()
		bottomrightsizer.Add((0, DV.control_vgap))
		self.videolist = DamnList(self.toppanel, self)
		il = wx.ImageList(16, 16, True)
		for i in range(DV.listicons.GetImageCount()):
			il.Add(DV.listicons.GetBitmap(i))
		self.videolist.AssignImageList(il, wx.IMAGE_LIST_SMALL)
		bottomrightsizer.Add(self.videolist, 1, wx.EXPAND)
		self.videocolumn = self.videolist.InsertColumn(ID_COL_VIDNAME, DV.l('Videos'))
		# We're done! Final touches...
		self.videos = []
		self.SetClientSize(self.toppanel.GetBestSize())
		self.Center()
		self.Bind(wx.EVT_KEY_DOWN, self.onKeyDown, self.toppanel)
		self.Bind(wx.EVT_CLOSE, self.onClose)
	def onAdd(self, event=None, val=None):
		if val is None:
			val = self.urlbox.GetValue()
			self.urlbox.SetValue('')
		message = None
		if not val:
			message = (DV.l('No URL entered'), DV.l('You must enter a URL!'))
		elif not self.parent.validURI(val):
			message = (DV.l('Invalid URL'), DV.l('This is not a valid URL!'))
		if message is not None:
			dlg = wx.MessageDialog(None, message[1], message[0], wx.OK | wx.ICON_EXCLAMATION)
			dlg.SetIcon(DV.icon)
			dlg.ShowModal()
			dlg.Destroy()
			return
		self.videolist.InsertStringItem(len(self.videos), val)
		self.videolist.SetItemImage(len(self.videos), DamnGetListIcon('generic'), DamnGetListIcon('generic'))
		self.videos.append(val)
		self.parent.addVid([val], None)
		self.urlbox.SetFocus()
	def update(self, original, name, icon):
		for i in range(len(self.videos)):
			if self.videos[i] == original:
				self.videolist.SetStringItem(i, self.videocolumn, name)
				self.videolist.SetItemImage(i, DamnGetListIcon(icon), DamnGetListIcon(icon))
	def onAutoconvertCheck(self, event=None):
		DV.prefs.set('autoconvert', str(self.autoconvertcheck.GetValue()))
	def onMonitorCheck(self, event=None):
		newpref = self.monitorcheck.GetValue()
		DV.prefs.set('clipboard', str(newpref))
		if newpref:
			self.monitorlabel.SetLabel(DV.l('Your clipboard is being monitored.'))
			self.monitorlabel2.SetLabel(DV.l('Simply copy a video URL and DamnVid will add it.'))
		else:
			self.monitorlabel.SetLabel(DV.l('Your clipboard is not being monitored.'))
			self.monitorlabel2.SetLabel(DV.l('Check the checkbox above if you want it to be monitored.'))
		self.monitorlabel.Wrap(180)
		self.monitorlabel2.Wrap(180)
		self.toppanel.Layout()
	def onKeyDown(self, event):
		if event.GetKeyCode() in (wx.WXK_ESCAPE, wx.WXK_CANCEL):
			self.onClose(event)
		else:
			event.Skip() # Let the event slide, otherwise the key press isn't even registered
	def onClose(self, event):
		DV.prefs.save() # Save eventually-changed-with-the-checkboxes prefs
		self.Destroy()
