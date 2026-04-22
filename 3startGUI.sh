#!/bin/bash

source virtualenvwrapper.sh 
workon 'labrad'

cd ~/LabRAD/cct/clients
python CCTGUI_horizontal.py &

workon 'labrad'
cd ~/LabRAD/common/devel/RealSimpleGrapher
python rsg.py &
