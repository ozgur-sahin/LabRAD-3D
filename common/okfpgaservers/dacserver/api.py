import ok
from DacConfiguration_Horizontal import hardwareConfiguration

class api(object):
    '''class containing all commands for interfacing with the fpga'''
    def __init__(self):
        self.xem = None
        self.okDeviceID = hardwareConfiguration.okDeviceID
        self.okDeviceFile = hardwareConfiguration.okDeviceFile
        
    def checkConnection(self):
        if self.xem is None: raise Exception("FPGA not connected")
    
    def connectOKBoard(self):
        fp = ok.FrontPanel()
        # print "Done Not High Error Code=", ok.FrontPanel.DoneNotHigh
        module_count = fp.GetDeviceCount()
        print "Found {} unused modules".format(module_count)
        for i in range(module_count):
            serial = fp.GetDeviceListSerial(i)
            tmp = ok.FrontPanel()
            ret = tmp.OpenBySerial(serial)
            # print "OpenBySerial returned: ", ret
            iden = tmp.GetDeviceID()
            if iden == self.okDeviceID:
                self.xem = tmp
                print 'Connected to {}'.format(iden)
                self.programOKBoard()
                return True
        return False
    
    def programOKBoard(self):
        print "Is xem open:", self.xem.IsOpen()
        self.xem.ResetFPGA()
        print "resetted FPGA"
        import time
        time.sleep(0.2)
        prog = self.xem.ConfigureFPGA(self.okDeviceFile)
        if prog: 
            print "Not able to program FPGA, error code: ", prog
            raise Exception("Not able to program FPGA, error code: " + str(prog))
        print "ConfigureFPGA finished"
        pll = ok.PLL22150()
        print "pll initialization successful."
        self.xem.GetEepromPLL22150Configuration(pll)
        print "GetEeprom successful"
        pll.SetDiv1(pll.DivSrc_VCO,4)
        self.xem.SetPLL22150Configuration(pll)
        print "Programmed OK Board"
        
    def programBoard(self, sequence):
        self.xem.WriteToBlockPipeIn(0x80, 2, sequence)
    
    def resetFIFODAC(self):
        self.xem.ActivateTriggerIn(0x40,8)  
        
    def setDACVoltage(self, volstr):
        self.xem.WriteToBlockPipeIn(0x82, 2, volstr)   

