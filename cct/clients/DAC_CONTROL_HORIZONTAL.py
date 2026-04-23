from PyQt4 import QtGui, QtCore, uic
from numpy import *
# from qtui.QCustomSpinBoxION import QCustomSpinBoxION
from qtui.QCustomSpinBox import QCustomSpinBox
from twisted.internet.defer import inlineCallbacks, returnValue
import sys
# sys.path.append('/home/cct/LabRAD/common/abstractdevices')
from common.okfpgaservers.dacserver.DacConfiguration_Horizontal import hardwareConfiguration as hc

UpdateTime = 50 # ms
SIGNALID = 270836
SIGNALID2 = 270835

class MULTIPOLE_CONTROL(QtGui.QWidget):
    def __init__(self, reactor, parent=None):
        super(MULTIPOLE_CONTROL, self).__init__(parent)
        self.updating = False
        self.reactor = reactor
        self.connect()
        
    @inlineCallbacks    
    def makeGUI(self):
        self.multipoles = yield self.dacserver.get_multipole_names()
        self.position_vector = yield self.dacserver.get_position_vector()
        self.position = yield self.dacserver.get_position()
        self.controls = {k: QCustomSpinBox(k, (-5000.,5000.)) for k in self.multipoles}
        self.multipoleValues = {k: 0.0 for k in self.multipoles}
        # make ability to tune the ion trapping height
        # self.pSlider = QtGui.QSlider(QtCore.Qt.Vertical)
        # self.pSlider.setFixedHeight(250)
        # self.pSlider.setMinimum(0)
        # self.pSlider.setMaximum(len(self.position_vector)-1)
        # # print(self.position_vector)
        # self.pSlider.setValue(self.position_vector.index(str(self.position)))
        # self.pSlider.setTickPosition(QtGui.QSlider.TicksBelow)
        # self.pSlider.setTickInterval(1)
        # self.pLabel = QtGui.QLabel('H: ' + str(self.position))
        # self.pLabel.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        # self.ctrlPosLayout.addWidget(self.pLabel)
        # self.ctrlPosLayout.addWidget(self.pSlider)
        self.ctrlPosButtonLayout.addLayout(self.ctrlPosLayout)
        for ik, k in enumerate(self.multipoles):
            if len(self.multipoles) > 8:
                if ik < len(self.multipoles)/2:
                    self.ctrlLayout.addWidget(self.controls[k])
            else:
                self.ctrlLayout.addWidget(self.controls[k])
        # add controls for 2nd trap if needed
        if len(self.multipoles) > 8:
            # self.pSlider_extra = QtGui.QSlider(QtCore.Qt.Vertical)
            # self.pSlider_extra.setFixedHeight(200)
            # self.pSlider_extra.setMinimum(0)
            # self.pSlider_extra.setMaximum(len(self.position_vector)-1)
            # # print(self.position_vector)
            # self.pSlider_extra.setValue(self.position_vector.index(str(self.position)))
            # self.pSlider_extra.setTickPosition(QtGui.QSlider.TicksBelow)
            # self.pSlider_extra.setTickInterval(1)
            # self.pLabel_extra = QtGui.QLabel('H: ' + str(self.position))
            # self.pLabel_extra.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
            # self.ctrlPosLayout_extra.addWidget(self.pLabel_extra)
            # self.ctrlPosLayout_extra.addWidget(self.pSlider_extra)
            # self.ctrlLayout_extra.addLayout(self.ctrlPosLayout_extra)
            for ik, k in enumerate(self.multipoles):
                if ik >= len(self.multipoles)/2:
                    self.ctrlLayout_extra.addWidget(self.controls[k])

        self.inputUpdated = False
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.sendToServer)
        self.timer.start(UpdateTime)   
        # add in diagnostic buttons
        self.multipoleFileSelectButton = QtGui.QPushButton('Set C File')
        self.displayAnalogVoltages = QtGui.QPushButton('Analog Voltages')
        self.displayMultipoleValues = QtGui.QPushButton('Print Multipoles')
        self.zeroMultipoleValues = QtGui.QPushButton('Zero Multipoles')
        self.writeMultipoleValues1 = QtGui.QPushButton('Write Memory Slot 1')
        self.readMultipoleValues1 = QtGui.QPushButton('Read Memory Slot 1')
        self.writeMultipoleValues2 = QtGui.QPushButton('Write Memory Slot 2')
        self.readMultipoleValues2 = QtGui.QPushButton('Read Memory Slot 2')
        self.ctrlPosButtonLayout.addWidget(self.multipoleFileSelectButton)
        self.ctrlPosButtonLayout.addWidget(self.displayAnalogVoltages)
        self.ctrlPosButtonLayout.addWidget(self.displayMultipoleValues)
        self.ctrlPosButtonLayout.addWidget(self.zeroMultipoleValues)
        self.ctrlPosButtonLayout.addWidget(self.writeMultipoleValues1)
        self.ctrlPosButtonLayout.addWidget(self.readMultipoleValues1)
        self.ctrlPosButtonLayout.addWidget(self.writeMultipoleValues2)
        self.ctrlPosButtonLayout.addWidget(self.readMultipoleValues2)

        # connect all the button controls
        for k in self.multipoles:
            self.controls[k].onNewValues.connect(self.inputHasUpdated)
        # self.pSlider.valueChanged.connect(self.inputHasUpdated)
        self.multipoleFileSelectButton.released.connect(self.selectCFile)
        self.displayAnalogVoltages.released.connect(self.displayVoltages)
        self.displayMultipoleValues.released.connect(self.displayMultipoles)
        self.zeroMultipoleValues.released.connect(self.zeroMultipoles)
        self.writeMultipoleValues1.released.connect(self.writeMultipoles1)
        self.readMultipoleValues1.released.connect(self.readMultipoles1)
        self.writeMultipoleValues2.released.connect(self.writeMultipoles2)
        self.readMultipoleValues2.released.connect(self.readMultipoles2)

        self.ctrlLayout_full = QtGui.QGridLayout()
        self.ctrlLayout_full.addLayout(self.ctrlPosButtonLayout, 0, 0)
        self.ctrlLayout_full.addLayout(self.ctrlLayout, 0, 1)
        if len(self.multipoles) > 8:
            self.ctrlLayout_full.addLayout(self.ctrlLayout_extra, 0, 2)
        self.setLayout(self.ctrlLayout_full)
        yield self.followSignal(0, 0)   
        
    @inlineCallbacks
    def connect(self):
        from labrad.wrappers import connectAsync
        from labrad.types import Error
        self.cxn = yield connectAsync()
        self.dacserver = yield self.cxn.dac_server
        yield self.setupListeners()
        self.ctrlLayout = QtGui.QVBoxLayout()
        self.ctrlPosLayout = QtGui.QHBoxLayout()
        self.ctrlPosButtonLayout = QtGui.QVBoxLayout()
        # add more controls for more than one trap
        self.multipoles = yield self.dacserver.get_multipole_names()
        if len(self.multipoles) > 8:
            self.ctrlLayout_extra = QtGui.QVBoxLayout()
        yield self.makeGUI()
        
    def inputHasUpdated(self):
        self.inputUpdated = True
        for k in self.multipoles:
            self.multipoleValues[k] = round(self.controls[k].spinLevel.value(), 3)
        # self.position = self.position_vector[self.pSlider.value()]
        self.pLabel.setText('H: ' + str(self.position))

    def sendToServer(self):
        if self.inputUpdated:
            self.dacserver.set_multipole_values(self.multipoleValues.items(), int(self.position))
            # self.dacserver.set_multipole_position(int(self.position))
            # self.dacserver.set_center_voltage(self.multipoleValues.items(), self.center_voltage)
            self.inputUpdated = False
    
    @inlineCallbacks        
    def selectCFile(self):
        fn = QtGui.QFileDialog().getOpenFileName()
        self.updating = True
        yield self.dacserver.set_control_file(str(fn))
        for i in range(self.ctrlLayout.count()): self.ctrlLayout.itemAt(i).widget().close()
        self.updating = False
        yield self.makeGUI()
        self.inputHasUpdated()

    @inlineCallbacks
    def displayVoltages(self):
        av = yield self.dacserver.get_analog_voltages()
        av.sort()
        # elecSingleTrap = ['17','18','19','20','21','22','23','24','25']
        # av_SingleTrap = []
        # for (k, v) in av:
        #     if k in elecSingleTrap:
        #         av_SingleTrap.append(v)
        # outVol = '['+', '.join(map(str, av_SingleTrap))+']'
        elecDoubleTrap = ['01','02','03','04','05','06','07','08']
        av_DoubleTrap = []
        for (k, v) in av:
            if k in elecDoubleTrap:
                av_DoubleTrap.append(v)
        outVol = '['+', '.join(map(str, av_DoubleTrap))+']'
        msgBox = QtGui.QMessageBox(QtGui.QMessageBox.NoIcon, "DAC Voltages", outVol)
        msgBox.exec_()

    @inlineCallbacks
    def displayMultipoles(self):
        multi_val = yield self.dacserver.get_multipole_values()
        multi_val.sort()
        multi_array = []
        for (mname, mval) in multi_val:
            multi_array.append(mname + ' = ' + str(mval))
        multi_display = ', '.join(map(str, multi_array))
        msgBox = QtGui.QMessageBox(QtGui.QMessageBox.NoIcon, "Multipole Values", multi_display)
        msgBox.exec_()

    # write the current multipole values to the memory slot 1
    # there should be a better way to toggle between the memory slots, but this is the easy fix...
    def writeMultipoles1(self):
        self.dacserver.set_multipole_values(self.multipoleValues.items(), int(self.position), 1)

    # read the multipole values from memory slot 1 and set the current multipoles to the values from memory slot 1
    @inlineCallbacks
    def readMultipoles1(self):
        self.inputUpdated = True
        # change trapping position
        temp_position = yield self.dacserver.get_position(1)
        # self.pSlider.setValue(self.position_vector.index(str(temp_position)))
        self.pLabel.setText('H: ' + str(temp_position))
        # change multipoles
        temp_multipoles = yield self.dacserver.get_multipole_values(1)
        for k, v in temp_multipoles:
            self.controls[k].spinLevel.setValue(v)

    # write the current multipole values to the memory slot 2
    # there should be a better way to toggle between the memory slots, but this is the easy fix...
    def writeMultipoles2(self):
        self.dacserver.set_multipole_values(self.multipoleValues.items(), int(self.position), 2)

    # read the multipole values from memory slot 2 and set the current multipoles to the values from memory slot 2
    @inlineCallbacks
    def readMultipoles2(self):
        self.inputUpdated = True
        # change trapping position
        temp_position = yield self.dacserver.get_position(2)
        # self.pSlider.setValue(self.position_vector.index(str(temp_position)))
        self.pLabel.setText('H: ' + str(temp_position))
        # change multipoles
        temp_multipoles = yield self.dacserver.get_multipole_values(2)
        for k, v in temp_multipoles:
            self.controls[k].spinLevel.setValue(v)

    # zero all multipole values and gamma, keeping the height the same
    def zeroMultipoles(self):
        self.inputUpdated = True
        for k in self.multipoles:
            self.controls[k].spinLevel.setValue(0.0)
        
    @inlineCallbacks    
    def setupListeners(self):
        yield self.dacserver.signal__ports_updated(SIGNALID)
        yield self.dacserver.addListener(listener = self.followSignal, source = None, ID = SIGNALID) 
        
    @inlineCallbacks
    def followSignal(self, x, s):
        if self.updating: return
        multipoles = yield self.dacserver.get_multipole_values()
        for (k,v) in multipoles:
            self.controls[k].setValueNoSignal(v)
        pos = yield self.dacserver.get_position()
        # self.pSlider.setValue(self.position_vector.index(str(pos)))
        # self.pLabel.setText('H: ' + str(pos))

    def closeEvent(self, x):
        self.reactor.stop()

