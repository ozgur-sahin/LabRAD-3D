from common.devel.bum.sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit

class SidebandCoolingTwoTone(pulse_sequence):

    def sequence(self):
        from OpticalPumping import OpticalPumping
        
        sc = self.parameters.SidebandCooling
        scc = self.parameters.SidebandCoolingContinuous
        opc = self.parameters.OpticalPumpingContinuous

        channel_854 = '854DP'
        channel_866 = '866DP'
        SPcenter_729 = WithUnit(80.0, 'MHz')

        Nc = int(sc.sideband_cooling_cycles) 

        amp866 = sc.sideband_cooling_amplitude_866
        freq866 = sc.sideband_cooling_frequency_866       

        amp854 = sc.sideband_cooling_amplitude_854
        freq854 = sc.sideband_cooling_frequency_854

        # This channel is the double pass channel which has 
        # an additional single pass AOM to drive two tones
        DPchannel_729 = sc.channel_729 
        amps729_sc_DP = sc.sideband_cooling_amplitude_729
        amps729_sc_SPTT1 = sc.sideband_cooling_amplitude_729_SPTT1
        amps729_sc_SPTT2 = sc.sideband_cooling_amplitude_729_SPTT2

        freq729_sc_dp = self.calc_freq_from_array(sc.line_selection)
        freq729_sc_dp += sc.stark_shift
        freq729_sc_sptt1 = SPcenter_729 + sc.sideband_tone_1
        freq729_sc_sptt2 = SPcenter_729 + sc.sideband_tone_2

        freq729_op = self.calc_freq_from_array(self.parameters.OpticalPumping.line_selection)
        sbc_op_duration = sc.sideband_cooling_optical_pumping_duration

        # only do continuous sideband cooling
        duration = scc.sideband_cooling_continuous_duration
        duration_854 = duration + opc.optical_pumping_continuous_repump_additional
        duration_866 = duration + 2 * opc.optical_pumping_continuous_repump_additional

        for i in range(Nc):
            self.addDDS(DPchannel_729, self.end, duration, freq729_sc_dp, amps729_sc_DP)
            self.addTTL('729bichro', self.end, duration)
            self.addDDS('729DP2_SPTT1', self.end, duration, freq729_sc_sptt1, amps729_sc_SPTT1)
            self.addDDS('729DP2_SPTT2', self.end, duration, freq729_sc_sptt2, amps729_sc_SPTT2)
            self.addDDS(channel_854, self.end, duration_854, freq854, amp854)
            self.addDDS(channel_866, self.end, duration_866, freq866, amp866)
            self.end = self.end + duration_866
            self.addSequence(OpticalPumping,{'OpticalPumping.optical_pumping_frequency_729':freq729_op,
                                                        'OpticalPumpingContinuous.optical_pumping_continuous_duration':sbc_op_duration})
            
            duration += sc.sideband_cooling_duration_729_increment_per_cycle
            duration_854 = duration + opc.optical_pumping_continuous_repump_additional
            duration_866 = duration + 2 * opc.optical_pumping_continuous_repump_additional