@echo Packaging DamnVid for win32.
@echo ----------------------------
@cd ..
@echo Trying to delete old setup, if any.
@del /q DamnVid-setup*
@echo Building list of required files.
@python build-any\build-required-files.py
@python build-exe\find-system-paths-win32.py
@set /p python= < python32-path.tmp
@echo Creating /package/ directory.
@mkdir package
@echo Switching to /package/ directory.
@cd package
@echo Compyling DamnVid.
@copy /Y ..\build-exe\msvcp90.dll %python%\msvcp90.dll
@%python%\python -OO ..\build-exe\py2exe-win32.py py2exe
@echo Running UPX --brute on compyled executable.
@echo upx --brute dist\DamnVid.exe
@echo Switching to /package/dist/ directory.
@cd dist
@copy /Y ..\..\build-exe\gdiplus.dll .\gdiplus.dll
@copy /Y ..\..\build-exe\msvcp71.dll .\msvcp71.dll
@copy /Y ..\..\build-exe\msvcr71.dll .\msvcr71.dll
@copy /Y ..\..\build-exe\unicows.dll .\unicows.dll
@echo Packaging with NSIS.
@python ..\..\build-exe\build-nsi.py
@makensis -V4 -NOCD ..\..\NSIS-win32.nsi
@echo Switching back to root directory.
@cd ..\..
@echo DamnVid packaged.
@echo Renaming setup.
@set /p version= < version.damnvid
@ren DamnVid-setup.exe DamnVid-setup-%version%.exe
@echo Cleaning up.
@python build-any/cleanup.py
@cd build-exe
@echo All done.
@pause
