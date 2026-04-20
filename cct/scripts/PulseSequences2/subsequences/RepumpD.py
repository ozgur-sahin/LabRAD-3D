from common.devel.bum.sequences.pulse_sequence import pulse_sequence

class RepumpD(pulse_sequence):
   
  
    def sequence(self):
        p = self.parameters.RepumpD_5_2
        st = self.parameters.StateReadout
        channel_854 = '854DP'
        channel_866 = '866DP'
        self.end = self.start + p.repump_d_duration
        self.addDDS(channel_854, self.start, p.repump_d_duration, p.repump_d_frequency_854, p.repump_d_amplitude_854)
        self.addDDS(channel_866, self.start, p.repump_d_duration, st.state_readout_frequency_866, st.state_readout_amplitude_866)



        # gas = self.parameters.GlobalAOMSelection
        # if gas.global_aom_selection_toggle:
        #     channel_854 = '854' + gas.global_aom_selection_channel
        #     channel_866 = '866' + gas.global_aom_selection_channel
        # else:
        #     channel_854 = p.channel_854
        #     channel_866 = p.channel_866
        # self.end = self.start + p.repump_d_duration
        # #self.addTTL('854TTL',self.start, p.repump_d_duration)
        # self.addDDS(channel_854, self.start, p.repump_d_duration, p.repump_d_frequency_854, p.repump_d_amplitude_854)
        # if channel_866 == '866DP':
        #     self.addDDS(channel_866, self.start, p.repump_d_duration, st.state_readout_frequency_866, st.state_readout_amplitude_866)
        # if channel_866 == '866extra':
        #     self.addDDS(channel_866, self.start, p.repump_d_duration, st.state_readout_frequency_866extra, st.state_readout_amplitude_866extra)