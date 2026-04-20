from common.devel.bum.sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit
#from treedict import TreeDict

class StateReadout(pulse_sequence):
    '''
    Pulse sequence for reading out the state of the ion. 
    '''
    
    
    def sequence(self):
        st = self.parameters.StateReadout
        # gas = self.parameters.GlobalAOMSelection
        readout_mode = st.readout_mode
        repump_additional = self.parameters.DopplerCooling.doppler_cooling_repump_additional# need the doppler paramters for the additional repumper time 
        # st.use_camera_for_readout = False
        readout_duration=st.state_readout_duration

        channel_397 = '397DP'
        channel_866 = '866DP'

        duration_397=readout_duration
        duration_866=readout_duration + repump_additional

        self.addTTL('ReadoutCount', self.start, readout_duration)

        self.addDDS (channel_397,self.start, duration_397, st.state_readout_frequency_397, st.state_readout_amplitude_397)
        self.addDDS (channel_866,self.start, duration_866, st.state_readout_frequency_866, st.state_readout_amplitude_866)


        # if gas.global_aom_selection_toggle:
        #     channel_397 = '397' + gas.global_aom_selection_channel
        #     channel_866 = '866' + gas.global_aom_selection_channel
        # else:
        #     channel_397 = st.channel_397
        #     channel_866 = st.channel_866
        # duration_397=readout_duration
        # duration_866=readout_duration + repump_additional
        
        
        # self.addTTL('ReadoutCount', self.start, readout_duration)
        # if channel_397 == '397DP' and channel_866 == '866DP':
        #     self.addDDS (channel_397,self.start, duration_397, st.state_readout_frequency_397, st.state_readout_amplitude_397)
        #     self.addDDS (channel_866,self.start, duration_866, st.state_readout_frequency_866, st.state_readout_amplitude_866)
        # elif channel_397 == '397extra' and channel_866 == '866extra':
        #     self.addDDS (channel_397,self.start, duration_397, st.state_readout_frequency_397extra, st.state_readout_amplitude_397extra)
        #     self.addDDS (channel_866,self.start, duration_866, st.state_readout_frequency_866extra, st.state_readout_amplitude_866extra)
        
        # changing the 866 from a dds to a rf source enabled by a switch
        #self.addTTL('866DP', self.start+ WithUnit(0.25, 'us'), duration_866 - WithUnit(0.1, 'us') )

        self.end = self.start + duration_866        
