# -*- coding: utf-8 -*-
from dUI import *
from dLog import *

class DamnHistoryViewer(wx.Dialog):
	def __init__(self, main):
		wx.Dialog.__init__(self, main, -1, DV.l('History'))
		self.main = main
		topsizer = wx.BoxSizer(wx.VERTICAL)
		self.SetSizer(topsizer)
		self.toppanel = wx.Panel(self, -1)
		topsizer.Add(self.toppanel, 1, wx.EXPAND)
		topvbox = wx.BoxSizer(wx.VERTICAL)
		tophbox = wx.BoxSizer(wx.HORIZONTAL)
		self.toppanel.SetSizer(tophbox)
		tophbox.Add((DV.border_padding, 0))
		tophbox.Add(topvbox, 1, wx.EXPAND)
		tophbox.Add((DV.border_padding, 0))
		topvbox.Add((0, DV.border_padding))
		topvbox.Add(wx.StaticText(self.toppanel, -1, DV.l('History') + u':'), 0)
		topvbox.Add((0, DV.border_padding * 2))
		self.historyPanel = wx.ScrolledWindow(self.toppanel, -1, size = (400, 400), style=wx.SB_VERTICAL)
		self.historyPanel.SetMinSize((400, 400))
		tmpscroll = wx.ScrollBar(self.toppanel, -1, style=wx.SB_VERTICAL)
		self.scrollbarOffset = tmpscroll.GetSizeTuple()[0]
		tmpscroll.Destroy()
		del tmpscroll
		self.historyPanel.SetScrollbars(0, DV.control_vgap * DV.scroll_factor, 0, 0)
		topvbox.Add(self.historyPanel, 1, wx.EXPAND)
		self.historySizer = wx.BoxSizer(wx.VERTICAL)
		self.historyPanel.SetSizer(self.historySizer)
		bottomSizer = wx.BoxSizer(wx.HORIZONTAL)
		topvbox.Add(bottomSizer, 0, wx.EXPAND)
		self.deleteButton = wx.Button(self.toppanel, wx.ID_DELETE, DV.l('Clear history'))
		bottomSizer.Add(self.deleteButton, 0, wx.ALIGN_LEFT)
		self.Bind(wx.EVT_BUTTON, self.onClearHistory, self.deleteButton)
		bottomSizer.Add(wx.StaticText(self.toppanel, -1, ''), 1, wx.EXPAND)
		self.closeButton = wx.Button(self.toppanel, wx.ID_CLOSE, DV.l('Close'))
		bottomSizer.Add(self.closeButton, 0, wx.ALIGN_RIGHT)
		self.Bind(wx.EVT_BUTTON, self.onClose, self.closeButton)
		topvbox.Add((0, DV.border_padding))
		self.Bind(wx.EVT_CLOSE, self.onClose)
		self.update()
	def onClearHistory(self, event=None):
		Damnlog('onClearHistory event fired:', event)
		DV.prefs.seta('damnvid-videohistory','videos',[])
		DV.prefs.save()
		self.update()
	def onClose(self, event=None):
		Damnlog('History window close event:', event)
		try:
			self.main.onCloseHistory(event)
		except:
			Damnlog('History window could not notify parent that it has been closed.')
		self.Destroy()
	def addHistoryItem(self, uri, title, icon=None):
		Damnlog('Creating history item for URI', uri, 'with title', title, 'and icon', icon)
		tmpSizer = wx.BoxSizer(wx.HORIZONTAL)
		self.historySizer.Add(tmpSizer, 0, wx.EXPAND)
		if icon is not None:
			icon = DV.listicons.getRawBitmap(icon)
		else:
			icon = DV.listicons.getRawBitmap('fail')
		tmpSizer.Add(DamnOmniElement(self, wx.StaticBitmap(self.historyPanel, -1, icon), uri), 0)
		tmpSizer.Add((DV.border_padding / 2,0))
		titlelink = DamnOmniLink(self, self.historyPanel, title, uri)
		while titlelink.GetBestSizeTuple()[0] > 300:
			try:
				titlelink.Destroy()
			except:
				pass
			title = title[:-2]
			titlelink = DamnOmniLink(self, self.historyPanel, title, uri)
		tmpSizer.Add(titlelink, 0, wx.ALIGN_LEFT)
		tmpSizer.Add(wx.StaticText(self.historyPanel, -1, ''), 1)
		addButton = wx.Button(self.historyPanel, -1, '+', size = (24,24))
		self.Bind(wx.EVT_BUTTON, DamnCurry(self.onAdd, uri), addButton)
		tmpSizer.Add(addButton, 0)
		delButton = wx.Button(self.historyPanel, -1, '-', size = (24,24))
		self.Bind(wx.EVT_BUTTON, DamnCurry(self.onDel, uri), delButton)
		tmpSizer.Add(delButton, 0)
		#tmpSizer.Add((self.scrollbarOffset, 0))
	def onAdd(self, uri, event=None):
		self.main.onAddHistoryVideo(uri, event)
	def onDel(self, uri, event=None):
		uri = DamnUnicode(uri)
		Damnlog('Removing URI', uri,'from history.')
		history = DV.prefs.geta('damnvid-videohistory','videos')
		todrop = []
		for i in range(len(history)):
			video = history[i].split(DV.history_split)
			if len(video) != 3:
				todrop.append(i)
			elif video[0] == uri:
				Damnlog('Found URI', uri,'at index', i, 'in history.')
				todrop.append(i)
		if len(todrop):
			Damnlog('Dropping history entries:', todrop)
			todrop.reverse()
			for i in todrop:
				history = history[:i] + history[i+1:]
			DV.prefs.seta('damnvid-videohistory','videos',history)
			DV.prefs.save()
			self.update()
	def update(self):
		Damnlog('Clearing video history panel.')
		self.historySizer.DeleteWindows()
		self.historyPanel.DestroyChildren()
		history = DV.prefs.geta('damnvid-videohistory','videos')
		histsize = int(DV.prefs.get('videohistorysize'))
		Damnlog('Video history is',history,'; history size is',histsize)
		if not histsize:
			Damnlog('Histsize is zero.')
			self.historySizer.Add(wx.StaticText(self.historyPanel, -1, DV.l('The history feature has been disabled in the preferences.')))
		elif not len(history):
			Damnlog('History is empty.')
			self.historySizer.Add(wx.StaticText(self.historyPanel, -1, DV.l('The history is empty.')))
		else:
			Damnlog('Histsize is not 0, building history.')
			todrop = []
			for i in range(min(histsize,len(history))):
				video = history[i].split(DV.history_split)
				if len(video) != 3:
					Damnlog('Invalid length', len(video),'for history item', video,'; dropping', i)
					todrop.append(i)
				else:
					self.addHistoryItem(video[0], video[1], video[2])
			if len(todrop):
				Damnlog('Dropping history entries:', todrop)
				todrop.reverse()
				for i in todrop:
					history = history[:i] + history[i+1:]
				DV.prefs.seta('damnvid-videohistory','videos',history)
			Damnlog('Done building video history dialog.')
		# These silly recomputations are required for it to display (mostly) correctly (in Windows only, works fine elsewhere)
		self.historyPanel.Layout()
		self.toppanel.Layout()
		self.SetClientSize(self.toppanel.GetBestSize())
		self.historyPanel.AdjustScrollbars()
		self.historyPanel.Refresh()
