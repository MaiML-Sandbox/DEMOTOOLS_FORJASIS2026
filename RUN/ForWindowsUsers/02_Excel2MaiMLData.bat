@echo off
setlocal
cd /d %~dp0

REM Activate virtual environment
call ..\..\SETUP\ForWindowsUsers\handsonvenv\Scripts\activate

REM copy input data files
copy .\DATAFILES\02_Excel2MaiMLData\INPUT\*.xlsx ..\..\SRC\02_Excel2MaiMLData\INPUT\excel\
copy .\DATAFILES\01_Excel2MaiMLProtocol\OUTPUT\Excel2MaiMLProtocol_Output.maiml .\DATAFILES\02_Excel2MaiMLData\INPUT\
copy .\DATAFILES\02_Excel2MaiMLData\INPUT\Excel2MaiMLProtocol_Output.maiml ..\..\SRC\02_Excel2MaiMLData\INPUT\maiml\
copy .\DATAFILES\02_Excel2MaiMLData\INSERTIONFILES\* ..\..\SRC\02_Excel2MaiMLData\INPUT\others\
copy .\DATAFILES\02_Excel2MaiMLData\INPUT\usersettings.py ..\..\SRC\02_Excel2MaiMLData\USERS\

REM Run Python script
echo on
python ..\..\SRC\02_Excel2MaiMLData\excel2dataMaiML2.py
REM copy output data files
copy ..\..\SRC\02_Excel2MaiMLData\OUTPUT\Excel2MaiMLData_Output.maiml .\DATAFILES\02_Excel2MaiMLData\OUTPUT\*

REM Deactivate virtual environment
call deactivate
echo "Output MaiML file Excel2MaiMLData_Output.maiml copied to DATAFILES\02_Excel2MaiMLData\OUTPUT\"
echo "Excel to MaiML Data conversion completed."
pause