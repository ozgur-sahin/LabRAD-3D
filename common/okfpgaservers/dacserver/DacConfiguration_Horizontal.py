class channelConfiguration(object):
    """
    Stores complete information for each DAC channel
    """


    def __init__(self, dacChannelNumber, trapElectrodeNumber = None, smaOutNumber = None, name = None, boardVoltageRange = (-40, 40), allowedVoltageRange = (-40, 40)):
        self.dacChannelNumber = dacChannelNumber
        self.trapElectrodeNumber = trapElectrodeNumber
        self.smaOutNumber = smaOutNumber
        self.boardVoltageRange = boardVoltageRange
        self.allowedVoltageRange = allowedVoltageRange
        self.calibration = []
        if (name == None) & (trapElectrodeNumber != None):
            self.name = str(trapElectrodeNumber).zfill(2)
        else:
            self.name = name

    def setCalibrationParams(self, c):
        self.calibration = c
    def computeDigitalVoltage(self, analogVoltage):
        return int(round(sum([ self.calibration[n] * analogVoltage ** n for n in range(len(self.calibration)) ])))

class hardwareConfiguration(object):
    EXPNAME = 'CCT'
    default_multipoles = ['Ex','Ey','Ez','U1','U2','U3','U4','U5']
    okDeviceID = 'DAC Controller'
    okDeviceFile = 'control_noninverted.bit'
    centerElectrode = False #write False if no Centerelectrode
    PREC_BITS = 16
    pulseTriggered = True
    maxCache = 126
    filter_RC = 5e4 * 4e-7
    elec_dict = {
    	# This is the mapping of DAC chip to DAC output pin

        #horizontal trap, circular breakout board
        'T-DC1': channelConfiguration(1, trapElectrodeNumber='T-DC1'), # endcap
        'T-DC2': channelConfiguration(8, trapElectrodeNumber='T-DC2'), #endcap
        'T-DC3': channelConfiguration(17, trapElectrodeNumber='T-DC3'), #finger
        'T-DC4': channelConfiguration(4, trapElectrodeNumber='T-DC4'), #finger
        'T-DC5': channelConfiguration(3, trapElectrodeNumber='T-DC5'), #finger
        'T-DC6': channelConfiguration(16, trapElectrodeNumber='T-DC6'), #finger
        'T-DC7': channelConfiguration(15, trapElectrodeNumber='T-DC7'), #finger
        'T-DC8': channelConfiguration(22, trapElectrodeNumber='T-DC8'), #finger
        'T-DC9': channelConfiguration(10, trapElectrodeNumber='T-DC9'), #finger
        'T-DC10': channelConfiguration(23, trapElectrodeNumber='T-DC10'), #finger
        'T-DC11': channelConfiguration(11, trapElectrodeNumber='T-DC11'), #finger
        'T-DC12': channelConfiguration(24, trapElectrodeNumber='T-DC12'), #finger
        'T-DC13': channelConfiguration(6, trapElectrodeNumber='T-DC13'), #center
        'T-DC14': channelConfiguration(14, trapElectrodeNumber='T-DC14'), #center
        'T-DC15': channelConfiguration(21, trapElectrodeNumber='T-DC15'), #center
        'T-DC16': channelConfiguration(12, trapElectrodeNumber='T-DC16'), #center
        'T-RF1 bias': channelConfiguration(2, trapElectrodeNumber='T-RF1 bias'), # RF1 bias
        'T-RF2 bias': channelConfiguration(5, trapElectrodeNumber='T-RF2 bias'), # RF2 bias

        # # Calbration:
        # '06': channelConfiguration(6, trapElectrodeNumber=6),
        # '07': channelConfiguration(7, trapElectrodeNumber=7),
        # '08': channelConfiguration(8, trapElectrodeNumber=8),
        # '09': channelConfiguration(9, trapElectrodeNumber=9),
        # '10': channelConfiguration(10, trapElectrodeNumber=10),
        # '11': channelConfiguration(11, trapElectrodeNumber=11),
        # '12': channelConfiguration(12, trapElectrodeNumber=12),
        # '13': channelConfiguration(13, trapElectrodeNumber=13),
        # '14': channelConfiguration(14, trapElectrodeNumber=14),
        # '15': channelConfiguration(15, trapElectrodeNumber=15),
        # '16': channelConfiguration(16, trapElectrodeNumber=16),
        # '17': channelConfiguration(17, trapElectrodeNumber=17),
        # '18': channelConfiguration(18, trapElectrodeNumber=18),
        # '19': channelConfiguration(19, trapElectrodeNumber=19),
        # '20': channelConfiguration(20, trapElectrodeNumber=20),
        # '21': channelConfiguration(21, trapElectrodeNumber=21),
        # '22': channelConfiguration(22, trapElectrodeNumber=22),
        # '23': channelConfiguration(23, trapElectrodeNumber=23),
        # '24': channelConfiguration(24, trapElectrodeNumber=24),
        # '25': channelConfiguration(25, trapElectrodeNumber=25),
        # '26': channelConfiguration(26, trapElectrodeNumber=26),
        # '27': channelConfiguration(27, trapElectrodeNumber=27),
        # '28': channelConfiguration(28, trapElectrodeNumber=28)




        # Old ones:

        # #3D 75um vertical trap, old breakout board
        # '01': channelConfiguration(7, trapElectrodeNumber=1),
        # '02': channelConfiguration(6, trapElectrodeNumber=2),
        # '03': channelConfiguration(12, trapElectrodeNumber=3),
        # '04': channelConfiguration(9, trapElectrodeNumber=4),
        # '05': channelConfiguration(11, trapElectrodeNumber=5),
        # '06': channelConfiguration(10, trapElectrodeNumber=6),
        # '07': channelConfiguration(8, trapElectrodeNumber=7),
        # '08': channelConfiguration(14, trapElectrodeNumber=8),
        # '09': channelConfiguration(13, trapElectrodeNumber=9), # center
        # '10': channelConfiguration(15, trapElectrodeNumber=10), # RF1 bias
        # '11': channelConfiguration(16, trapElectrodeNumber=11), # RF2 bias



        # CCT setup
        # '01': channelConfiguration(13, trapElectrodeNumber=1), #24 #11
        # '02': channelConfiguration(6, trapElectrodeNumber=2), #2 #6
        # '03': channelConfiguration(5, trapElectrodeNumber=3), #4 #14
        # '04': channelConfiguration(14, trapElectrodeNumber=4), #10 #13
        # '05': channelConfiguration(2, trapElectrodeNumber=5), #12 #17
        # '06': channelConfiguration(12, trapElectrodeNumber=6), #27 #3
        # '07': channelConfiguration(18, trapElectrodeNumber=7), #25 #5
        # '08': channelConfiguration(15, trapElectrodeNumber=8), #7 #19
        # '09': channelConfiguration(9, trapElectrodeNumber=9), #5
        # '10': channelConfiguration(10, trapElectrodeNumber=10), #19
        # '11': channelConfiguration(11, trapElectrodeNumber=11), #13
        # '12': channelConfiguration(16, trapElectrodeNumber=12), #14
        # '13': channelConfiguration(3, trapElectrodeNumber=13), #3
        # '14': channelConfiguration(19, trapElectrodeNumber=14), #17
        # '15': channelConfiguration(7, trapElectrodeNumber=15), #11
        # '16': channelConfiguration(17, trapElectrodeNumber=16), #6
        # # The following are for the single trap
        # '17': channelConfiguration(1, trapElectrodeNumber=17),
        # '18': channelConfiguration(4, trapElectrodeNumber=18),
        # '19': channelConfiguration(23, trapElectrodeNumber=19),
        # '20': channelConfiguration(24, trapElectrodeNumber=20),
        # '21': channelConfiguration(25, trapElectrodeNumber=21),
        # '22': channelConfiguration(26, trapElectrodeNumber=22),
        # '23': channelConfiguration(27, trapElectrodeNumber=23),
        # '24': channelConfiguration(20, trapElectrodeNumber=24),
        # '25': channelConfiguration(8, trapElectrodeNumber=25) #CNT
        # # '26': channelConfiguration(1, trapElectrodeNumber=23),
        # # '27': channelConfiguration(16, trapElectrodeNumber=27),
        # # '28': channelConfiguration(22, trapElectrodeNumber=28)
        }

    notused_dict = {

        #75um vertical trap, circular breakout board
        'V-DC0': channelConfiguration(28, trapElectrodeNumber='V-DC0'), # center
        'V-DC1': channelConfiguration(6, trapElectrodeNumber='V-DC1'),
        'V-DC2': channelConfiguration(7, trapElectrodeNumber='V-DC2'),
        'V-DC3': channelConfiguration(24, trapElectrodeNumber='V-DC3'),
        'V-DC4': channelConfiguration(16, trapElectrodeNumber='V-DC4'),
        'V-DC5': channelConfiguration(25, trapElectrodeNumber='V-DC5'),
        'V-DC6': channelConfiguration(27, trapElectrodeNumber='V-DC6'),
        'V-DC7': channelConfiguration(8, trapElectrodeNumber='V-DC7'),
        'V-DC8': channelConfiguration(26, trapElectrodeNumber='V-DC8'),
        'V-RF1 bias': channelConfiguration(18, trapElectrodeNumber='V-RF1 bias'), # RF1 bias
        'V-RF2 bias': channelConfiguration(13, trapElectrodeNumber='V-RF2 bias'), # RF2 bias

        #Totally unused electrodes
        'Channel01':channelConfiguration(1, trapElectrodeNumber='Channel01'),
        'Channel02':channelConfiguration(2, trapElectrodeNumber='Channel02'),
        'Channel03':channelConfiguration(3, trapElectrodeNumber='Channel03'),
        'Channel04':channelConfiguration(4, trapElectrodeNumber='Channel04'), # broken
        'Channel05':channelConfiguration(5, trapElectrodeNumber='Channel05'),
        'Channel23':channelConfiguration(23, trapElectrodeNumber='Channel23'),
        
               }

    sma_dict = {
        #'RF bias 1': channelConfiguration(1, smaOutNumber=1, name='RF bias 1', boardVoltageRange=(-40., 40.), allowedVoltageRange=(-40., 40.)),
        # 'RF bias 2': channelConfiguration(9, smaOutNumber=2, name='RF bias 2', boardVoltageRange=(-40., 40.), allowedVoltageRange=(-40., 40.)),
        # 'RF bias 3': channelConfiguration(10, smaOutNumber=3, name='RF bias 3', boardVoltageRange=(-40., 40.), allowedVoltageRange=(-40., 40.)),
        # 'RF bias 4': channelConfiguration(15, smaOutNumber=4, name='RF bias 4', boardVoltageRange=(-40., 40.), allowedVoltageRange=(-40., 40.)),
        # 'RF bias 5': channelConfiguration(18, smaOutNumber=5, name='RF bias 5', boardVoltageRange=(-40., 40.), allowedVoltageRange=(-40., 40.)),
        # 'RF bias 6': channelConfiguration(20, smaOutNumber=6, name='RF bias 6', boardVoltageRange=(-40., 40.), allowedVoltageRange=(-40., 40.)),
        # 'RF bias 7': channelConfiguration(21, smaOutNumber=7, name='RF bias 7', boardVoltageRange=(-40., 40.), allowedVoltageRange=(-40., 40.))
        # 'RF bias': channelConfiguration(1, smaOutNumber=1, name='RF bias', boardVoltageRange=(-40., 40.), allowedVoltageRange=(-2.0, 0))
        }
