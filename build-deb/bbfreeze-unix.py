#!/usr/bin/env python
# -*- coding: utf-8 -*-
from bbfreeze import Freezer

bbFreeze_Class=Freezer('package')
bbFreeze_Class.addScript('DamnVid.py',gui_only=True)
bbFreeze_Class.use_compression=1
bbFreeze_Class.include_py=True
bbFreeze_Class()
