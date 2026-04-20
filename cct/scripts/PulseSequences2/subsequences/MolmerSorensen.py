from common.devel.bum.sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit

class MolmerSorensen(pulse_sequence):
    
    
    def sequence(self):

        #this hack will be not needed with the new dds parsing methods
        slope_dict = {0:0.0, 2:2.0, 4:5.0, 6:600.0}
        
        ms = self.parameters.MolmerSorensen
        frequency_advance_duration = WithUnit(6, 'us')

        freq_729dp = ms.frequency + ms.ac_stark_shift

        print "Running MS subseq freq 729: ", freq_729dp 
        print "MS params" , self.parameters.MolmerSorensen.ac_stark_shift

        try:
            slope_duration = WithUnit(int(slope_dict[ms.shape_profile]),'us')
        except KeyError:
            raise Exception('Cannot find shape profile: ' + str(ms.shape_profile))

        ampl_off = WithUnit(-48.0, 'dBm')

        if ms.analysis_pulse_enable:
            self.end = self.start + 2*frequency_advance_duration + ms.duration + slope_duration + ms.analysis_duration
        else:
            self.end = self.start + 2*frequency_advance_duration + ms.duration + slope_duration

        self.addTTL('729cw', self.start, self.end - self.start)

        # SP: advance the frequency and amplitude for the whole period, depending on bichro or not
        if ms.bichro_enable:
            print "bichro enabled-> running ms gate ioi"
            self.addTTL('729bichro', self.start, ms.duration + 1.5*frequency_advance_duration + slope_duration)
        else:
            print "MS subseq bichro IS NOT enabled-> running a carrier"

        # DP:first advance the frequency but keep amplitude low
        self.addDDS('729DP2', self.start, frequency_advance_duration, freq_729dp, ampl_off)
        
        # Ramp up the DP
        self.addDDS('729DP2', self.start + frequency_advance_duration, ms.duration, freq_729dp, 
                    ms.amplitude, phase = ms.phase,
                    profile=int(ms.shape_profile)
                    )

        if ms.analysis_pulse_enable:
            print "scan phase enabled : " , ms.analysis_phase
            self.addDDS('729DP2', self.start + 2*frequency_advance_duration + ms.duration + slope_duration, ms.analysis_duration,
                        freq_729dp, ms.analysis_amplitude, phase = ms.analysis_phase
                        )
        
       

