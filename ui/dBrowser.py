# -*- coding: utf-8 -*-
from dUI import *
from dConstants import *
from dLog import *
from dTubes import *
class DamnVidBrowser(wx.Dialog):
	def __init__(self, parent):
		Damnlog('Opening new YouTube browser dialog.')
		self.parent = parent
		wx.Dialog.__init__(self, parent, -1, DV.l('Search for videos...'))
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
		searchhbox = wx.BoxSizer(wx.HORIZONTAL)
		topvbox.Add(searchhbox, 0, wx.EXPAND)
		searchhbox.Add(wx.StaticText(self.toppanel, -1, DV.l('Search:')), 0, wx.ALIGN_CENTER_VERTICAL)
		searchhbox.Add((DV.control_hgap, 0))
		self.standardchoices = {
			'most_popular':DV.l('Most popular'),
			'most_viewed':DV.l('Most viewed'),
			'top_rated':DV.l('Top rated'),
			'recently_featured':DV.l('Recently featured'),
			'most_recent':DV.l('Most recent'),
			'most_discussed':DV.l('Most discussed'),
			'top_favorites':DV.l('Top favorites'),
			'most_linked':DV.l('Most linked'),
			'most_responded':DV.l('Most responded')
		}
		self.searchbox = wx.SearchCtrl(self.toppanel, -1, '', style=wx.TE_PROCESS_ENTER)
		self.searchbox.SetSearchMenuBitmap(wx.Bitmap(DV.images_path + 'searchctrl.png'))
		self.searchbox.Bind(wx.EVT_TEXT_ENTER, self.search)
		searchhbox.Add(self.searchbox, 1, wx.EXPAND | wx.ALIGN_CENTER_VERTICAL)
		self.searchbutton = wx.animate.GIFAnimationCtrl(self.toppanel, -1, DV.images_path + 'search.gif')
		self.searchbutton.Bind(wx.EVT_LEFT_DOWN, self.search)
		searchhbox.Add((DV.control_hgap, 0))
		searchhbox.Add(self.searchbutton, 0, wx.ALIGN_CENTER_VERTICAL)
		self.scrollpanel = wx.ScrolledWindow(self.toppanel, -1, size=(360, 270 + 3 * DV.control_vgap))
		self.scrollpanel.SetMinSize((360, 270 + 3 * DV.control_vgap))
		self.scrollpanel.SetScrollbars(0, DV.control_vgap * DV.scroll_factor, 0, 0)
		scrollpanelsizer = wx.BoxSizer(wx.HORIZONTAL)
		self.scrollpanel.SetSizer(scrollpanelsizer)
		self.resultpanel = wx.Panel(self.scrollpanel, -1)
		scrollpanelsizer.Add(self.resultpanel, 1, wx.EXPAND)
		self.resultsizer = wx.BoxSizer(wx.VERTICAL)
		self.resultpanel.SetSizer(self.resultsizer)
		topvbox.Add((0, DV.control_vgap))
		topvbox.Add(self.scrollpanel, 1, wx.EXPAND)
		self.Bind(wx.EVT_CLOSE, self.onClose)
		self.Bind(DV.evt_load, self.onLoad)
		self.buildSearchbox()
		self.loadlevel = 0
		self.results = []
		self.displayedurls = []
		self.resultctrls = []
		self.service = None
		self.scrollpanel.Hide()
		self.waitingpanel = wx.Panel(self.toppanel, -1, size=(360, 270 + 3 * DV.control_vgap))
		waitingsizer = wx.BoxSizer(wx.VERTICAL)
		self.waitingpanel.SetSizer(waitingsizer)
		waitingsizer.Add((0, int(DV.control_vgap * 1.5)))
		waitingsizer2 = wx.BoxSizer(wx.HORIZONTAL)
		waitingsizer.Add(waitingsizer2)
		waitingsizer2.Add((DV.control_hgap, 0))
		topvbox.Add(self.waitingpanel)
		self.searchingimg = wx.StaticBitmap(self.waitingpanel, -1, wx.Bitmap(DV.images_path + 'searchpanel.png'))
		waitingsizer2.Add(self.searchingimg)
		Damnlog('YouTube browser dialog has been built. Populating.')
		defaultsearch = DV.prefs.gets('damnvid-search', 'default_search')
		if defaultsearch and DV.prefs.gets('damnvid-search', 'doinitialsearch') == 'True':
			self.search(search=defaultsearch)
		else:
			pass
		topvbox.Add((0, DV.control_vgap))
		self.downloadAll = wx.Button(self.toppanel, -1, DV.l('Download all'))
		self.downloadAll.Bind(wx.EVT_BUTTON, self.onDownloadAll)
		topvbox.Add(self.downloadAll, 0, wx.ALIGN_RIGHT)
		topvbox.Add((0, DV.border_padding))
		self.SetClientSize(self.GetBestSize())
		self.Center()
		Damnlog('YouTube browser dialog init complete.')
	def cleanString(self, s):
		return DamnHtmlEntities(s)
	def getService(self):
		if self.service is None:
			self.service = DamnYouTubeService(self)
			self.service.start()
		else:
			try:
				if self.service.stillAlive():
					return self.service
			except:
				self.service = None
				return self.getService()
		return self.service
	def search(self, event=None, search=u''):
		Damnlog('YouTube browser is now searching for', search, 'from event', event)
		self.scrollpanel.Hide()
		self.waitingpanel.Show()
		self.toppanel.Layout()
		if not search:
			search = self.searchbox.GetValue()
		if not search:
			return
		search=DamnUnicode(search)
		self.searchbutton.LoadFile(DV.images_path + 'searching.gif')
		self.searchbutton.Play()
		Damnlog('YouTube browser interface updated and ready for search, resolving API query.')
		prefix = u'http://gdata.youtube.com/feeds/api/videos?racy=include&orderby=viewCount&vq='
		isstandard = False
		for i in self.standardchoices.keys():
			if DV.l(self.standardchoices[i], warn=False) == search:
				isstandard = True
				search = i
		if search in self.standardchoices.keys():
			Damnlog('Query is a standard choice:', search)
			prefix = u'http://gdata.youtube.com/feeds/api/standardfeeds/'
			searchlabel = self.standardchoices[search]
		else:
			Damnlog('Query is not a standard choice. Updating query history.')
			history = DV.prefs.geta('damnvid-search', 'history')
			if search not in history:
				history.append(search)
				while len(history) > int(DV.prefs.gets('damnvid-search', 'history_length')):
					history.pop(0)
			DV.prefs.seta('damnvid-search', 'history', history)
			searchlabel = search
		self.searchbox.SetValue(searchlabel)
		Damnlog('Youtube browser API prefix is', prefix)
		self.buildSearchbox()
		Damnlog('YouTube browser search box populating complete, beginning actual search for', search, 'at URL:', prefix + urllib2.quote(search.encode('utf8')))
		self.getService().query(('feed', DamnUnicode(prefix + urllib2.quote(search.encode('utf8')))))
		Damnlog('YouTube browser search results for', search, 'requested, preparing interface.')
		for i in self.resultctrls:
			i.Destroy()
		self.resultctrls = []
		self.scrollpanel.AdjustScrollbars()
		self.resultsizer.Clear(True)
		self.displayedurls = []
		Damnlog('Interface ready to receive results.')
	def onLoad(self, event):
		info = event.GetInfo()
		Damnlog('onLoad event on YouTube browser. Event data:', info)
		if info.has_key('newsearch'):
			self.onSearchPostEvent(info['newsearch'], event)
			return
		if info['query'][0] == 'feed':
			results = info['result']
			boldfont = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
			boldfont.SetWeight(wx.FONTWEIGHT_BOLD)
			tmpscrollbar = wx.ScrollBar(self.resultpanel, -1, style=wx.SB_VERTICAL)
			panelwidth = self.scrollpanel.GetSizeTuple()[0] - tmpscrollbar.GetSizeTuple()[0]
			tmpscrollbar.Destroy()
			del tmpscrollbar
			self.resultpanel.DestroyChildren()
			self.resultpanel.Layout()
			for i in range(len(results.entry)):
				tmpvbox = wx.BoxSizer(wx.VERTICAL)
				tmpsizer = wx.BoxSizer(wx.HORIZONTAL)
				tmpvbox.Add((0, DV.border_padding))
				tmpvbox.Add(tmpsizer)
				tmppanel = wx.Panel(self.resultpanel, -1, style=wx.SIMPLE_BORDER)
				self.resultctrls.append(tmppanel)
				tmppanel.SetBackgroundColour(wx.WHITE)
				tmppanel.SetMinSize((panelwidth, -1))
				self.resultsizer.Add(tmppanel)
				tmppanel.SetSizer(tmpvbox)
				tmpsizer.Add((DV.border_padding, 0))
				thumb = wx.animate.GIFAnimationCtrl(tmppanel, -1, DV.images_path + 'thumbnail.gif')
				self.getService().query(('image', results.entry[i].media.thumbnail[0].url, thumb))
				tmpsizer.Add(thumb)
				thumb.Play()
				tmpsizer.Add((DV.control_hgap, 0))
				infobox = wx.BoxSizer(wx.VERTICAL)
				tmpsizer.Add(infobox, 1, wx.EXPAND)
				tmpTitle = self.cleanString(results.entry[i].media.title.text)
				title = DamnHyperlink(tmppanel, -1, tmpTitle, self.cleanString(results.entry[i].media.player.url), wx.WHITE)
				while title.GetBestSizeTuple()[0] > 208:
					try:
						title.Destroy()
					except:
						Damnlog('!Failed to destroy old title hyperlink while attempting to fit it inside the YouTube browser.')
					tmpTitle = tmpTitle[:-8]
					title = DamnHyperlink(tmppanel, -1, tmpTitle + u'...', self.cleanString(results.entry[i].media.player.url), wx.WHITE)
				title.SetToolTip(wx.ToolTip(self.cleanString(results.entry[i].media.title.text)))
				infobox.Add(title)
				#infobox.Add((0,DV.control_vgap))
				desc = self.makeDescPanel(results.entry[i].media.description.text, tmppanel, panelwidth - 2 * DV.border_padding)
				tmpvbox.Add(desc, 0, wx.EXPAND)
				desc.Hide()
				videoinfo = wx.BoxSizer(wx.HORIZONTAL)
				infobox.Add(videoinfo)
				#infobox.Add((0,DV.control_vgap))
				tmplabel = wx.StaticText(tmppanel, -1, results.entry[i].media.category[0].text)
				tmplabel.SetFont(boldfont)
				tmplabel.SetForegroundColour(wx.BLACK)
				videoinfo.Add(tmplabel)
				tmplabel = wx.StaticText(tmppanel, -1, ', ')
				tmplabel.SetForegroundColour(wx.BLACK)
				videoinfo.Add(tmplabel)
				tmplabel = wx.StaticText(tmppanel, -1, self.sec2time(results.entry[i].media.duration.seconds))
				tmplabel.SetFont(boldfont)
				tmplabel.SetForegroundColour(wx.BLACK)
				videoinfo.Add(tmplabel)
				tmplabel = wx.StaticText(tmppanel, -1, '.')
				tmplabel.SetForegroundColour(wx.BLACK)
				videoinfo.Add(tmplabel)
				statistics = wx.BoxSizer(wx.HORIZONTAL)
				infobox.Add(statistics)
				infobox.Add((0, DV.control_vgap))
				statistics2 = wx.BoxSizer(wx.HORIZONTAL)
				infobox.Add(statistics2)
				try:
					viewcount = wx.StaticText(tmppanel, -1, self.numFormat(results.entry[i].statistics.view_count))
				except:
					viewcount = wx.StaticText(tmppanel, -1, self.numFormat(0))
				viewcount.SetFont(boldfont)
				viewcount.SetForegroundColour(wx.BLACK)
				statistics.Add(viewcount)
				tmplabel = wx.StaticText(tmppanel, -1, DV.l(' views.'))
				tmplabel.SetForegroundColour(wx.BLACK)
				statistics.Add(tmplabel)
				tmplabel = wx.StaticText(tmppanel, -1, DV.l('Rating: '))
				tmplabel.SetForegroundColour(wx.BLACK)
				statistics2.Add(tmplabel, 0, wx.ALIGN_CENTER_VERTICAL)
				if results.entry[i].rating is None:
					tmplabel = wx.StaticText(tmppanel, -1, DV.l('(None)'))
					tmplabel.SetForegroundColour(wx.BLACK)
					statistics2.Add(tmplabel, 0, wx.ALIGN_CENTER_VERTICAL)
				else:
					statistics2.Add(wx.StaticBitmap(tmppanel, -1, wx.Bitmap(DV.images_path + 'stars_' + str(int(round(float(results.entry[i].rating.average), 0))) + '.png')), 0, wx.ALIGN_CENTER_VERTICAL)
				infobox.Add((0, DV.control_vgap))
				buttonrow = wx.BoxSizer(wx.HORIZONTAL)
				infobox.Add(buttonrow)
				btnDesc = wx.Button(tmppanel, -1, DV.l('Description'))
				buttonrow.Add(btnDesc)
				buttonrow.Add((DV.control_hgap, 0))
				btnDesc.Bind(wx.EVT_BUTTON, DamnCurry(self.onDescButton, desc, tmppanel))
				btnDownload = wx.Button(tmppanel, -1, DV.l('Download'))
				btnDownload.Bind(wx.EVT_BUTTON, DamnCurry(self.onDownload, results.entry[i].media.player.url))
				self.displayedurls.append(results.entry[i].media.player.url)
				buttonrow.Add(btnDownload)
				tmpsizer.Add((DV.border_padding, 0))
				tmpvbox.Add((0, DV.border_padding))
				if i + 1 != len(results.entry):
					self.resultsizer.Add((0, DV.control_vgap))
					self.resultsizer.Add(wx.StaticLine(tmppanel, -1), 0, wx.EXPAND)
					self.resultsizer.Add((0, DV.control_vgap))
			self.waitingpanel.Hide()
			self.scrollpanel.Show()
			self.resultpanel.Fit()
			self.scrollpanel.AdjustScrollbars()
			self.resultpanel.Layout()
			self.toppanel.Layout()
		elif info['query'][0] == 'image':
			try:
				ctrl = info['query'][2]
				ctrl.Stop()
				ctrl.SetInactiveBitmap(wx.Bitmap(info['result']))
			except:
				pass
			try:
				os.remove(info['result'])
			except:
				pass
		elif info['query'][0] == 'done':
			try:
				self.service = None
				self.searchbutton.Stop()
				self.searchbutton.LoadFile(DV.images_path + 'search.gif')
			except:
				pass
	def buildSearchbox(self):
		Damnlog('Building search box on YouTube browser dialog.')
		val = self.searchbox.GetValue().strip().lower()
		Damnlog('Clean search box value is', val, '; Destroying boxmenu.')
		boxmenu = wx.Menu('')
		history = DV.prefs.geta('damnvid-search', 'history')
		Damnlog('Rebuilding history menu. History data:', history)
		if len(history):
			history.reverse() # Recent entries appear on top
			for i in history:
				item = wx.MenuItem(boxmenu, -1, i, kind=wx.ITEM_RADIO)
				boxmenu.AppendItem(item) # Once again, item has to be appended before being checked
				item.Check(i.lower() == val)
				boxmenu.Bind(wx.EVT_MENU, DamnCurry(self.onSearchMenu, i), item)
				self.Bind(wx.EVT_MENU, DamnCurry(self.onSearchMenu, i), item)
			item = wx.MenuItem(boxmenu, -1, DV.l('(Clear search history)'), kind=wx.ITEM_RADIO) # Ironic, but necessary to put this one as a radio, otherwise wx guesses that the menu is actually two separated radio menus
			boxmenu.AppendItem(item)
			boxmenu.Bind(wx.EVT_MENU, DamnCurry(self.onSearchMenu, None), item)
			self.Bind(wx.EVT_MENU, DamnCurry(self.onSearchMenu, None), item)
		Damnlog('History menu rebuilt, will now add standard choices.')
		for i in self.standardchoices.iterkeys():
			item = wx.MenuItem(boxmenu, -1, self.standardchoices[i], kind=wx.ITEM_RADIO)
			boxmenu.AppendItem(item)
			item.Check(i == val or self.standardchoices[i].lower() == val)
			boxmenu.Bind(wx.EVT_MENU, DamnCurry(self.onSearchMenu, i), item)
			self.Bind(wx.EVT_MENU, DamnCurry(self.onSearchMenu, i), item)
		Damnlog('History menu built, assigning it to search box.')
		self.searchbox.SetMenu(boxmenu)
	def onSearchMenu(self, query, event=None):
		Damnlog('YouTube browser dialog received onSearchMenu event. Query is', query)
		DV.postEvent(self, DamnLoadingEvent(DV.evt_loading, -1, {'newsearch':query})) # Fix wxPython on Linux bug: Need to be in a new event loop iteration to do the search (and potentially, menu rebuilding).
	def onSearchPostEvent(self, query, event=None):
		Damnlog('YouTube browser dialog received onSearchPostEvent event. Query is', query)
		if query is None: # Clear history
			DV.prefs.seta('damnvid-search', 'history', [])
			DV.prefs.save()
			Damnlog('Query is none, deleted history, rebuilding search box.')
			self.buildSearchbox()
		else:
			self.searchbox.SetValue(query)
			Damnlog('Query is not none, set searchbox value, starting search.')
			self.search()
	def makeDescPanel(self, desc, parent, width):
		Damnlog('Making description panel:', desc)
		if desc is None:
			Damnlog('Warning: description is None!')
			desc = u''
		desc = self.cleanString(desc)
		Damnlog('Cleaned string:', desc)
		panel = wx.Panel(parent, -1)
		panel.SetBackgroundColour(wx.WHITE)
		wrapper = wx.BoxSizer(wx.HORIZONTAL)
		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add((0, DV.control_vgap))
		wrapper.Add((DV.border_padding, 0))
		wrapper.Add(sizer)
		wrapper.Add((DV.border_padding, 0))
		panel.SetSizer(wrapper)
		descfont = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
		descfont.SetWeight(wx.FONTWEIGHT_BOLD)
		txt = wx.StaticText(panel, -1, DV.l('Description:'))
		txt.SetFont(descfont)
		txt.SetForegroundColour(wx.BLACK)
		sizer.Add(txt)
		descs = []
		lastindex = 0
		urls = []
		curmatch = 1
		for link in REGEX_HTTP_GENERIC_LOOSE.finditer(desc):
			before = desc[lastindex:link.start()].strip()
			if before:
				descs.extend((before, link.group()))
			else:
				descs.append(link.group())
				curmatch -= 1
			urls.append(curmatch)
			lastindex = link.end()
			curmatch += 2
		if not len(descs):
			descs = [desc]
		for i in range(len(descs)):
			if i in urls:
				link = DamnHyperlink(panel, -1, descs[i], descs[i], wx.WHITE)
				sizer.Add(link)
			else:
				txt = wx.StaticText(panel, -1, descs[i])
				txt.SetForegroundColour(wx.BLACK)
				txt.Wrap(width)
				sizer.Add(txt)
		return panel
	def sec2time(self, sec):
		t = (0, 0, int(sec))
		t = (t[0], (t[2] - t[2] % 60) / 60, t[2] % 60)
		t = (str((t[1] - t[1] % 60) / 60), str(t[1] % 60), str(t[2]))
		if t[0] == '0':
			return t[1] + ':' + self.numFormat(t[2], True)
		return t[0] + ':' + self.numFormat(t[1], True) + ':' + self.numFormat(t[2], True)
	def numFormat(self, num, doublezero=False):
		num = REGEX_THOUSAND_SEPARATORS.sub(',', str(num))
		if doublezero and len(num) == 1:
			num = '0' + num
		return num
	def onDownload(self, url, event):
		self.parent.addVid([url], DV.prefs.get('autoconvert') == 'True')
	def onDownloadAll(self, event):
		self.parent.addVid(self.displayedurls, DV.prefs.get('autoconvert') == 'True')
	def onDescButton(self, ctrl, panel, event):
		position = self.scrollpanel.GetViewStart()
		ctrl.Show(not ctrl.IsShown())
		panel.Fit()
		panel.Layout()
		self.resultpanel.Fit()
		self.scrollpanel.AdjustScrollbars()
		self.scrollpanel.Scroll(position[0], position[1])
	def onClose(self, event=None):
		self.parent.searchopen = False
		DV.prefs.save() # Saves search history
		self.Destroy()