class CHANNEL_CONTROL (QtGui.QWidget):
    def __init__(self, reactor, parent=None):
        super(CHANNEL_CONTROL, self).__init__(parent)
        self.reactor = reactor
        self.makeGUI()
        self.connect()
     
    def makeGUI(self):
        self.dacDict = dict(hc.elec_dict.items() + hc.sma_dict.items())
        self.controls = {k: QCustomSpinBox(k, self.dacDict[k].allowedVoltageRange) for k in self.dacDict.keys()}
        layout = QtGui.QGridLayout()
        if bool(hc.sma_dict):
            smaBox = QtGui.QGroupBox('SMA Out')
            smaLayout = QtGui.QVBoxLayout()
            smaBox.setLayout(smaLayout)
        elecBox = QtGui.QGroupBox('Electrodes')
        elecLayout = QtGui.QGridLayout()
        elecBox.setLayout(elecLayout)
        # set electrode positions (not the best way, but it works)
        trapElecLayout = [[8,4], [4,0], [2,0], [0,0], [6,6], [2,6], [6,2], [2,2], [0,4], [8,8], [6,8], [4,8], [2,8], [0,8], [8,0], [6,0], [2,4], [6,4], [4,2], [4,6]]
        if bool(hc.sma_dict):
            layout.addWidget(smaBox, 0, 0)
        layout.addWidget(elecBox, 0, 1)

        for s in hc.sma_dict:
            smaLayout.addWidget(self.controls[s], alignment = QtCore.Qt.AlignRight)
        elecList = hc.elec_dict.keys()
        elecList.sort()
        # if bool(hc.centerElectrode):
        #     elecList.pop(hc.centerElectrode-1)
        for i,e in enumerate(elecList):
            if int(i) <= 25:
                elecLayout.addWidget(self.controls[e], trapElecLayout[int(i)][0], trapElecLayout[int(i)][1]+1)
        # if bool(hc.centerElectrode):
        #     self.controls[str(hc.centerElectrode).zfill(2)].title.setText('CNT')
        #     elecLayout.addWidget(self.controls[str(hc.centerElectrode).zfill(2)], 7, 3) 

        spacer = QtGui.QSpacerItem(20,40,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.MinimumExpanding)
        if bool(hc.sma_dict):
            smaLayout.addItem(spacer)        
        self.inputUpdated = False                
        self.timer = QtCore.QTimer(self)        
        self.timer.timeout.connect(self.sendToServer)
        self.timer.start(UpdateTime)
        
        for k in self.dacDict.keys():
            self.controls[k].onNewValues.connect(self.inputHasUpdated(k))

        layout.setColumnStretch(1, 1)                   
        self.setLayout(layout)

    @inlineCallbacks
    def connect(self):
        from labrad.wrappers import connectAsync
        from labrad.types import Error
        self.cxn = yield connectAsync()
        self.dacserver = yield self.cxn.dac_server
        yield self.setupListeners()
        yield self.followSignal(0, 0)

    def inputHasUpdated(self, name):
        def iu():
            self.inputUpdated = True
            self.changedChannel = name
        return iu

    def sendToServer(self):
        if self.inputUpdated:            
            self.dacserver.set_individual_analog_voltages([(self.changedChannel, round(self.controls[self.changedChannel].spinLevel.value(), 3))]*1) # 17 for single trap
            self.inputUpdated = False
            
    @inlineCallbacks    
    def setupListeners(self):
        yield self.dacserver.signal__ports_updated(SIGNALID2)
        yield self.dacserver.addListener(listener = self.followSignal, source = None, ID = SIGNALID2)
    
    @inlineCallbacks
    def followSignal(self, x, s):
        # print 'notified here'
        av = yield self.dacserver.get_analog_voltages()
        for (c, v) in av:
            self.controls[c].setValueNoSignal(v)

    def closeEvent(self, x):
        self.reactor.stop()        

