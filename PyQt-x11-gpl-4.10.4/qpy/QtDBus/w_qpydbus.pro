# Tell the original .pro file about additional directories.
INCLUDEPATH = "/usr/include/python2.7" "../../QtDBus" "/home/cct/LabRAD/PyQt-x11-gpl-4.10.4/qpy/QtDBus"
CONFIG += release
VPATH = /home/cct/LabRAD/PyQt-x11-gpl-4.10.4/qpy/QtDBus
include(/home/cct/LabRAD/PyQt-x11-gpl-4.10.4/qpy/QtDBus/qpydbus.pro)
