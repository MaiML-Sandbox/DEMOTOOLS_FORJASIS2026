#!/bin/bash
set -e
cd "$(dirname "$0")"

# Activate virtual environment
source ../../SETUP/ForMacUsers/handsonvenv/bin/activate

#copy input data files
rm -rf ../../SRC/02_Excel2MaiMLData/INPUT/maiml/*
rm -rf ../../SRC/02_Excel2MaiMLData/INPUT/others/*
rm -rf ../../SRC/02_Excel2MaiMLData/INPUT/excel/*

# copy maiml files
cp ./DATAFILES/01_Excel2MaiMLProtocol/OUTPUT/Excel2MaiMLProtocol_Output.maiml ./DATAFILES/02_Excel2MaiMLData/INPUT/
cp ./DATAFILES/02_Excel2MaiMLData/INPUT/Excel2MaiMLProtocol_Output.maiml ../../SRC/02_Excel2MaiMLData/INPUT/maiml/Excel2MaiMLProtocol_Output.maiml
#copy excel files
cp ./DATAFILES/02_Excel2MaiMLData/INPUT/Excel2MaiMLData_Input.xlsx ../../SRC/02_Excel2MaiMLData/INPUT/excel/Excel2MaiMLData_Input.xlsx
# copy other files
cp ./DATAFILES/02_Excel2MaiMLData/INSERTIONFILES/* ../../SRC/02_Excel2MaiMLData/INPUT/others/
# copy settings files
cp ./DATAFILES/02_Excel2MaiMLData/INPUT/usersettings.py ../../SRC/02_Excel2MaiMLData/USERS/

# Run Python script
python ../../SRC/02_Excel2MaiMLData/excel2dataMaiML2.py
# copy output data files
cp ../../SRC/02_Excel2MaiMLData/OUTPUT/Excel2MaiMLData_Output.maiml ./DATAFILES/02_Excel2MaiMLData/OUTPUT/
echo "Output MaiML file \"Excel2MaiMLData_Output.maiml\" copied to DATAFILES/02_Excel2MaiMLData/OUTPUT/"
deactivate
echo "Excel to MaiML Data conversion completed."