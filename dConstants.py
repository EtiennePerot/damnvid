# -*- coding: utf-8 -*-
import re
# Begin ID constants
ID_COL_VIDNAME = 0
ID_COL_VIDPROFILE = 1
ID_COL_VIDSTAT = 2
ID_COL_VIDPATH = 3
# Begin regex constants
REGEX_PATH_MULTI_SEPARATOR_CHECK = re.compile('/+')
REGEX_FFMPEG_DURATION_EXTRACT = re.compile('^\\s*Duration:\\s*(\\d+):(\\d\\d):([.\\d]+)', re.IGNORECASE)
REGEX_FFMPEG_TIME_EXTRACT = re.compile('time=([.\\d]+)', re.IGNORECASE)
REGEX_FILENAME_SANE_CHARACTERS = re.compile('[-+/a-z _=~.,\\d]', re.IGNORECASE)
REGEX_SHELLARG_SAFE = re.compile(r'^[-+/\w_=~.,]+$', re.IGNORECASE)
REGEX_HTTP_GENERIC = re.compile('^https?://(?:[-_\w]+\.)+\w{2,4}(?:[/?][-_+&^%$=`~?.,/:;{}#\w]*)?$', re.IGNORECASE)
REGEX_HTTP_GENERIC_LOOSE = re.compile('https?://(?:[-_\w]+\.)+\w{2,4}(?:[/?][-_+&^%$=`~?.,/:;{}\w]*)?', re.IGNORECASE)
REGEX_HTTP_EXTRACT_FILENAME = re.compile('^.*/|[?#].*$')
REGEX_HTTP_EXTRACT_DIRNAME = re.compile('^([^?#]*)/.*?$')
REGEX_FILE_CLEANUP_FILENAME = re.compile('[\\/:?"|*<>]+')
REGEX_URI_EXTENSION_EXTRACT = re.compile('^(?:[^?|<>]+[/\\\\])?[^/\\\\|?<>#]+\\.(\\w{1,3})(?:$|[^/\\\\\\w].*?$)')
REGEX_HTTP_GENERIC_TITLE_EXTRACT = re.compile('<title>([^<>]+)</title>', re.IGNORECASE)
REGEX_THOUSAND_SEPARATORS = re.compile('(?<=[0-9])(?=(?:[0-9]{3})+(?![0-9]))')
# End regex constants
# End constants