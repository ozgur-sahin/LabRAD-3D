#!/bin/bash

source virtualenvwrapper.sh
workon 'labrad'

#start all servers
cd ~/LabRAD/cct/clients
python NodeClient-CCT.py
