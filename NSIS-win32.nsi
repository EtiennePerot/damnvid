!include "MUI2.nsh"
!define APP "DamnVid"
!define URL "http://code.google.com/p/damnvid/"
!define HALPPAGE "http://code.google.com/p/damnvid/wiki/Help"
name "${APP}"
caption "${APP} installation"
outFile "..\..\${APP}-setup.exe"
installDir "$PROGRAMFILES\${APP}\"
RequestExecutionLevel admin
!define MUI_ICON "img\installer.ico"
!define MUI_UNICON "img\uninstaller.ico"
!define MUI_HEADERIMAGE
!define MUI_HEADERIMAGE_BITMAP "img\installheader.bmp"
!define MUI_HEADERIMAGE_UNBITMAP "img\uninstallheader.bmp"
!define MUI_ABORTWARNING
!define MUI_COMPONENTSPACE_SMALLDESC
!define MUI_HEADERIMAGE_BITMAP_NOSTRETCH
!define MUI_FINISHPAGE
!define MUI_FINISHPAGE_TEXT "Thank you for installing ${APP}. No more of these damn unreadable videos."
!define MUI_FINISHPAGE_RUN "$INSTDIR\DamnVid.exe"
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
setOverwrite try
writeUninstaller "$INSTDIR\uninstall.exe"
!insertmacro MUI_STARTMENU_WRITE_BEGIN Application
createDirectory "$SMPROGRAMS\$StartMenuFolder"
createShortCut "$SMPROGRAMS\$StartMenuFolder\${APP}.lnk" "$INSTDIR\${APP}.exe"
createShortCut "$SMPROGRAMS\$StartMenuFolder\Uninstall.lnk" "$INSTDIR\uninstall.exe"
!insertmacro MUI_STARTMENU_WRITE_END
file "DamnVid.exe"
file "DamnVid.exe.manifest"
file "gdiplus.dll"
file "unicows.dll"
file "MSVCR71.dll"
file "MSVCP71.dll"
file "w9xpopen.exe"
setOutPath "$INSTDIR\bin"
file "bin\ffmpeg.exe"
file "bin\SDL.dll"
setOutPath "$INSTDIR\conf"
file "conf\!readme.txt"
file "conf\conf.ini"
file "conf\default.ini"
setOutPath "$INSTDIR\img"
file "img\googlevideo.png"
file "img\icon256.png"
file "img\icon.ico"
file "img\online.png"
file "img\stoat.jpg"
file "img\veoh.png"
file "img\video.png"
file "img\youtube.png"
file "img\dailymotion.png"
setOutPath "$INSTDIR\output"
file "output\!readme.txt"
setOutPath "$INSTDIR\temp"
file "temp\!readme.txt"
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
delete "$INSTDIR\DamnVid.exe"
delete "$INSTDIR\DamnVid.exe.manifest"
delete "$INSTDIR\gdiplus.dll"
delete "$INSTDIR\unicows.dll"
delete "$INSTDIR\MSVCR71.dll"
delete "$INSTDIR\MSVCP71.dll"
delete "$INSTDIR\w9xpopen.exe"
delete "$INSTDIR\bin\ffmpeg.exe"
delete "$INSTDIR\bin\SDL.dll"
delete "$INSTDIR\conf\!readme.txt"
delete "$INSTDIR\conf\conf.ini"
delete "$INSTDIR\conf\default.ini"
delete "$INSTDIR\img\googlevideo.png"
delete "$INSTDIR\img\icon256.png"
delete "$INSTDIR\img\icon.ico"
delete "$INSTDIR\img\online.png"
delete "$INSTDIR\img\stoat.jpg"
delete "$INSTDIR\img\veoh.png"
delete "$INSTDIR\img\video.png"
delete "$INSTDIR\img\youtube.png"
delete "$INSTDIR\img\dailymotion.png"
delete "$INSTDIR\output\!readme.txt"
delete "$INSTDIR\temp\!readme.txt"
rmDir "$INSTDIR\output" ; If it still contains files, it won't be deleted.
rmDir "$INSTDIR\bin"
rmDir "$INSTDIR\conf"
rmDir "$INSTDIR\img"
rmDir "$INSTDIR\temp"
rmDir "$INSTDIR"
!insertmacro MUI_STARTMENU_GETFOLDER Application $StartMenuFolder
delete "$SMPROGRAMS\$StartMenuFolder\${APP}.lnk"
delete "$SMPROGRAMS\$StartMenuFolder\Uninstall.lnk"
rmDir "$SMPROGRAMS\$StartMenuFolder"
DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP}"
DeleteRegKey HKCU "Software\${APP}"
sectionEnd