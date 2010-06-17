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

@echo All done.
@pause
