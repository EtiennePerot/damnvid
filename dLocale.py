# -*- coding: utf-8 -*-
from dCore import *
from dLog import *
def DamnLocale(s, warn=True, reverse=False):
	s = DamnUnicode(s)
	if DV.locale is None:
		Damnlog('Locale warning: Locale is None.')
		return s
	if reverse:
		for i in DV.locale['strings'].iterkeys():
			if DV.locale['strings'][i] == s:
				return i
		Damnlog('Reverse locale lookup atempt for:', s, 'failed for language', DV.lang)
		return s
	if not DV.locale['strings'].has_key(s):
		if warn and s not in DV.locale_warnings:
			DV.locale_warnings.append(s)
			Damnlog('Locale warning:', s, 'has no key for language', DV.lang)
		return s
	return DamnUnicode(DV.locale['strings'][s])
def DamnLoadCurrentLocale():
	if DV.languages.has_key(DV.lang):
		DV.locale = DV.languages[DV.lang]
	else:
		DV.locale = None
def DamnLocaleInit():
	Damnlog('Loading locales.')
	DV.languages = {}
	DV.l = DamnLocale # Function shortcut
	DV.locale = None
	DV.lang = 'English' # Default, will be overriden later if needed.
	for i in os.listdir(DV.locale_path):
		if i[-7:].lower() == '.locale':
			Damnlog('Loading locale', DV.locale_path + i)
			DamnExecFile(DV.locale_path + i, globs=globals())
	DamnLoadCurrentLocale()
