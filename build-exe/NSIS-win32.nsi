!include "MUI2.nsh"
!define APP "DamnVid"
!define URL "http://code.google.com/p/damnvid/"
!define HALPPAGE "http://code.google.com/p/damnvid/wiki/Help"
name "${APP}"
caption "${APP} installation"
SetCompressor lzma
outFile "..\..\${APP}-setup.exe"
installDir "$PROGRAMFILES\${APP}"
RequestExecutionLevel admin
!define MUI_ICON "..\..\img\installer.noinclude.ico"
!define MUI_UNICON "..\..\img\uninstaller.noinclude.ico"
!define MUI_HEADERIMAGE
!define MUI_HEADERIMAGE_BITMAP "..\..\img\installheader.bmp"
!define MUI_HEADERIMAGE_UNBITMAP "..\..\img\uninstallheader.bmp"
!define MUI_ABORTWARNING
!define MUI_COMPONENTSPACE_SMALLDESC
!define MUI_HEADERIMAGE_BITMAP_NOSTRETCH
!define MUI_FINISHPAGE
!define MUI_FINISHPAGE_TEXT "Thank you for installing ${APP}. No more of these damn unreadable videos."
!define MUI_FINISHPAGE_RUN "$INSTDIR\DamnVid.exe"
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "COPYING"
!insertmacro MUI_PAGE_DIRECTORY
# Begin Start menu config
Var StartMenuFolder
!define MUI_STARTMENUPAGE_REGISTRY_ROOT "HKCU"
!define MUI_STARTMENUPAGE_REGISTRY_KEY "Software\${APP}"
!define MUI_STARTMENUPAGE_REGISTRY_VALUENAME "Start Menu Folder"
!insertmacro MUI_PAGE_STARTMENU Application $StartMenuFolder
# End Start menu config
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH
!insertmacro MUI_LANGUAGE "English"
BrandingText " "
section
setOutPath "$INSTDIR"
setOverwrite try
writeUninstaller "$INSTDIR\uninstall.exe"
!insertmacro MUI_STARTMENU_WRITE_BEGIN Application
createDirectory "$SMPROGRAMS\$StartMenuFolder"
createShortCut "$SMPROGRAMS\$StartMenuFolder\${APP}.lnk" "$INSTDIR\${APP}.exe"
createShortCut "$SMPROGRAMS\$StartMenuFolder\Uninstall.lnk" "$INSTDIR\uninstall.exe"
!insertmacro MUI_STARTMENU_WRITE_END
file "gdiplus.dll"
file "unicows.dll"
file "MSVCR71.dll"
file "MSVCP71.dll"
<files>
WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP}" "DisplayName" "${APP}"
WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP}" "UninstallString" "$INSTDIR\uninstall.exe"
WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP}" "URLUpdateInfo" "${URL}"
WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP}" "URLInfoAbout" "${URL}"
WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP}" "HelpLink" "${URL}"
WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP}" "DisplayIcon" "$INSTDIR\img\icon.ico"
WriteRegStr HKCR ".damnvid" "" "DamnVid.file"
WriteRegStr HKCR "DamnVid.file" "" "DamnVid file"
WriteRegStr HKCR "DamnVid.file\DefaultIcon" "" "$\"$INSTDIR\img\iconfile.ico$\""
WriteRegStr HKCR "DamnVid.file\Shell" "" ""
WriteRegStr HKCR "DamnVid.file\Shell\Open" "" ""
WriteRegStr HKCR "DamnVid.file\Shell\Open\Command" "" "$\"$INSTDIR\DamnVid.exe$\" $\"%1$\""
WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP}" "NoModify" 1
WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP}" "NoRepair" 1
sectionEnd
section "Uninstall"
delete "$INSTDIR\gdiplus.dll"
delete "$INSTDIR\unicows.dll"
delete "$INSTDIR\MSVCR71.dll"
delete "$INSTDIR\MSVCP71.dll"
<delete>
delete "$INSTDIR\uninstall.exe"
rmDir /r "$INSTDIR"
!insertmacro MUI_STARTMENU_GETFOLDER Application $StartMenuFolder
delete "$SMPROGRAMS\$StartMenuFolder\${APP}.lnk"
delete "$SMPROGRAMS\$StartMenuFolder\Uninstall.lnk"
rmDir "$SMPROGRAMS\$StartMenuFolder"
DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP}"
DeleteRegKey HKCU "Software\${APP}"
DeleteRegKey HKCR ".damnvid"
DeleteRegKey HKCR "DamnVid.file"
sectionEnd