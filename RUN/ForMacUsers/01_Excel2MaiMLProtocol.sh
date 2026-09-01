#!/bin/bash
set -e
cd "$(dirname "$0")"

# Activate virtual environment
source ../../SETUP/ForMacUsers/handsonvenv/bin/activate

#copy input data files
rm -rf ../../SRC/01_Excel2MaiMLProtocol/INPUT/maiml/*
rm -rf ../../SRC/01_Excel2MaiMLProtocol/INPUT/others/*
rm -rf ../../SRC/01_Excel2MaiMLProtocol/INPUT/excel/*

#copy input data files
cp ./DATAFILES/01_Excel2MaiMLProtocol/INPUT/*.xlsx ../../SRC/01_Excel2MaiMLProtocol/INPUT/excel/
cp ./DATAFILES/01_Excel2MaiMLProtocol/INSERTIONFILES/* ../../SRC/01_Excel2MaiMLProtocol/INPUT/others/
cp ./DATAFILES/01_Excel2MaiMLProtocol/INPUT/usersettings.py ../../SRC/01_Excel2MaiMLProtocol/USERS/

# Run Python script
python ../../SRC/01_Excel2MaiMLProtocol/excel2protocolMaiML2.py


# copy output data files
cp ../../SRC/01_Excel2MaiMLProtocol/OUTPUT/Excel2MaiMLProtocol_Output.maiml ./DATAFILES/01_Excel2MaiMLProtocol/OUTPUT/
echo "Output MaiML file \"Excel2MaiMLProtocol_Output.maiml\" copied to DATAFILES/01_Excel2MaiMLProtocol/OUTPUT/"
deactivate
echo "Excel to MaiML Protocol conversion completed."