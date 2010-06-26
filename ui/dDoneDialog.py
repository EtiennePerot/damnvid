# -*- coding: utf-8 -*-
from dUI import *
class DamnDoneDialog(wx.Dialog):
	def __init__(self, content, aborted=False, main=None):
		Damnlog('Done dialog opening with parameters content =', content, '; aborted?', aborted)
		dirs = []
		files = {}
		icons = {}
		for i in content:
			if i[1] not in dirs:
				dirs.append(i[1])
				files[i[1]] = []
			files[i[1]].append(i[0])
			icons[i[1] + i[0]] = i[2]
		dirs.sort()
		for i in dirs:
			files[i].sort()
		Damnlog('Done dialog parsed content; dirs =', dirs, '; files =', files)
		self.parent = main
		title = 'Processing done.'
		if aborted:
			title = 'Processing aborted.'
		wx.Dialog.__init__(self, None, -1, DV.l(title))
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
		mainvbox = wx.BoxSizer(wx.VERTICAL)
		panel.SetSizer(mainvbox)
		# Build UI
		Damnlog('Building center UI of done dialog.')
		if aborted:
			title = wx.StaticText(panel, -1, DV.l('Video conversion aborted.'))
		elif len(content):
			title = wx.StaticText(panel, -1, DV.l('Video conversion successful.'))
		else:
			title = wx.StaticText(panel, -1, DV.l('Video conversion failed.'))
		title.SetFont(wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD))
		mainvbox.Add(title)
		mainvbox.Add((0, DV.border_padding * 2))
		if len(content):
			Damnlog('There is content, so we\'re gonna build tree.')
			mainvbox.Add(wx.StaticText(panel, -1, DV.l('The following videos have been processed:')))
			foldericon = wx.Bitmap(DV.images_path + 'foldermovie.png')
			for d in dirs:
				Damnlog('Building videos list for directory', d)
				tmpvbox = wx.BoxSizer(wx.VERTICAL)
				mainvbox.Add(tmpvbox)
				tmphbox = wx.BoxSizer(wx.HORIZONTAL)
				tmpvbox.Add(tmphbox)
				tmphbox.Add(DamnOmniElement(self, wx.StaticBitmap(panel, -1, foldericon), d), 0, wx.ALIGN_CENTER_VERTICAL)
				tmphbox.Add((DV.border_padding / 2, 0))
				tmphbox.Add(DamnOmniLink(self, panel, d))
				tmpinnerhbox = wx.BoxSizer(wx.HORIZONTAL)
				tmpvbox.Add(tmpinnerhbox)
				tmpinnerhbox.Add((foldericon.GetWidth() + DV.border_padding, 0))
				tmpinnervbox = wx.BoxSizer(wx.VERTICAL)
				tmpinnerhbox.Add(tmpinnervbox, 1)
				for f in files[d]:
					tmphbox2 = wx.BoxSizer(wx.HORIZONTAL)
					tmpinnervbox.Add(tmphbox2)
					tmphbox2.Add(DamnOmniElement(self, wx.StaticBitmap(panel, -1, DV.listicons.getRawBitmap(icons[d + f])), target=d+f), 0, wx.ALIGN_CENTER_VERTICAL)
					tmphbox2.Add((DV.border_padding / 2, 0))
					tmphbox2.Add(DamnOmniLink(self, panel, f, target=d+f))
				mainvbox.Add((0, DV.border_padding))
		else:
			Damnlog('There\'s no content, so we\'re not gonna build much.')
			mainvbox.Add(wx.StaticText(panel, -1, DV.l('No videos were processed.')))
			mainvbox.Add((0, DV.border_padding))
		mainvbox.Add((0, DV.border_padding)) # Again!
		okhbox = wx.BoxSizer(wx.HORIZONTAL)
		mainvbox.Add(okhbox, 0, wx.ALIGN_RIGHT)
		okButton = wx.Button(panel, wx.ID_OK, DV.l('OK'))
		okhbox.Add(okButton)
		self.Bind(wx.EVT_BUTTON, self.onOK, okButton)
		Damnlog('Finished building done dialog UI, displaying it.')
		# Finished building UI
		self.SetClientSize(self.GetBestSize())
		self.Center()
		Damnlog('Done dialog displayed and centered.')
	def onOK(self, event):
		self.Close(True)
