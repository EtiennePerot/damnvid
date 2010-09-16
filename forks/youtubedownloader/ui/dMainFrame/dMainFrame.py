# -*- coding: utf-8 -*-
from ..dUI import *
from .orig_dMainFrame import DamnMainFrame as orig_DamnMainFrame
from dMenubar import *
from dMainListPanel import *
from dMainSidePanel import *
from dMainGaugePanel import *
from dMainGoPanel import *

class DamnMainFrame(orig_DamnMainFrame): # The main window
	def setupGrid(self, panel):
		grid = wx.FlexGridSizer(2, 2, 8, 8)
		grid.Add(DamnMainListPanel(self), 1, wx.EXPAND)
		sidePanel = DamnMainSidePanel(self)
		grid.Add(sidePanel, 0, wx.EXPAND)
		#sidePanel.SetMinSize((DV.border_padding, -1))
		grid.Add(DamnMainGaugePanel(self), 0, wx.EXPAND)
		grid.Add((0, 0), 0, wx.EXPAND)
		panel.SetSizer(grid)
		grid.AddGrowableRow(0, 1)
		grid.AddGrowableCol(0, 1)
