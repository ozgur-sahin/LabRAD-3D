from common.devel.bum.sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U
from treedict import TreeDict
import numpy as np

class MotionAnalysisSpectrum(pulse_sequence):
    
                          
    scannable_params = {   'Motion_Analysis.detuning': [(0,200.0, 50.0, 'kHz'),'spectrum'],
                           'Motion_Analysis.amplitude_397': [(-25.0,-13.0, 1.0, 'dBm'),'current']}
 

    show_params= [
                  'Motion_Analysis.pulse_width_397',
                  'Motion_Analysis.amplitude_397',
                  'Motion_Analysis.sideband_selection',
                  'Motion_Analysis.line_selection',
                  'Motion_Analysis.detuning',
                  'Motion_Analysis.channel_729',

                  'Motion_Analysis.duration_729',
                  'Motion_Analysis.amplitude_729'

                ]

    fixed_params = {'Display.relative_frequencies': True

                    }
    
    @classmethod
    def run_initial(cls, cxn, parameters_dict):
        
        awg = cxn.keysight_33600a

        tf = parameters_dict.TrapFrequencies
        ma = parameters_dict.Motion_Analysis
        sideband_selection = ma.sideband_selection
        sideband_frequencies = [tf.radial_frequency_1, tf.radial_frequency_2, tf.axial_frequency, tf.rf_drive_frequency, 0]
        
        freq = U(0,'MHz')
        for order,sideband_frequency in zip(sideband_selection, sideband_frequencies):
            freq += order * sideband_frequency

        freq = freq + ma.detuning
        awg.program_square_wave(freq['kHz'],5.,0.,50.)
    
    @classmethod
    def run_in_loop(cls, cxn, parameters_dict, data_so_far,data_x):
        awg = cxn.keysight_33600a

        tf = parameters_dict.TrapFrequencies
        ma = parameters_dict.Motion_Analysis
        sideband_selection = ma.sideband_selection
        sideband_frequencies = [tf.radial_frequency_1, tf.radial_frequency_2, tf.axial_frequency, tf.rf_drive_frequency, 0]
        
        freq = U(0,'MHz')
        for order,sideband_frequency in zip(sideband_selection, sideband_frequencies):
            freq += order * sideband_frequency

        freq = freq + ma.detuning
        awg.program_square_wave(freq['kHz'],5.,0.,50.)
        

    @classmethod
    def run_finally(cls,cxn, parameters_dict, data, x):
        awg = cxn.keysight_33600a
        awg.set_state(1,0) 

        
    def sequence(self):        
        from subsequences.StatePreparation import StatePreparation
        from subsequences.RabiExcitation import RabiExcitation
        from subsequences.StateReadout import StateReadout
        from subsequences.EmptySequence import EmptySequence
        from subsequences.MotionAnalysis import MotionAnalysis
        from subsequences.OpticalPumping import OpticalPumping
        
        # additional optical pumping duratrion 
        duration_op= self.parameters.SidebandCooling.sideband_cooling_optical_pumping_duration

        ## calculate the final diagnosis params
        ma = self.parameters.Motion_Analysis
        freq_729 = self.calc_freq_from_array(ma.line_selection, ma.sideband_selection)
        print freq_729

        self.addSequence(StatePreparation)
        # 397 excitation 
        self.addSequence(MotionAnalysis)
        # small optical pumping after the motion excitation
        self.addSequence(OpticalPumping, {'OpticalPumpingContinuous.optical_pumping_continuous_duration':duration_op })

        # 729 excitation to transfer the motional DOF to the electronic DOF
        # running the excitation from the Rabi flopping 
        self.addSequence(RabiExcitation, {'Excitation_729.rabi_excitation_frequency': freq_729,
                                          'Excitation_729.rabi_excitation_amplitude': ma.amplitude_729,
                                          'Excitation_729.rabi_excitation_duration':  ma.duration_729,
                                          "Excitation_729.channel_729":ma.channel_729})

        
        self.addSequence(StateReadout)





