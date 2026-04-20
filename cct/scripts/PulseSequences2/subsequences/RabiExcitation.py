from common.devel.bum.sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit

  
class RabiExcitation(pulse_sequence):
    '''
    Runs a 729 excitation with the Excitation_729 params
    channel_729
    
    rabi_excitation_amp
    rabi_excitation_duration
    rabi_excitation_frequency
    rabi_excitation_phase
    '''
    

    def sequence(self):
        
        ampl_off = WithUnit(-48.0, 'dBm')
        frequency_advance_duration = WithUnit(6, 'us')
        
        freq_729 = self.parameters.Excitation_729.rabi_excitation_frequency
        duration_729 = self.parameters.Excitation_729.rabi_excitation_duration
        phase_729 = self.parameters.Excitation_729.rabi_excitation_phase
        amp_729 = self.parameters.Excitation_729.rabi_excitation_amplitude
        channel_729 = self.parameters.Excitation_729.channel_729
        # changeDDS = self.parameters.Excitation_729.rabi_change_DDS
         
        #first advance the frequency but keep amplitude low        
        self.addDDS(channel_729, self.start, frequency_advance_duration, freq_729, ampl_off)
        if channel_729 == '729DP2':
            SPcenter_729 = WithUnit(80.0, 'MHz')
            SPamp_729_max = WithUnit(-10.0, 'dBm')
            self.addDDS('729DP2_SPST', self.start, frequency_advance_duration, SPcenter_729, ampl_off)
            self.addDDS('729DP2_SPST', self.start + frequency_advance_duration, duration_729, SPcenter_729, SPamp_729_max)
        self.addDDS(channel_729, self.start + frequency_advance_duration, duration_729, freq_729, amp_729, phase_729)
        
        
        self.end = self.start + frequency_advance_duration + duration_729
                    
    