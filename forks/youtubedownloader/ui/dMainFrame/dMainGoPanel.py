# -*- coding: utf-8 -*-
from ..dUI import *
from .orig_dMainGoPanel import DamnMainGoPanel as orig_DamnMainGoPanel

class DamnMainGoPanel(orig_DamnMainGoPanel):
	def __init__(self, parent):
		orig_DamnMainGoPanel.__init__(self, parent)
		self.Hide()
