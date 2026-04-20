#!/bin/bash

~/LabRAD/scalabrad-0.8.0/bin/labrad --tls-required=false &
~/LabRAD/scalabrad-web-server-2.0.2/bin/labrad-web &
 

source virtualenvwrapper.sh #already done in ~/.bashrc
workon 'labrad'

#start node server
python -m labrad.node --tls=off &
