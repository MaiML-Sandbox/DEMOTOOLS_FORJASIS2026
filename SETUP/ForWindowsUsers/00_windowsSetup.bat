:: @echo off
setlocal

REM --- Proxy settings (if needed) ---
REM If you are behind a proxy, uncomment(Remove 'REM') and edit the following lines:
REM set HTTP_PROXY=http://your.proxy.server:port
REM set HTTPS_PROXY=http://your.proxy.server:port
REM pip config set global.proxy http://your.proxy.server:port

cd /d %~dp0

REM create python virtual environment
echo Creating virtual environment...

python -m venv handsonvenv

REM activate virtual environment
call .\handsonvenv\Scripts\activate

REM install python packages
echo Installing dependencies...
python -m pip install --upgrade pip
python -m pip install -r ..\requirements.txt
if errorlevel 1 (
    echo Failed to install dependencies.
    exit /b 1
)

REM --- Extract data files ---
set "TARGET_DIR=..\..\RUN\ForWindowsUsers"
set "ZIPFILE=..\DATAFILES.zip"

echo Check if the ZIP file exists and extract it
pause
if exist "%ZIPFILE%" (
    echo Extracting data files into '%TARGET_DIR%' ...
    powershell -Command "Expand-Archive -Force '%ZIPFILE%' '%TARGET_DIR%'"
) else (
    echo Error: ZIP file '%ZIPFILE%' not found.
    exit /b 1
)

endlocal

echo Setup complete!
pause
