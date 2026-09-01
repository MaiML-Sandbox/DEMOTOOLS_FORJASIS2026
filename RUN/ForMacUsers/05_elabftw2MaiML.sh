#!/bin/bash
set -e
cd "$(dirname "$0")"

# Activate virtual environment
source ../../SETUP/ForMacUsers/handsonvenv/bin/activate

#copy input data files
mkdir -p ../../SRC/05_elabftw2MaiML/MaiML

# Run Python script. 
# Please modify the following command to match your execution environment.
python ../../SRC/05_elabftw2MaiML/elabftw_to_maiml.py --experiment-id 000 --output ../../SRC/05_elabftw2MaiML/MaiML/experiment_000.maiml

# copy output data files
cp ../../SRC/05_elabftw2MaiML/MaiML/*.maiml ./DATAFILES/05_elabftw2MaiML/MaiML/
echo "Output MaiML file copied to DATAFILES/05_elabftw2MaiML/MaiML/"

deactivate

echo "eLabFTW to MaiML conversion completed."