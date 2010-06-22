@call build-app-only-win32.bat /nopause
@echo Packaging with NSIS.
@%python%\python -OO ..\..\build-exe\build-nsi.py
@makensis -V4 -NOCD ..\..\NSIS-win32.nsi
@echo Switching back to root directory.
@cd ..\..
@echo DamnVid packaged.
@echo Renaming setup.
@set /p version= < version.damnvid
@ren DamnVid-setup.exe DamnVid-setup-%version%.exe
@echo Cleaning up.
@%python%\python -OO build-any/cleanup.py
@cd build-exe
@echo All done.
@pause
