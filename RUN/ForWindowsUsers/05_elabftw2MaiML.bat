@echo off
setlocal
cd /d %~dp0

REM Activate virtual environment
call ..\..\SETUP\ForWindowsUsers\handsonvenv\Scripts\activate

REM copy input data files
mkdir ..\..\SRC\05_elabftw2MaiML\MaiML

REM Run Python script
REM Please modify the following command to match your execution environment.
echo on
python ..\..\SRC\05_elabftw2MaiML\elabftw_to_maiml.py --experiment-id 000 --output ..\..\SRC\05_elabftw2MaiML\MaiML\experiment_000.maiml 

REM copy output data files
copy ..\..\SRC\05_elabftw2MaiML\MaiML\*.maiml .\DATAFILES\05_elabftw2MaiML\MaiML\*

REM Deactivate virtual environment
call deactivate
echo "Output Excel file copied to DATAFILES\05_elabftw2MaiML\MaiML\"
echo "eLabFTW to MaiML conversion completed."
pause
