from common.devel.bum.sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U
import time
from treedict import TreeDict
import numpy as np
from labrad.units import WithUnit

'''
Configuration 7/6/2024
two pulsers, the second pulser for 729 single pass only
All tones will be turned on before pulse sequence
timing is controlled by TTL from the first pulser
'''


class MolmerSorensenGate(pulse_sequence):

    scannable_params = {   'MolmerSorensen.duration': [(0,230.0, 10.0, 'us'),'ms_time'],
                           'MolmerSorensen.amplitude': [(-20, -10, 0.5, 'dBm'),'ms_time'],
                           'MolmerSorensen.detuning': [(-10.0, 10, 0.5, 'kHz'),'ms_time'],
                           'MolmerSorensen.phase': [(0, 360, 15, 'deg'),'parity'],
                           'MolmerSorensen.analysis_phase': [(0, 360, 15, 'deg'),'parity'],
                           'MolmerSorensen.ac_stark_shift': [(-10.0, 10, 0.5, 'kHz'),'ms_time',],
                           'MolmerSorensen.asymetric_ac_stark_shift': [(-10.0, 10, 0.5, 'kHz'),'ms_time',],
                        }

    show_params= [        'MolmerSorensen.duration',
                          'MolmerSorensen.line_selection',
                          'MolmerSorensen.sideband_selection',
                          'MolmerSorensen.detuning',
                          'MolmerSorensen.ac_stark_shift',
                          'MolmerSorensen.asymetric_ac_stark_shift',
                          'MolmerSorensen.amp_red',
                          'MolmerSorensen.amp_blue',
                          'MolmerSorensen.amplitude',
                          'MolmerSorensen.analysis_pulse_enable',
                          'MolmerSorensen.shape_profile',
                          'MolmerSorensen.bichro_enable',
                          'MolmerSorensen.analysis_duration',
                          'MolmerSorensen.analysis_amplitude',
                          'MolmerSorensen.analysis_phase',
                  ]

    @classmethod
    def run_initial(cls, cxn, parameters_dict):
        
        # import labrad
        # cxn = labrad.connect()
        # address 7 is 729DP2_SPST
        # address 6 is 729DP2_SPTT1
        # address 2 is 729DP2_SPTT2

        ms = parameters_dict.MolmerSorensen

        SPcenter_729 = WithUnit(80.0, 'MHz')
        SPamp_729_max = WithUnit(-10.0, 'dBm')

        mode = ms.sideband_selection
        trap_frequency = parameters_dict['TrapFrequencies.' + mode]
        freq_blue = SPcenter_729 - trap_frequency - ms.detuning - ms.asymetric_ac_stark_shift
        freq_red = SPcenter_729 + trap_frequency + ms.detuning

        amp_blue = ms.amp_blue
        amp_red = ms.amp_red

        cxn.pulser2.frequency('729DP2_SPST', SPcenter_729)
        cxn.pulser2.frequency('729DP2_SPTT1', freq_red)
        cxn.pulser2.frequency('729DP2_SPTT2', freq_blue)

        cxn.pulser2.amplitude('729DP2_SPST', SPamp_729_max)
        cxn.pulser2.amplitude('729DP2_SPTT1', amp_red)
        cxn.pulser2.amplitude('729DP2_SPTT2', amp_blue)

        cxn.pulser2.output('729DP2_SPST', True)
        cxn.pulser2.output('729DP2_SPTT1', True)
        cxn.pulser2.output('729DP2_SPTT2', True)

        time.sleep(1.0)
        cxn.normalpmtflow.set_mode("Normal")
        pass
        

    @classmethod
    def run_in_loop(cls,cxn, parameters_dict, data, x):
        # print "x and data:", x, data
        pass

    @classmethod
    def run_finally(cls,cxn, parameters_dict, data, x):
        cxn.pulser2.output('729DP2_SPST', False)
        cxn.pulser2.output('729DP2_SPTT1', False)
        cxn.pulser2.output('729DP2_SPTT2', False)

    def sequence(self):        
        from subsequences.StatePreparation import StatePreparation
        from subsequences.MolmerSorensen import MolmerSorensen
        from subsequences.StateReadout import StateReadout
        from subsequences.TurnOffAll import TurnOffAll
        from subsequences.EmptySequence import EmptySequence

        ms = self.parameters.MolmerSorensen
        freq_729 = self.calc_freq(ms.line_selection)

        self.end = U(10., 'us')
        self.addSequence(StatePreparation, {'SidebandCooling.single_pass_twotone': True})
        self.addSequence(MolmerSorensen, {'MolmerSorensen.frequency': freq_729,
                                          'MolmerSorensen.phase': ms.phase,
                                          'MolmerSorensen.analysis_duration': ms.analysis_duration,
                                          'MolmerSorensen.analysis_amplitude': ms.analysis_amplitude,
                                          'MolmerSorensen.analysis_phase': ms.analysis_phase,
                                          })
        self.addSequence(StateReadout)



class MolmerSorensenCalcPop(MolmerSorensenGate):

    scannable_params = {
        'MolmerSorensen.point' : [(1., 1., 1., ''),'current'],
              }

    @classmethod
    def run_finally(cls,cxn, parameters_dict, data, x):
        cxn.pulser2.output('729DP2_SPST', False)
        cxn.pulser2.output('729DP2_SPTT1', False)
        cxn.pulser2.output('729DP2_SPTT2', False)

    	SS = 1 - data[-1][0] - data[-1][1]
    	SDDS = data[-1][1]
    	DD = data[-1][0]
        avrage_D = data[-1][0] + data[-1][1] / 2
        parity = SS + DD - SDDS
        return SS, SDDS, DD, avrage_D, parity



class MolmerSorensenAllPop(pulse_sequence):

    scannable_params = {   'MolmerSorensen.duration': [(0,230.0, 10.0, 'us'),'ms_time'],
                           'MolmerSorensen.amplitude': [(-20, -10, 0.5, 'dBm'),'ms_time'],
                           'MolmerSorensen.detuning': [(-10.0, 10, 0.5, 'kHz'),'ms_time'],
                           'MolmerSorensen.phase': [(0, 360, 15, 'deg'),'parity'],
                           'MolmerSorensen.analysis_phase': [(0, 360, 15, 'deg'),'parity'],
                           'MolmerSorensen.ac_stark_shift': [(-10.0, 10, 0.5, 'kHz'),'ms_time',],
                           'MolmerSorensen.asymetric_ac_stark_shift': [(-10.0, 10, 0.5, 'kHz'),'ms_time',],
                        }

    show_params= [        'MolmerSorensen.duration',
                          'MolmerSorensen.line_selection',
                          'MolmerSorensen.sideband_selection',
                          'MolmerSorensen.detuning',
                          'MolmerSorensen.ac_stark_shift',
                          'MolmerSorensen.asymetric_ac_stark_shift',
                          'MolmerSorensen.amp_red',
                          'MolmerSorensen.amp_blue',
                          'MolmerSorensen.amplitude',
                          'MolmerSorensen.analysis_pulse_enable',
                          'MolmerSorensen.shape_profile',
                          'MolmerSorensen.bichro_enable',
                          'MolmerSorensen.analysis_duration',
                          'MolmerSorensen.analysis_amplitude',
                          'MolmerSorensen.analysis_phase',
                  ]

    sequence = MolmerSorensenCalcPop