class CHANNEL_MONITOR(QtGui.QWidget):
    def __init__(self, reactor, parent=None):
        super(CHANNEL_MONITOR, self).__init__(parent)
        self.reactor = reactor        
        self.makeGUI()
        self.connect()
       
        
    def makeGUI(self):      
        self.dacDict = dict(hc.elec_dict.items() + hc.sma_dict.items())
        self.displays = {k: QtGui.QLCDNumber() for k in self.dacDict.keys()}
        print self.displays
        layout = QtGui.QGridLayout()
        if bool(hc.sma_dict):
            smaBox = QtGui.QGroupBox('SMA Out')
            smaLayout = QtGui.QGridLayout()
            smaBox.setLayout(smaLayout)       
        elecBox = QtGui.QGroupBox('Electrodes')
        elecLayout = QtGui.QGridLayout()
        elecLayout.setColumnStretch(1, 2)
        elecLayout.setColumnStretch(3, 2)
        elecLayout.setColumnStretch(5, 2)
        elecLayout.setColumnStretch(7, 2)
        elecLayout.setColumnStretch(9, 2)
        elecLayout.setColumnStretch(11, 2)
        elecBox.setLayout(elecLayout)
        # set electrode positions (not the best way, but it works)
        trapElecLayout = [[8,4], [4,0], [2,0], [0,0], [6,6], [2,6], [6,2], [2,2], [0,4], [8,8], [6,8], [4,8], [2,8], [0,8], [8,0], [6,0], [4,2], [4,6]]
        if bool(hc.sma_dict):
            layout.addWidget(smaBox, 0, 0)
        layout.addWidget(elecBox, 0, 1)
        
        if bool(hc.sma_dict):
            for k in hc.sma_dict:
                self.displays[k].setAutoFillBackground(True)
                smaLayout.addWidget(QtGui.QLabel(k), self.dacDict[k].smaOutNumber, 0)
                smaLayout.addWidget(self.displays[k], self.dacDict[k].smaOutNumber, 1)
                s = hc.sma_dict[k].smaOutNumber+1

        elecList = hc.elec_dict.keys()
        elecList.sort()
        print 'Eleclist: ', elecList
        if bool(hc.centerElectrode):
            elecList.pop(hc.centerElectrode-1)
        for i,e in enumerate(elecList):
            if bool(hc.sma_dict):
                self.displays[k].setAutoFillBackground(True)
            if int(i) <= 25:
                elecLayout.addWidget(QtGui.QLabel(e), trapElecLayout[int(i)][0], trapElecLayout[int(i)][1])
                elecLayout.addWidget(self.displays[e], trapElecLayout[int(i)][0], trapElecLayout[int(i)][1]+1)
                print i, e, self.displays[e]
        if bool(hc.centerElectrode):
            elecLayout.addWidget(QtGui.QLabel('Center'), 4, 4)
            elecLayout.addWidget(self.displays[str(hc.centerElectrode).zfill(2)], 4, 5, 1, 1)      
          
        if bool(hc.sma_dict):
            spacer = QtGui.QSpacerItem(20,40,QtGui.QSizePolicy.Minimum,QtGui.QSizePolicy.MinimumExpanding)
            smaLayout.addItem(spacer, s, 0,10, 2)  

        self.setLayout(layout)  
                
    @inlineCallbacks
    def connect(self):
        from labrad.wrappers import connectAsync
        from labrad.types import Error
        self.cxn = yield connectAsync()
        self.dacserver = yield self.cxn.dac_server
        self.ionInfo = {}
        yield self.setupListeners()
        yield self.followSignal(0, 0)    
        for i in hc.notused_dict:        #Sets unused channels to about 0V
            yield self.dacserver.set_individual_digital_voltages_u([(i, 32768)])     

                  
    @inlineCallbacks    
    def setupListeners(self):
        yield self.dacserver.signal__ports_updated(SIGNALID2)
        yield self.dacserver.addListener(listener = self.followSignal, source = None, ID = SIGNALID2)
    
    @inlineCallbacks
    def followSignal(self, x, s):        
        av = yield self.dacserver.get_analog_voltages()
        print av
        brightness = 210
        darkness = 255 - brightness           
        for (k, v) in av:
            # print k
            # print v
            self.displays[k].display(float(v)) 
            if abs(v) > 30:
                self.displays[k].setStyleSheet("QWidget {background-color: orange }")
            else:
                R = int(brightness + v*darkness/30.)
                G = int(brightness - abs(v*darkness/30.))
                B = int(brightness - v*darkness/30.)
                hexclr = '#%02x%02x%02x' % (R, G, B)
                self.displays[k].setStyleSheet("QWidget {background-color: "+hexclr+" }")

    def closeEvent(self, x):
        self.reactor.stop()

