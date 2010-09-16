# -*- coding: utf-8 -*-
from ..dUI import *
from .orig_dMainSidePanel import DamnMainSidePanel as orig_DamnMainSidePanel

class DamnMainSidePanel(orig_DamnMainSidePanel):
	def __init__(self, parent):
		orig_DamnMainSidePanel.__init__(self, parent)
		for e in self.GetChildren():
			e.Hide()
		self.Hide()
		#self.SetSize((0,0))
		#self.SetMinSize((0,0))
		#self.SetMaxSize((0,0))
