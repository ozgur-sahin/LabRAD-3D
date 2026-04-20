# Tell the original .pro file about additional directories.
INCLUDEPATH = "/usr/include/python2.7" "../../QtCore" "/home/cct/LabRAD/PyQt-x11-gpl-4.10.4/qpy/QtCore"
CONFIG += release
VPATH = /home/cct/LabRAD/PyQt-x11-gpl-4.10.4/qpy/QtCore
include(/home/cct/LabRAD/PyQt-x11-gpl-4.10.4/qpy/QtCore/qpycore.pro)
