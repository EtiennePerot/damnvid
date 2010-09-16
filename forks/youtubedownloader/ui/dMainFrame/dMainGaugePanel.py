# -*- coding: utf-8 -*-
from ..dUI import *
from .orig_dMainGaugePanel import DamnMainGaugePanel as orig_DamnMainGaugePanel
from .orig_dMainGoPanel import DamnMainStopButton as orig_DamnMainStopButton

class DamnMainGaugePanel(orig_DamnMainGaugePanel):
	def __init__(self, parent):
		orig_DamnMainGaugePanel.__init__(self, parent)
		parent.stopbutton = orig_DamnMainStopButton(panel=self, parent=parent)
		# Todo: add button here