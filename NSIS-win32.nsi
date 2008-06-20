!include "MUI.nsh"
!define APP "DamnVid"
!define URL "http://code.google.com/p/damnvid/"
name "${APP}"
caption "${APP} installation"
outFile "${APP}-setup.exe"
installDir "$PROGRAMFILES\${APP}\"
RequestExecutionLevel user
!define MUI_HEADERIMAGE
!define MUI_ABORTWARNING
!define MUI_COMPONENTSPACE_SMALLDESC
!define MUI_HEADERIMAGE_BITMAP_NOSTRETCH
!define MUI_FINISHPAGE
!define MUI_FINISHPAGE_TEXT "Thank you for installing ${APP}. No more of these Damn unreadable videos."
!insertmacro MUI_PAGE_WELCOME
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
writeUninstaller "$INSTDIR\uninstall.exe"
!insertmacro MUI_STARTMENU_WRITE_BEGIN Application
createDirectory "$SMPROGRAMS\$StartMenuFolder"
createShortCut "$SMPROGRAMS\$StartMenuFolder\${APP}.lnk" "$INSTDIR\${APP}.exe"
createShortCut "$SMPROGRAMS\$StartMenuFolder\Uninstall.lnk" "$INSTDIR\uninstall.exe"
!insertmacro MUI_STARTMENU_WRITE_END
WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP}" "DisplayName" "${APP}"
WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP}" "UninstallString" "$INSTDIR\uninstall.exe"
WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP}" "URLUpdateInfo" "${URL}"
WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP}" "URLInfoAbout" "${URL}"
WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP}" "HelpLink" "${URL}"
WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP}" "DisplayIcon" "$INSTDIR\img\icon.ico"
WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP}" "NoModify" 1
WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP}" "NoRepair" 1
sectionEnd
section "Uninstall"
delete "$INSTDIR\uninstall.exe"
rmDir "$INSTDIR"
!insertmacro MUI_STARTMENU_GETFOLDER Application $StartMenuFolder
delete "$SMPROGRAMS\$StartMenuFolder\${APP}.lnk"
delete "$SMPROGRAMS\$StartMenuFolder\Uninstall.lnk"
rmDir "$SMPROGRAMS\$StartMenuFolder"
DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP}"
DeleteRegKey HKCU "Software\${APP}"
sectionEnd