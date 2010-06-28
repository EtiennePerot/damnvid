# -*- coding: utf-8 -*-
from dUI import *
class DamnEEgg(wx.Dialog):
	def __init__(self, parent, id):
		wx.Dialog.__init__(self, parent, id, DV.l('Salute the Secret Stoat!'))
		topvbox = wx.BoxSizer(wx.VERTICAL)
		self.SetSizer(topvbox)
		self.panel = wx.Panel(self, -1)
		topvbox.Add(self.panel, 1, wx.EXPAND)
		self.vbox = wx.BoxSizer(wx.VERTICAL)
		self.panel.SetSizer(self.vbox)
		self.vbox.Add(wx.StaticBitmap(self.panel, -1, wx.Bitmap(DV.images_path + 'stoat.jpg')), 0, wx.ALIGN_CENTER)
		self.AddText(DV.l('DamnVid ') + DV.version + DV.l(' is *100% stoat-powered*, and *proud* of it.'), True)
		self.AddText(DV.l('*No stoats were harmed* (much) during DamnVid\'s development. Ya rly.'), True)
		self.vbox.Add((0, 5))
		self.AddText(DV.l('Praise the *Secret Stoat* and all it stands for: *WIN*.'), True)
		self.vbox.Add((0, 5))
		self.AddText(DV.l('Definitions of *WIN* on the Web:'), True)
		self.vbox.Add((0, 5))
		self.AddText(DV.l('- be the winner in a contest or competition; be victorious; "He won the Gold Medal in skating"; "Our home team won"; "Win the game"'))
		self.AddText(DV.l('- acquire: win something through one\'s efforts; "I acquired a passing knowledge of Chinese"; "Gain an understanding of international finance"'))
		self.AddText(DV.l('- gain: obtain advantages, such as points, etc.; "The home team was gaining ground"'))
		self.AddText(DV.l('- a victory (as in a race or other competition); "he was happy to get the win"'))
		self.AddText(DV.l('- winnings: something won (especially money)'))
		self.AddText(DV.l('- succeed: attain success or reach a desired goal; "The enterprise succeeded"; "We succeeded in getting tickets to the show"; "she struggled to overcome her handicap and won"'))
		btn = wx.Button(self.panel, -1, DV.l('Secret Stoat!'))
		self.vbox.Add(btn, 0, wx.ALIGN_CENTER)
		self.Bind(wx.EVT_BUTTON, self.onBtn, btn)
		self.SetClientSize(self.panel.GetBestSize())
		self.Center()
	def AddText(self, s, center=False):
		strings = ['']
		for i in s:
			if i == '*':
				strings.append('')
			else:
				strings[-1] += i
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		bold = False
		sysfont = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
		normfont = wx.Font(sysfont.GetPointSize(), sysfont.GetFamily(), sysfont.GetStyle(), sysfont.GetWeight())
		boldfont = wx.Font(sysfont.GetPointSize(), sysfont.GetFamily(), sysfont.GetStyle(), wx.FONTWEIGHT_BOLD)
		for i in strings:
			t = wx.StaticText(self.panel, -1, i)
			t.Wrap(500)
			if bold:
				t.SetFont(boldfont)
			else:
				t.SetFont(normfont)
			bold = not bold
			hbox.Add(t)
		if center:
			self.vbox.Add(hbox, 0, wx.ALIGN_CENTER)
		else:
			self.vbox.Add(hbox, 0)
	def onBtn(self, event):
		self.Close(True)
class DamnAboutDamnVid(wx.Dialog):
	def __init__(self, parent, id, main):
		self.parent = main
		wx.Dialog.__init__(self, parent, id, DV.l('About DamnVid ') + DV.version)
		absbox1 = wx.BoxSizer(wx.VERTICAL)
		absbox2 = wx.BoxSizer(wx.HORIZONTAL)
		self.SetSizer(absbox1)
		absbox1.Add((0, DV.border_padding))
		absbox1.Add(absbox2)
		absbox1.Add((0, DV.border_padding))
		topvbox = wx.BoxSizer(wx.VERTICAL)
		absbox2.Add((DV.border_padding, 0))
		absbox2.Add(topvbox)
		absbox2.Add((DV.border_padding, 0))
		panel = wx.Panel(self, -1)
		topvbox.Add(panel, 1, wx.EXPAND)
		hbox = wx.BoxSizer(wx.HORIZONTAL)
		panel.SetSizer(hbox)
		vbox1 = wx.BoxSizer(wx.VERTICAL)
		hbox.Add(vbox1, 0, wx.EXPAND)
		vbox2 = wx.BoxSizer(wx.VERTICAL)
		hbox.Add(vbox2, 1, wx.EXPAND)
		icon = wx.StaticBitmap(panel, -1, wx.Bitmap(DV.images_path + 'icon256.png'))
		icon.Bind(wx.EVT_LEFT_DCLICK, self.eEgg)
		vbox1.Add(icon, 1, wx.ALIGN_CENTER)
		title = wx.StaticText(panel, -1, DV.l('DamnVid ') + DV.version)
		title.SetFont(wx.Font(20, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
		vbox2.Add(title)
		vbox2.Add((0, DV.border_padding * 2))
		author = wx.StaticText(panel, -1, DV.l('By Etienne Perot'))
		author.SetFont(wx.Font(16, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
		vbox2.Add(author)
		vbox2.Add((0, DV.border_padding * 2))
		vbox2.Add(DamnHyperlink(panel, -1, DV.url, DV.url))
		vbox2.Add(wx.StaticText(panel, -1, DV.l('Contributors:')))
		vbox2.Add(wx.StaticText(panel, -1, DV.l('- Andreas Noteng (Packaging)')))
		vbox2.Add(wx.StaticText(panel, -1, DV.l('- Palmer (Graphics)')))
		vbox2.Add(wx.StaticText(panel, -1, DV.l('- Benoit Philippe (Testing)')))
		vbox2.Add(wx.StaticText(panel, -1, DV.l('Special thanks to:')))
		vbox2.Add(wx.StaticText(panel, -1, DV.l('- The FFmpeg team')))
		vbox2.Add(wx.StaticText(panel, -1, DV.l('- Every stoat on the planet')))
		vbox2.Add(wx.StaticText(panel, -1, DV.l('- You!')))
		for l in DV.languages.iterkeys():
			if DV.lang == l and DV.languages[l].has_key('author'):
				vbox2.Add((0, DV.border_padding))
				vbox2.Add(wx.StaticText(panel, -1, DV.l('Translation:')))
				vbox2.Add(wx.StaticText(panel, -1, DamnUnicode(DV.languages[l]['author'])))
		vbox2.Add((0, DV.border_padding * 2))
		hbox2 = wx.BoxSizer(wx.HORIZONTAL)
		vbox2.Add(hbox2, 0, wx.ALIGN_RIGHT)
		okButton = wx.Button(panel, -1, DV.l('OK'))
		self.Bind(wx.EVT_BUTTON, self.onOK, okButton)
		hbox2.Add(okButton)
		self.SetClientSize(self.GetBestSize())
		self.Layout()
		self.Center()
	def eEgg(self, event):
		dlg = DamnEEgg(None, -1)
		dlg.SetIcon(DV.icon)
		dlg.ShowModal()
		dlg.Destroy()
	def onOK(self, event):
		self.Close(True)
