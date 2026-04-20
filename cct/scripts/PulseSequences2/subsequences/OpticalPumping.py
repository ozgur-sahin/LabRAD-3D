from common.devel.bum.sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit

class OpticalPumping(pulse_sequence):
    
    '''
    Optical pumping unig a frequency selective transition  
    '''


    def sequence(self):


        op = self.parameters.OpticalPumping
        opc = self.parameters.OpticalPumpingContinuous
        opp = self.parameters.OpticalPumpingPulsed 
        ops = self.parameters.OpticalPumping397Sigma
        sp = self.parameters.StatePreparation
        gas = self.parameters.GlobalAOMSelection
        # choose the carrier frequency
        #freq_729=self.calc_freq_from_array(op.line_selection)
        freq_729 = op.optical_pumping_frequency_729
        channel_854 = '854DP'
        channel_866 = '866DP'

        if op.optical_pumping_type == 'continuous':
            continuous = True
        elif op.optical_pumping_type == 'pulsed':
            continuous = False
        else:
            raise Exception ('Incorrect optical pumping type {0}'.format(op.optical_pumping_type))
        if op.optical_pumping_type == 'continuous':
            duration_854 = opc.optical_pumping_continuous_duration + opc.optical_pumping_continuous_repump_additional
            duration_866 = opc.optical_pumping_continuous_duration + 2 * opc.optical_pumping_continuous_repump_additional

            freq866 = op.optical_pumping_frequency_866
            ampl866 = op.optical_pumping_amplitude_866
            freq854 = op.optical_pumping_frequency_854
            ampl854 = op.optical_pumping_amplitude_854

            self.end = self.start + duration_866
            
            self.addDDS(sp.channel_729, self.start, opc.optical_pumping_continuous_duration, freq_729, op.optical_pumping_amplitude_729)
            if sp.channel_729 == '729DP2':
                SPcenter_729 = WithUnit(80.0, 'MHz')
                SPamp_729_max = WithUnit(-10.0, 'dBm')
                self.addDDS('729DP2_SPST', self.start, opc.optical_pumping_continuous_duration, SPcenter_729, SPamp_729_max)
            #self.addTTL('854TTL',self.start, duration_854)
            self.addDDS(channel_854, self.start, duration_854, freq854, ampl854)
            self.addDDS(channel_866, self.start, duration_866, freq866, ampl866)

        elif op.optical_pumping_type == 'pulsed':
            cycles = int(opp.optical_pumping_pulsed_cycles)
            cycle_duration = opp.optical_pumping_pulsed_duration_729 + opp.optical_pumping_pulsed_duration_repumps + opp.optical_pumping_pulsed_duration_additional_866 + 2 * opp.optical_pumping_pulsed_duration_between_pulses
            cycles_start = [self.start + cycle_duration * i for i in range(cycles)]
            self.end = self.start + cycles * cycle_duration
            ampl729 = op.optical_pumping_amplitude_729

            freq866 = op.optical_pumping_frequency_866
            ampl866 = op.optical_pumping_amplitude_866
            freq854 = op.optical_pumping_frequency_854
            ampl854 = op.optical_pumping_amplitude_854

            for start in cycles_start:
                start_repumps = start + opp.optical_pumping_pulsed_duration_729 + opp.optical_pumping_pulsed_duration_between_pulses
                duration_866 =  opp.optical_pumping_pulsed_duration_repumps + opp.optical_pumping_pulsed_duration_additional_866
                self.addDDS(sp.channel_729, start, opp.optical_pumping_pulsed_duration_729 , freq_729 , ampl729)
                if sp.channel_729 == '729DP2':
                    SPcenter_729 = WithUnit(80.0, 'MHz')
                    SPamp_729_max = WithUnit(-10.0, 'dBm')
                    self.addDDS('729DP2_SPST', start, opp.optical_pumping_pulsed_duration_729, SPcenter_729, SPamp_729_max)
                #self.addTTL('854TTL',start_repumps, opp.optical_pumping_pulsed_duration_repumps)
                self.addDDS(channel_854, start_repumps, opp.optical_pumping_pulsed_duration_repumps, freq854, ampl854)
                self.addDDS(channel_866, start_repumps, duration_866, freq866 , ampl866)

        else:
            raise Exception ('Incorrect optical pumping type {}'.format(op.optical_pumping_type))  

        # if gas.global_aom_selection_toggle:
        #     channel_854 = '854' + gas.global_aom_selection_channel
        #     channel_866 = '866' + gas.global_aom_selection_channel
        # else:
        #     channel_854 = op.channel_854
        #     channel_866 = op.channel_866
        # print "Optical pumping 729 freq:.{}".format(freq_729)        
        # print "Optical pumping line selection:.{}".format(op.line_selection)
        # print freq_729
        # if op.optical_pumping_type == 'continuous':
        #     continuous = True
        # elif op.optical_pumping_type == 'pulsed':
        #     continuous = False
        # else:
        #     raise Exception ('Incorrect optical pumping type {0}'.format(op.optical_pumping_type))
        # if op.optical_pumping_type == 'continuous':
        #     duration_854 = opc.optical_pumping_continuous_duration + opc.optical_pumping_continuous_repump_additional
        #     duration_866 = opc.optical_pumping_continuous_duration + 2 * opc.optical_pumping_continuous_repump_additional
        #     # channel_854 = op.channel_854
        #     # channel_866 = op.channel_866
        #     if channel_866 == '866DP':
        #         freq866 = op.optical_pumping_frequency_866
        #         ampl866 = op.optical_pumping_amplitude_866
        #         freq854 = op.optical_pumping_frequency_854
        #         ampl854 = op.optical_pumping_amplitude_854
        #     if channel_866 == '866extra':
        #         freq866 = op.optical_pumping_frequency_866extra
        #         ampl866 = op.optical_pumping_amplitude_866extra
        #         freq854 = op.optical_pumping_frequency_854extra
        #         ampl854 = op.optical_pumping_amplitude_854extra
        #     self.end = self.start + duration_866
            
        #     self.addDDS(sp.channel_729, self.start, opc.optical_pumping_continuous_duration, freq_729, op.optical_pumping_amplitude_729)
        #     #self.addTTL('854TTL',self.start, duration_854)
        #     self.addDDS(channel_854, self.start, duration_854, freq854, ampl854)
        #     self.addDDS(channel_866, self.start, duration_866, freq866, ampl866)
        # elif op.optical_pumping_type == 'pulsed':
        #     cycles = int(opp.optical_pumping_pulsed_cycles)
        #     cycle_duration = opp.optical_pumping_pulsed_duration_729 + opp.optical_pumping_pulsed_duration_repumps + opp.optical_pumping_pulsed_duration_additional_866 + 2 * opp.optical_pumping_pulsed_duration_between_pulses
        #     cycles_start = [self.start + cycle_duration * i for i in range(cycles)]
        #     self.end = self.start + cycles * cycle_duration
        #     ampl729 = op.optical_pumping_amplitude_729
        #     # channel_854 = op.channel_854
        #     # channel_866 = op.channel_866
        #     if channel_866 == '866DP':
        #         freq866 = op.optical_pumping_frequency_866
        #         ampl866 = op.optical_pumping_amplitude_866
        #         freq854 = op.optical_pumping_frequency_854
        #         ampl854 = op.optical_pumping_amplitude_854
        #     if channel_866 == '866extra':                                      
        #         freq866 = op.optical_pumping_frequency_866extra
        #         ampl866 = op.optical_pumping_amplitude_866extra
        #         freq854 = op.optical_pumping_frequency_854extra
        #         ampl854 = op.optical_pumping_amplitude_854extra
        #     for start in cycles_start:
        #         start_repumps = start + opp.optical_pumping_pulsed_duration_729 + opp.optical_pumping_pulsed_duration_between_pulses
        #         duration_866 =  opp.optical_pumping_pulsed_duration_repumps + opp.optical_pumping_pulsed_duration_additional_866
        #         self.addDDS(sp.channel_729, start, opp.optical_pumping_pulsed_duration_729 , freq_729 , ampl729)
        #         #self.addTTL('854TTL',start_repumps, opp.optical_pumping_pulsed_duration_repumps)
        #         self.addDDS(channel_854, start_repumps, opp.optical_pumping_pulsed_duration_repumps, freq854, ampl854)
        #         self.addDDS(channel_866, start_repumps, duration_866, freq866 , ampl866)
        # # elif op.optical_pumping_type == '397sigma':
        # #     duration_866 = ops.optical_pumping_397sigma_duration + ops.optical_pumping_397sigma_additional
        # #     freq397 = ops.optical_pumping_397sigma_frequency_397
        # #     amp397 = ops.optical_pumping_397sigma_amplitude_397
        # #     freq866 = ops.optical_pumping_397sigma_frequency_866
        # #     amp866 = ops.optical_pumping_397sigma_amplitude_866
        # #     self.end = self.start + duration_866
        # #     self.addDDS(ops.channel_397_sigma, self.start, ops.optical_pumping_397sigma_duration, freq397, amp397)
        # #     self.addDDS('866', self.start, duration_866, freq866, amp866)
        # else:
        #     raise Exception ('Incorrect optical pumping type {}'.format(op.optical_pumping_type))  
