# Tell the original .pro file about additional directories.
INCLUDEPATH = "/usr/include/python2.7" "../../QtDeclarative" "/home/cct/LabRAD/PyQt-x11-gpl-4.10.4/qpy/QtDeclarative"
CONFIG += release
VPATH = /home/cct/LabRAD/PyQt-x11-gpl-4.10.4/qpy/QtDeclarative
include(/home/cct/LabRAD/PyQt-x11-gpl-4.10.4/qpy/QtDeclarative/qpydeclarative.pro)