class DAC_Control(QtGui.QMainWindow):
    def __init__(self, reactor, parent=None):
        super(DAC_Control, self).__init__(parent)
        self.reactor = reactor   

        channelControlTab = self.buildChannelControlTab()        
        multipoleControlTab = self.buildMultipoleControlTab()
        # scanTab = self.buildScanTab()
        tab = QtGui.QTabWidget()
        tab.addTab(multipoleControlTab,'&Multipoles')
        tab.addTab(channelControlTab, '&Channels')
        # tab.addTab(scanTab, '&Scans')
        self.setWindowTitle('DAC Control')
        self.setCentralWidget(tab)
    
    def buildMultipoleControlTab(self):
        widget = QtGui.QWidget()
        gridLayout = QtGui.QGridLayout()
        gridLayout.addWidget(CHANNEL_MONITOR(self.reactor),0,0)
        gridLayout.addWidget(MULTIPOLE_CONTROL(self.reactor),0,1)
        widget.setLayout(gridLayout)
        return widget

    def buildChannelControlTab(self):
        widget = QtGui.QWidget()
        gridLayout = QtGui.QGridLayout()
        gridLayout.addWidget(CHANNEL_CONTROL(self.reactor),0,0)
        widget.setLayout(gridLayout)
        return widget
        
    def buildScanTab(self):
        from SCAN_CONTROL import Scan_Control_Tickle
        widget = QtGui.QWidget()
        gridLayout = QtGui.QGridLayout()
        gridLayout.addWidget(Scan_Control_Tickle(self.reactor, 'Ex1'), 0, 0)
        gridLayout.addWidget(Scan_Control_Tickle(self.reactor, 'Ey1'), 0, 1)
        widget.setLayout(gridLayout)
        return widget
    
    def closeEvent(self, x):
        self.reactor.stop()  

if __name__ == "__main__":
    a = QtGui.QApplication( [] )
    import qt4reactor
    qt4reactor.install()
    from twisted.internet import reactor
    DAC_Control = DAC_Control(reactor)
    DAC_Control.show()
    reactor.run()