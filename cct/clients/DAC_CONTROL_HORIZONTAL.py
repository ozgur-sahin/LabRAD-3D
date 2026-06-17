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
        # self.pLabel = QtGui.QLabel('H: ' + str(self.position))
        # self.pLabel.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)
        # self.ctrlPosLayout.addWidget(self.pLabel)
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

        self.multipole_oscillation_state = yield self.dacserver.get_multipole_oscillation_state()
        self.multipole_step_state = yield self.dacserver.get_multipole_step_state()
        self.multiple_sweep_state = yield self.dacserver.get_multiple_sweep_state()

        self.SweepTabWidget = QtGui.QTabWidget()

        self.MultipoleSweepWidget = self.makeMultipoleSweepBox()
        self.MultipoleStepWidget = self.makeMultipoleStepBox()
        self.MultipleMultipoleSweepWidget=self.makeMultipleMultipoleSweepBox(3)

        self.SweepTabWidget.addTab(self.MultipleMultipoleSweepWidget, '&Multiple Sweep')
        self.SweepTabWidget.addTab(self.MultipoleStepWidget, "&Step")
        self.SweepTabWidget.addTab(self.MultipoleSweepWidget, "&Sweep")

        
        self.ctrlPosButtonLayout.addWidget(self.SweepTabWidget)

        # connect all the button controls
        for k in self.multipoles:
            self.controls[k].onNewValues.connect(self.inputHasUpdated)
        # self.pSlider.valueChanged.connect(self.inputHasUpdated)
        self.multipoleFileSelectButton.released.connect(self.selectCFile)
        self.displayAnalogVoltages.released.connect(self.displayVoltages)
        self.displayMultipoleValues.released.connect(self.displayMultipoles)
        # self.displayAnalogVoltages.released.connect(self.startMultiSweep)
        # self.displayMultipoleValues.released.connect(self.StopMultiSweep)
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

    def makeMultipoleSweepBox(self):
        box = QtGui.QGroupBox('Multipole Sweep')
        layout = QtGui.QGridLayout()

        self.sweepMultipole = QtGui.QComboBox()
        self.sweepMultipole.addItems(self.multipoles)
        self.setDefaultSweepMultipole('Ez')

        self.sweepCenter = QtGui.QDoubleSpinBox()
        self.sweepCenter.setDecimals(4)
        self.sweepCenter.setRange(-1.0, 1.0)
        self.sweepCenter.setSingleStep(0.01)

        self.sweepAmplitude = QtGui.QDoubleSpinBox()
        self.sweepAmplitude.setDecimals(4)
        self.sweepAmplitude.setRange(0.0, 1.5)
        self.sweepAmplitude.setSingleStep(0.01)
        self.sweepAmplitude.setValue(0.5)

        self.sweepFrequency = QtGui.QDoubleSpinBox()
        self.sweepFrequency.setDecimals(3)
        self.sweepFrequency.setRange(0.01, 100.0)
        self.sweepFrequency.setSingleStep(0.01)
        self.sweepFrequency.setValue(0.01)

        self.sweepUpdateRate = QtGui.QDoubleSpinBox()
        self.sweepUpdateRate.setDecimals(1)
        self.sweepUpdateRate.setRange(0.1, 5.0)
        self.sweepUpdateRate.setSingleStep(0.1)
        self.sweepUpdateRate.setValue(5.0)

        self.sweepRestoreCenter = QtGui.QCheckBox('Restore center on stop')
        self.sweepRestoreCenter.setChecked(False)

        self.sweepUseCurrentButton = QtGui.QPushButton('Use Current')
        self.sweepStartButton = QtGui.QPushButton('Start')
        self.sweepStopButton = QtGui.QPushButton('Stop')
        self.sweepStartButton.setEnabled(self.multipole_oscillation_state)
        self.sweepStopButton.setEnabled(not self.multipole_oscillation_state)
        self.sweepStatus = QtGui.QLabel('Idle')

        layout.addWidget(QtGui.QLabel('Multipole'), 0, 0)
        layout.addWidget(self.sweepMultipole, 0, 1)
        layout.addWidget(QtGui.QLabel('Center'), 1, 0)
        layout.addWidget(self.sweepCenter, 1, 1)
        layout.addWidget(QtGui.QLabel('Amplitude'), 2, 0)
        layout.addWidget(self.sweepAmplitude, 2, 1)
        layout.addWidget(QtGui.QLabel('Freq Hz'), 3, 0)
        layout.addWidget(self.sweepFrequency, 3, 1)
        layout.addWidget(QtGui.QLabel('Update Hz'), 4, 0)
        layout.addWidget(self.sweepUpdateRate, 4, 1)
        layout.addWidget(self.sweepRestoreCenter, 5, 0, 1, 2)
        layout.addWidget(self.sweepUseCurrentButton, 6, 0, 1, 2)
        layout.addWidget(self.sweepStartButton, 7, 0)
        layout.addWidget(self.sweepStopButton, 7, 1)
        layout.addWidget(self.sweepStatus, 8, 0, 1, 2)

        self.sweepUseCurrentButton.released.connect(self.useCurrentSweepCenter)
        self.sweepStartButton.released.connect(self.startMultipoleSweep)
        self.sweepStopButton.released.connect(self.stopMultipoleSweep)

        box.setLayout(layout)
        return box
    
    def makeMultipoleStepBox(self):
        box = QtGui.QGroupBox('Multipole Step')
        layout = QtGui.QGridLayout()

        self.stepMultipole = QtGui.QComboBox()
        self.stepMultipole.addItems(self.multipoles)
        self.setDefaultStepMultipole('Ez')

        self.stepCenter = QtGui.QDoubleSpinBox()
        self.stepCenter.setDecimals(4)
        self.stepCenter.setRange(-1.0, 1.0)
        self.stepCenter.setSingleStep(0.01)

        self.stepAmplitude = QtGui.QDoubleSpinBox()
        self.stepAmplitude.setDecimals(4)
        self.stepAmplitude.setRange(0.0, 1.5)
        self.stepAmplitude.setSingleStep(0.01)
        self.stepAmplitude.setValue(0.5)

        self.stepPeriod = QtGui.QDoubleSpinBox()
        self.stepPeriod.setDecimals(3)
        self.stepPeriod.setRange(1.0, 500.0)
        self.stepPeriod.setSingleStep(0.1)
        self.stepPeriod.setValue(100.0)

        self.stepUpdateTime = QtGui.QDoubleSpinBox()
        self.stepUpdateTime.setDecimals(1)
        self.stepUpdateTime.setRange(0.25, 20.0)
        self.stepUpdateTime.setSingleStep(0.1)
        self.stepUpdateTime.setValue(1.0)

        self.stepRestoreCenter = QtGui.QCheckBox('Restore center on stop')
        self.stepRestoreCenter.setChecked(False)

        self.stepUseCurrentButton = QtGui.QPushButton('Use Current')
        self.stepStartButton = QtGui.QPushButton('Start')
        self.stepStopButton = QtGui.QPushButton('Stop')
        self.stepStartButton.setEnabled(self.multipole_step_state)
        self.stepStopButton.setEnabled(not self.multipole_step_state)
        self.stepStatus = QtGui.QLabel('Idle')

        layout.addWidget(QtGui.QLabel('Multipole'), 0, 0)
        layout.addWidget(self.stepMultipole, 0, 1)
        layout.addWidget(QtGui.QLabel('Center'), 1, 0)
        layout.addWidget(self.stepCenter, 1, 1)
        layout.addWidget(QtGui.QLabel('Amplitude'), 2, 0)
        layout.addWidget(self.stepAmplitude, 2, 1)
        layout.addWidget(QtGui.QLabel('Cycle Period'), 3, 0)
        layout.addWidget(self.stepPeriod, 3, 1)
        layout.addWidget(QtGui.QLabel('Update Time'), 4, 0)
        layout.addWidget(self.stepUpdateTime, 4, 1)
        layout.addWidget(self.stepRestoreCenter, 5, 0, 1, 2)
        layout.addWidget(self.stepUseCurrentButton, 6, 0, 1, 2)
        layout.addWidget(self.stepStartButton, 7, 0)
        layout.addWidget(self.stepStopButton, 7, 1)
        layout.addWidget(self.stepStatus, 8, 0, 1, 2)

        self.stepUseCurrentButton.released.connect(self.useCurrentStepCenter)
        self.stepStartButton.released.connect(self.startMultipoleStep)
        self.stepStopButton.released.connect(self.stopMultipoleStep)

        box.setLayout(layout)
        return box
    
    def makeMultipleMultipoleSweepBox(self, n=3, defaults=['Ez', 'Ex', 'Ey']):
        '''n is the number of swept multipoles'''
        box = QtGui.QGroupBox('Multiple Multipole Sweep')
        layout = QtGui.QGridLayout()
        self.multipoleboxes = [None]*n
        self.multipolecenter=[None]*n
        self.multipolespan=[None]*n
        self.multipolestep=[None]*n
        # layout.addWidget(QtGui.QLabel("Multipole Name"), 0, 1)
        layout.addWidget(QtGui.QLabel("Center"), 0, 2)
        layout.addWidget(QtGui.QLabel("Span"), 0, 3)
        layout.addWidget(QtGui.QLabel("Step"), 0, 4)
        layout.setRowStretch(0, 0)

        for i in range(n):
            self.multipoleboxes[i]=QtGui.QComboBox()
            self.multipoleboxes[i].addItems(self.multipoles)

            self.multipolecenter[i]=QtGui.QDoubleSpinBox()
            self.multipolecenter[i].setDecimals(3)
            self.multipolecenter[i].setRange(0.0, 1.5)
            self.multipolecenter[i].setSingleStep(0.01)
            self.multipolecenter[i].setValue(0)

            self.multipolespan[i]=QtGui.QDoubleSpinBox()
            self.multipolespan[i].setDecimals(3)
            self.multipolespan[i].setRange(0.0, 1.5)
            self.multipolespan[i].setSingleStep(0.01)
            self.multipolespan[i].setValue(0.05)

            self.multipolestep[i]=QtGui.QDoubleSpinBox()
            self.multipolestep[i].setDecimals(3)
            self.multipolestep[i].setRange(0.0, 0.5)
            self.multipolestep[i].setSingleStep(0.01)
            self.multipolestep[i].setValue(0.01)

            layout.addWidget(QtGui.QLabel("Multipole "+str(i+1)), i+1, 0)
            layout.addWidget(self.multipoleboxes[i], i+1, 1)
            layout.addWidget(self.multipolecenter[i], i+1, 2)
            layout.addWidget(self.multipolespan[i], i+1, 3)
            layout.addWidget(self.multipolestep[i], i+1, 4)
            layout.setRowStretch(i+1, 2)

        self.setDefaultMultipleSweepMultipole(defaults)
        self.dwell_time_box=QtGui.QDoubleSpinBox()
        self.dwell_time_box.setDecimals(3)
        self.dwell_time_box.setRange(0.5, 20.0)
        self.dwell_time_box.setSingleStep(0.1)
        self.dwell_time_box.setValue(1.0)

        self.multipleSweepRestoreCenter = QtGui.QCheckBox('Restore center on stop')
        self.multipleSweepRestoreCenter.setChecked(False)

        self.multipleSweepRepeat = QtGui.QCheckBox('Repeat')
        self.multipleSweepRepeat.setChecked(True)

        self.multipleSweepUseCurrentButton = QtGui.QPushButton('Use Current')
        self.multipleSweepStartButton = QtGui.QPushButton('Start')
        self.multipleSweepStopButton = QtGui.QPushButton('Stop')
        self.multipleSweepStartButton.setEnabled(self.multipole_step_state)
        self.multipleSweepStopButton.setEnabled(not self.multipole_step_state)
        self.MultipleSweepStatus = QtGui.QLabel('Idle')

        layout.addWidget(QtGui.QLabel("Dwell Time [s]"), n+1, 0)
        layout.addWidget(self.dwell_time_box, n+1, 2)
        layout.addWidget(self.multipleSweepRestoreCenter, n+2, 0, 1, 2)
        layout.addWidget(self.multipleSweepRepeat, n+2, 2, 1, 2)
        layout.addWidget(self.multipleSweepUseCurrentButton, n+3, 0, 1, 5)
        layout.addWidget(self.multipleSweepStartButton, n+4, 0, 1, 2)
        layout.addWidget(self.multipleSweepStopButton, n+4, 2, 1, 3)

        self.multipleSweepStartButton.released.connect(self.startMultiSweep)
        self.multipleSweepStopButton.released.connect(self.StopMultiSweep)
        self.multipleSweepUseCurrentButton.released.connect(self.useCurrentMultipleSweepCenter)
        self.multipleSweepRepeat.stateChanged.connect(self.RepeatStateChanged)
   

        box.setLayout(layout)
        return box
    
    def setDefaultSweepMultipole(self, multipole):
        index = self.sweepMultipole.findText(multipole)
        if index >= 0:
            self.sweepMultipole.setCurrentIndex(index)

    def setDefaultStepMultipole(self, multipole):
        index = self.stepMultipole.findText(multipole)
        if index >= 0:
            self.stepMultipole.setCurrentIndex(index)
    
    def setDefaultMultipleSweepMultipole(self, multipoles):
        for (box, mp) in zip(self.multipoleboxes, multipoles):
            index = box.findText(mp)
            if index >= 0:
                box.setCurrentIndex(index)
        
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
        # self.pLabel.setText('H: ' + str(self.position))

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
        # self.pLabel.setText('H: ' + str(temp_position))
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
        # self.pLabel.setText('H: ' + str(temp_position))
        # change multipoles
        temp_multipoles = yield self.dacserver.get_multipole_values(2)
        for k, v in temp_multipoles:
            self.controls[k].spinLevel.setValue(v)

    # zero all multipole values and gamma, keeping the height the same
    def zeroMultipoles(self):
        self.inputUpdated = True
        for k in self.multipoles:
            self.controls[k].spinLevel.setValue(0.0)

    def useCurrentSweepCenter(self):
        multipole = str(self.sweepMultipole.currentText())
        try:
            center = self.controls[multipole].spinLevel.value()
        except KeyError:
            return
        self.sweepCenter.setValue(center)

    def useCurrentStepCenter(self):
        multipole = str(self.stepMultipole.currentText())
        try:
            center = self.controls[multipole].spinLevel.value()
        except KeyError:
            return
        self.stepCenter.setValue(center)

    def useCurrentMultipleSweepCenter(self):
        for mpbox, centerbox in zip(self.multipoleboxes, self.multipolecenter):
            multipole = str(mpbox.currentText())
            try:
                center = self.controls[multipole].spinLevel.value()
            except KeyError:
                return
            centerbox.setValue(center)

    @inlineCallbacks
    def startMultipoleSweep(self):
        multipole = str(self.sweepMultipole.currentText())
        center = float(self.sweepCenter.value())
        amplitude = float(self.sweepAmplitude.value())
        frequency = float(self.sweepFrequency.value())
        update_rate = float(self.sweepUpdateRate.value())

        self.sweepStatus.setText('Starting...')
        try:
            yield self.dacserver.start_multipole_oscillation(
                multipole, center, amplitude, frequency, update_rate
            )
        except Exception, e:
            self.sweepStatus.setText('Start failed')
            self.sweepStartButton.setEnabled(True)
            msgBox = QtGui.QMessageBox(
                QtGui.QMessageBox.Warning,
                'Multipole Sweep',
                str(e)
            )
            msgBox.exec_()
            return

        self.sweepStartButton.setEnabled(False)
        
        self.sweepStopButton.setEnabled(True)
        self.sweepStatus.setText('Running: ' + multipole)

    @inlineCallbacks
    def stopMultipoleSweep(self):
        restore_center = bool(self.sweepRestoreCenter.isChecked())

        self.sweepStopButton.setEnabled(False)
        self.sweepStatus.setText('Stopping...')
        try:
            yield self.dacserver.stop_multipole_oscillation(restore_center)
        except Exception, e:
            self.sweepStatus.setText('Stop failed')
            self.sweepStopButton.setEnabled(True)
            msgBox = QtGui.QMessageBox(
                QtGui.QMessageBox.Warning,
                'Multipole Sweep',
                str(e)
            )
            msgBox.exec_()
            return

        self.sweepStartButton.setEnabled(True)
        self.sweepStatus.setText('Idle')

    @inlineCallbacks
    def startMultipoleStep(self):
        multipole = str(self.stepMultipole.currentText())
        center = float(self.stepCenter.value())
        amplitude = float(self.stepAmplitude.value())
        period = float(self.stepPeriod.value())
        update_time = float(self.stepUpdateTime.value())

        self.stepStartButton.setEnabled(False)
        self.stepStatus.setText('Starting...')
        try:
            yield self.dacserver.start_multipole_step(
                multipole, center, amplitude, period, update_time
            )
            print "started multipole step"
        except Exception, e:
            self.stepStatus.setText('Start failed')
            self.stepStartButton.setEnabled(True)
            msgBox = QtGui.QMessageBox(
                QtGui.QMessageBox.Warning,
                'Multipole Step',
                str(e)
            )
            msgBox.exec_()
            # print "error starting multipole step: ", e
            return

        self.stepStopButton.setEnabled(True)
        self.stepStatus.setText('Running: ' + multipole)

    @inlineCallbacks
    def stopMultipoleStep(self):
        restore_center = bool(self.stepRestoreCenter.isChecked())

        self.stepStopButton.setEnabled(False)
        self.stepStatus.setText('Stopping...')
        try:
            yield self.dacserver.stop_multipole_step(restore_center)
        except Exception, e:
            self.stepStatus.setText('Stop failed')
            self.stepStopButton.setEnabled(True)
            msgBox = QtGui.QMessageBox(
                QtGui.QMessageBox.Warning,
                'Multipole Step',
                str(e)
            )
            msgBox.exec_()
            return

        self.stepStartButton.setEnabled(True)
        self.stepStatus.setText('Idle')

    @inlineCallbacks
    def startMultiSweep(self):
        # sweep_names=('Ez', 'Ey', 'Ex')
        # sweep_limits=[
        #     [0.0, 1.0, 0.5],
        #     [0.0, 0.4, 0.2],
        #     [-1.0, 1.0, 0.5],
        # ]

        sweep_names=[]
        sweep_limits=[]
        for mpbox, mpcenter, mpspan, mpstep in zip(self.multipoleboxes,
                                                   self.multipolecenter,
                                                   self.multipolespan,
                                                   self.multipolestep):
            sweep_names.append(str(mpbox.currentText()))
            mpstart=float(mpcenter.value()-mpspan.value())
            mpstop=float(mpcenter.value()+mpspan.value())
            limits=[mpstart, mpstop, mpstep.value()]
            sweep_limits.append(limits)
        
        dwell_time=float(self.dwell_time_box.value())
        repeat=bool(self.multipleSweepRepeat.isChecked())

        print sweep_names
        print sweep_limits

        try:
            yield self.dacserver.start_multi_sweep(sweep_names, sweep_limits, dwell_time, repeat)
        except Exception, e:
            self.MultipleSweepStatus.setText('Start failed')
            self.sweepStartButton.setEnabled(True)
            msgBox = QtGui.QMessageBox(
                QtGui.QMessageBox.Warning,
                'Multipole Sweep',
                str(e)
            )
            msgBox.exec_()
            return

        self.multipleSweepStartButton.setEnabled(False)
        self.multipleSweepStopButton.setEnabled(True)
        
    @inlineCallbacks
    def StopMultiSweep(self):
        restore_center=bool(self.multipleSweepRestoreCenter.isChecked())

        self.multipleSweepStopButton.setEnabled(False)
        self.MultipleSweepStatus.setText('Stopping...')
        try:
            yield self.dacserver.stop_multi_sweep(restore_center)
        except Exception, e:
            self.MultipleSweepStatus.setText('Stop failed')
            self.multipleSweepStopButton.setEnabled(True)
            msgBox = QtGui.QMessageBox(
                QtGui.QMessageBox.Warning,
                'Multipole Step',
                str(e)
            )
            msgBox.exec_()
            return

        self.multipleSweepStartButton.setEnabled(True)
        self.MultipleSweepStatus.setText('Idle')

    @inlineCallbacks
    def RepeatStateChanged(self):
        print "GUI saw the repeat change"
        repeat_state=self.multipleSweepRepeat.isChecked()
        result = yield self.dacserver.change_repeat(repeat_state)
        if result:
            print "Repeat state successfully updated"
        else:
            print "Repeat state failed to update"

        

        
    @inlineCallbacks    
    def setupListeners(self):
        yield self.dacserver.signal__ports_updated(SIGNALID)
        yield self.dacserver.addListener(listener = self.followSignal, source = None, ID = SIGNALID) 
        
    @inlineCallbacks
    def followSignal(self, x, s):
        if self.updating: return
        multipoles = yield self.dacserver.get_multipole_values()
        # print 'followSignal called'
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
        trapElecLayout = [[8,4], [4,0], [2,0], [0,0], [6,6], [2,6], [6,2], [2,2], [0,4], [8,8], [6,8], [4,8], [2,8], [0,8], [8,0], [6,0], [4,2], [4,6]]
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
        # print self.displays
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
        # print 'Eleclist: ', elecList
        if bool(hc.centerElectrode):
            elecList.pop(hc.centerElectrode-1)
        for i,e in enumerate(elecList):
            if bool(hc.sma_dict):
                self.displays[k].setAutoFillBackground(True)
            if int(i) <= 25:
                elecLayout.addWidget(QtGui.QLabel(e), trapElecLayout[int(i)][0], trapElecLayout[int(i)][1])
                elecLayout.addWidget(self.displays[e], trapElecLayout[int(i)][0], trapElecLayout[int(i)][1]+1)
                # print i, e, self.displays[e]
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
        # print av
        brightness = 210
        darkness = 255 - brightness           
        for (k, v) in av:
            # print k
            # print v
            self.displays[k].display("%.3f" % float(v)) 
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
