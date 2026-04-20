from common.devel.bum.sequences.pulse_sequence import pulse_sequence
#from pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U
from treedict import TreeDict
import numpy as np

class MotionalRamsey729Half(pulse_sequence):


    scannable_params = {
                        
        'Motion_Analysis.duration_729': [(0, 500, 10, 'us') ,'rabi'],
        'Motion_Analysis.detuning': [(-10, 10, 1, 'kHz') ,'sideband_stark_shift'], 
        
        }

    show_params= ['Ramsey.ramsey_time',
                  'Ramsey.detuning',
                  'Ramsey.amplitude_729',
                  'Ramsey.channel_729',
                  'Ramsey.dynamic_decoupling_enable',

                  'Ramsey.first_pulse_line',
                  'Ramsey.first_pulse_sideband',
                  'Ramsey.first_pulse_duration',

                  'Ramsey.second_pulse_line',
                  'Ramsey.second_pulse_sideband',
                  'Ramsey.second_pulse_duration',
                  'Ramsey.second_pulse_phase',

                  'DynamicDecoupling.dd_line_selection',
                  'DynamicDecoupling.dd_sideband_selection',
                  'DynamicDecoupling.dd_channel_729',
                  'DynamicDecoupling.dd_repetitions',
                  'DynamicDecoupling.dd_pi_time',
                  'DynamicDecoupling.dd_amplitude_729',

                  'Motion_Analysis.channel_729',
                  'Motion_Analysis.amplitude_729',
                  'Motion_Analysis.duration_729',
                  'Motion_Analysis.line_selection',
                  'Motion_Analysis.sideband_selection',
                  'Motion_Analysis.detuning',

                  'EmptySequence.empty_sequence_duration',
                  'StateReadout.repeat_each_measurement',
                  ]

    
    def sequence(self):
        
        from subsequences.StatePreparation import StatePreparation
        from subsequences.RabiExcitation import RabiExcitation
        from subsequences.StateReadout import StateReadout
        from subsequences.EmptySequence import EmptySequence
        from subsequences.StateReadout import StateReadout
        from subsequences.DynamicDecoupling import DynamicDecoupling
        
        r = self.parameters.Ramsey
        dd = self.parameters.DynamicDecoupling
        ma = self.parameters.Motion_Analysis

        first_freq_729 = self.calc_freq_from_array(r.first_pulse_line, r.first_pulse_sideband)
        # final_freq_729 = self.calc_freq_from_array(r.second_pulse_line, r.second_pulse_sideband)
        motional_freq_729 = self.calc_freq_from_array(ma.line_selection, ma.sideband_selection)

        motional_freq_729 += ma.detuning

        # add Ramsey detuning
        first_freq_729 += self.parameters.Ramsey.detuning
        # final_freq_729 += self.parameters.Ramsey.detuning

        # ampl_off = U(-48.0, 'dBm')
        # frequency_advance_duration = U(6, 'us')

        # building the sequence
        self.addSequence(StatePreparation)
        self.addSequence(EmptySequence)
        # Carrier pi/2 pulse
        self.addSequence(RabiExcitation, { "Excitation_729.rabi_excitation_frequency" : first_freq_729,
                                           "Excitation_729.rabi_excitation_duration" : r.first_pulse_duration,
                                           "Excitation_729.rabi_excitation_amplitude" : r.amplitude_729,
                                           "Excitation_729.rabi_excitation_phase" : U(0, 'deg'),
                                           "Excitation_729.channel_729" : r.channel_729,
                                          })
        # RSB pi pulse
        self.addSequence(RabiExcitation, { "Excitation_729.rabi_excitation_frequency" : motional_freq_729,
                                           "Excitation_729.rabi_excitation_duration" : ma.duration_729,
                                           "Excitation_729.rabi_excitation_amplitude" : ma.amplitude_729,
                                           "Excitation_729.rabi_excitation_phase" : U(0, 'deg'),
                                           "Excitation_729.channel_729" : ma.channel_729,
                                          })

        self.addSequence(StateReadout)

    @classmethod
    def run_initial(cls,cxn, parameters_dict):
      cxn.normalpmtflow.set_mode("Normal")
      pass
        
    @classmethod
    def run_in_loop(cls,cxn, parameters_dict, data, x):
      pass
    
    @classmethod
    def run_finally(cls,cxn, parameters_dict, data, x):
      pass