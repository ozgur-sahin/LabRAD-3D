from common.devel.bum.sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit

class MolmerSorensen(pulse_sequence):
    
    
    def sequence(self):

        #this hack will be not needed with the new dds parsing methods
        slope_dict = {0:0.0, 2:2.0, 4:5.0, 6:600.0}
        
        ms = self.parameters.MolmerSorensen
        frequency_advance_duration = WithUnit(6, 'us')

        SPcenter_729 = WithUnit(80.0, 'MHz')
        SPamp_729_max = WithUnit(-10.0, 'dBm')

        mode = ms.sideband_selection
        trap_frequency = self.parameters['TrapFrequencies.' + mode]
        freq_blue = SPcenter_729 - trap_frequency - ms.detuning - ms.asymetric_ac_stark_shift
        freq_red = SPcenter_729 + trap_frequency + ms.detuning

        amp_blue = ms.amp_blue
        amp_red = ms.amp_red

        freq_729dp = ms.frequency + ms.ac_stark_shift

        print "Running MS subseq freq 729: ", freq_729dp 
        print "MS params" , self.parameters.MolmerSorensen.ac_stark_shift

        try:
            slope_duration = WithUnit(int(slope_dict[ms.shape_profile]),'us')
        except KeyError:
            raise Exception('Cannot find shape profile: ' + str(ms.shape_profile))

        ampl_off = WithUnit(-48.0, 'dBm')
        self.end = self.start + 3*frequency_advance_duration + ms.duration + slope_duration

        self.addDDS('729DP2_SPTT1', self.start, frequency_advance_duration, 
                        freq_red, ampl_off, phase = WithUnit(0, 'deg'))
        self.addDDS('729DP2_SPTT2', self.start, frequency_advance_duration, 
                        freq_blue, ampl_off, phase = WithUnit(0, 'deg'))
        self.addDDS('729DP2_SPST', self.start, frequency_advance_duration, 
                        SPcenter_729, ampl_off, phase = WithUnit(0, 'deg'))

        # SP: advance the frequency and amplitude for the whole period, depending on bichro or not
        if ms.bichro_enable:
            print "bichro enabled-> running ms gate ioi"
            self.addTTL('729bichro', self.start, ms.duration + 3*frequency_advance_duration + slope_duration)

            self.addDDS('729DP2_SPTT1', self.start + frequency_advance_duration, ms.duration + 2*frequency_advance_duration + slope_duration, 
                        freq_red, amp_red)
            self.addDDS('729DP2_SPTT2', self.start + frequency_advance_duration, ms.duration + 2*frequency_advance_duration + slope_duration, 
                        freq_blue, amp_blue, 
                        phase = WithUnit(180, 'deg')
                        )
        else:
            print "MS subseq bichro IS NOT enabled-> running a carrier"
            self.addDDS('729DP2_SPST', self.start + frequency_advance_duration, 
                        ms.duration + 2*frequency_advance_duration + slope_duration, SPcenter_729, SPamp_729_max)

        # DP:first advance the frequency but keep amplitude low
        self.addDDS('729DP2', self.start, 2*frequency_advance_duration, freq_729dp, ampl_off)
        
        # Ramp up the DP
        self.addDDS('729DP2', self.start + 2*frequency_advance_duration, ms.duration, freq_729dp, 
                    ms.amplitude, phase = ms.phase, 
                    # freq_ramp_rate = WithUnit(0, 'MHz'), amp_ramp_rate = WithUnit(0, 'dB')
                    # profile=int(ms.shape_profile)
                    )


        self.addDDS('729DP2', self.start + 2*frequency_advance_duration + slope_duration + ms.duration, frequency_advance_duration, 
                    freq_729dp, ampl_off, 
                    # freq_ramp_rate = WithUnit(0, 'MHz'), amp_ramp_rate = WithUnit(0, 'dB')
                    # profile=int(ms.shape_profile)
                    )

