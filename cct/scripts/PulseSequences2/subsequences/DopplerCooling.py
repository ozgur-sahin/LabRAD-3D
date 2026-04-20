from common.devel.bum.sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit

class DopplerCooling(pulse_sequence):
   
    #def addDDS(self, channel, start, duration, frequency, amplitude, phase = WithUnit(0, 'deg'), profile = 0):
    def sequence(self):
        p = self.parameters.DopplerCooling
        gas = self.parameters.GlobalAOMSelection
        opc = self.parameters.OpticalPumpingContinuous
        es = self.parameters.EmptySequence
  
        #print "Doppler Cooling" , p.doppler_cooling_duration
        
        repump_duration = p.doppler_cooling_duration + p.doppler_cooling_repump_additional
        # repump_duration_extra = p.doppler_cooling_duration_extra + p.doppler_cooling_repump_additional
        if self.parameters.DopplerCooling.doppler_cooling_parametric_pulse == True:
            self.addTTL('866_diff', self.start, WithUnit(2, 'us')) # 2 us for safe TTL switch on

        channel_397 = '397DP'
        channel_866 = '866DP'

        self.addDDS (channel_397, self.start, p.doppler_cooling_duration, p.doppler_cooling_frequency_397, p.doppler_cooling_amplitude_397)
        self.addDDS (channel_866, self.start, repump_duration, p.doppler_cooling_frequency_866, p.doppler_cooling_amplitude_866)


        # if p.doppler_cooling_two_traps:
        #     if p.doppler_cooling_continuous == "none":
        #         self.addDDS ('397DP', self.start, p.doppler_cooling_duration, p.doppler_cooling_frequency_397, p.doppler_cooling_amplitude_397)
        #         self.addDDS ('866DP', self.start, repump_duration, p.doppler_cooling_frequency_866, p.doppler_cooling_amplitude_866)
        #         self.addDDS ('397extra', self.start, p.doppler_cooling_duration_extra, p.doppler_cooling_frequency_397extra, p.doppler_cooling_amplitude_397extra)
        #         self.addDDS ('866extra', self.start, repump_duration_extra, p.doppler_cooling_frequency_866extra, p.doppler_cooling_amplitude_866extra)
        #     elif p.doppler_cooling_continuous == "DP":
        #         self.addDDS ('397DP', self.start, p.doppler_cooling_duration + opc.optical_pumping_continuous_duration + opc.optical_pumping_continuous_repump_additional + es.empty_sequence_duration, p.doppler_cooling_frequency_397, p.doppler_cooling_amplitude_397)
        #         self.addDDS ('866DP', self.start, repump_duration + opc.optical_pumping_continuous_duration + opc.optical_pumping_continuous_repump_additional + es.empty_sequence_duration, p.doppler_cooling_frequency_866, p.doppler_cooling_amplitude_866)
        #         self.addDDS ('397extra', self.start, p.doppler_cooling_duration_extra, p.doppler_cooling_frequency_397extra, p.doppler_cooling_amplitude_397extra)
        #         self.addDDS ('866extra', self.start, repump_duration_extra, p.doppler_cooling_frequency_866extra, p.doppler_cooling_amplitude_866extra)
        #     elif p.doppler_cooling_continuous == "extra":
        #         self.addDDS ('397DP', self.start, p.doppler_cooling_duration, p.doppler_cooling_frequency_397, p.doppler_cooling_amplitude_397)
        #         self.addDDS ('866DP', self.start, repump_duration, p.doppler_cooling_frequency_866, p.doppler_cooling_amplitude_866)
        #         self.addDDS ('397extra', self.start, p.doppler_cooling_duration_extra + opc.optical_pumping_continuous_duration + opc.optical_pumping_continuous_repump_additional + es.empty_sequence_duration, p.doppler_cooling_frequency_397extra, p.doppler_cooling_amplitude_397extra)
        #         self.addDDS ('866extra', self.start, repump_duration_extra + opc.optical_pumping_continuous_duration + opc.optical_pumping_continuous_repump_additional + es.empty_sequence_duration, p.doppler_cooling_frequency_866extra, p.doppler_cooling_amplitude_866extra)
        # else:
        #     if gas.global_aom_selection_toggle:
        #         channel_397 = '397' + gas.global_aom_selection_channel
        #         channel_866 = '866' + gas.global_aom_selection_channel
        #     else:
        #         channel_397 = p.channel_397
        #         channel_866 = p.channel_866
        #     if channel_397 == '397DP' and channel_866 == '866DP':
        #         self.addDDS (channel_397, self.start, p.doppler_cooling_duration, p.doppler_cooling_frequency_397, p.doppler_cooling_amplitude_397)
        #         self.addDDS (channel_866, self.start, repump_duration, p.doppler_cooling_frequency_866, p.doppler_cooling_amplitude_866)
        #     elif channel_397 == '397extra' and channel_866 == '866extra':
        #         self.addDDS (channel_397, self.start, p.doppler_cooling_duration_extra, p.doppler_cooling_frequency_397extra, p.doppler_cooling_amplitude_397extra)
        #         self.addDDS (channel_866, self.start, repump_duration_extra, p.doppler_cooling_frequency_866extra, p.doppler_cooling_amplitude_866extra)
        # changing the 866 from a dds to a rf source enabled by a switch
        # self.addTTL('866DP', self.start + WithUnit(0.2, 'us'), repump_duration- WithUnit(0.1, 'us') )


        self.end = self.start + repump_duration