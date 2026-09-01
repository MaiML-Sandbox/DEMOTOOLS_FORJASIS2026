@echo off
setlocal
cd /d %~dp0

REM Activate virtual environment
call ..\..\SETUP\ForWindowsUsers\handsonvenv\Scripts\activate

REM copy input data files
copy .\DATAFILES\01_Excel2MaiMLProtocol\INPUT\*.xlsx ..\..\SRC\01_Excel2MaiMLProtocol\INPUT\excel\
copy .\DATAFILES\01_Excel2MaiMLProtocol\INSERTIONFILES\* ..\..\SRC\01_Excel2MaiMLProtocol\INPUT\others\
copy .\DATAFILES\01_Excel2MaiMLProtocol\INPUT\usersettings.py ..\..\SRC\01_Excel2MaiMLProtocol\USERS\

REM Run Python script
echo on
python ..\..\SRC\01_Excel2MaiMLProtocol\excel2protocolMaiML2.py
REM copy output data files
copy ..\..\SRC\01_Excel2MaiMLProtocol\OUTPUT\Excel2MaiMLProtocol_Output.maiml .\DATAFILES\01_Excel2MaiMLProtocol\OUTPUT\

REM Deactivate virtual environment
call deactivate

echo "Output MaiML file Excel2MaiMLProtocol_Output.maiml copied to DATAFILES\01_Excel2MaiMLProtocol\OUTPUT\"
echo "Excel to MaiML Protocol conversion completed."
pause