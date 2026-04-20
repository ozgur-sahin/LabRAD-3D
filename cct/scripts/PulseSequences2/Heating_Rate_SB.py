import numpy as np
from common.devel.bum.sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U
from treedict import TreeDict
from Excitation729 import Excitation729

class rsb(Excitation729):

    scannable_params = {'Excitation_729.rabi_excitation_frequency': [(-30., 30., 2., 'kHz'), 'temp_rsb',True]}

    @classmethod
    def run_finally(cls, cxn, parameter_dict, data, data_x):
        data = data.sum(1)
        # peak_guess =  cls.peak_guess(data_x, data)[0]
        # print "@@@@@@@@@@@@@@", peak_guess
        print data_x
        print data
        fit_params = cls.gaussian_fit(data_x, data, return_all_params = True)
        print "red sideband"
        print "############## fit params: ", fit_params
        print "Amplitude: ", fit_params[1]
        return fit_params[1]

class bsb(Excitation729):

    scannable_params = {'Excitation_729.rabi_excitation_frequency': [(-30., 30., 2., 'kHz'), 'temp_bsb',True]}

    @classmethod
    def run_finally(cls, cxn, parameter_dict, data, data_x):
        data = data.sum(1)
        # peak_guess =  cls.peak_guess(data_x, data)[0]
        # print "@@@@@@@@@@@@@@", peak_guess
        print data_x
        print data
        fit_params = cls.gaussian_fit(data_x, data, return_all_params = True)
        print "blue sideband"
        print "############## fit params: ", fit_params
        print "Amplitude: ", fit_params[1]
        return fit_params[1]

class Temperature(pulse_sequence):
    
    sequence = [(rsb, {'Excitation_729.invert_sb': -1.0}), 
                (bsb, {'Excitation_729.invert_sb': 1.0})]

    @classmethod
    def run_finally(cls, cxn, parameter_dict, amp, seq_name):
        try:
            R = 1.0 * amp[0] / amp[1]
            return 1.0*R/(1.0-1.0*R)
        except:
            pass
        parameters_dict.Display.relative_frequencies = False

class Heating_Rate_SB(pulse_sequence):

    scannable_params = {'EmptySequence.empty_sequence_duration': [(0., 5., .5, 'ms'), 'heating_rate']}
    @classmethod
    def run_initial(cls, cxn, parameters_dict):
        parameters_dict.Display.relative_frequencies = True
        cxn.normalpmtflow.set_mode("Normal")

    sequence = Temperature

# -------------------------------------------------------------------------------
# Heating Rate Rabi
# -------------------------------------------------------------------------------

# class flop(Excitation729):

#     scannable_params = {
#         'Excitation_729.rabi_excitation_duration':  [(0., 60., 2., 'us'), 'rabi'],
#                         }


#     @classmethod
#     def run_finally(cls, cxn, parameter_dict, data, data_x):
#         data = data.sum(1) ##'1' takes data from first ion. Only needs to be altered if working with multiple ions
#         ex=data
#         t=data_x

#         trap_freq = parameter_dict.TrapFrequencies.axial_frequency['Hz']  
#         heat_time = parameter_dict.Heating.background_heating_time 

#         fitter = rate_from_flops_fitter()

#         if heat_time == 0:
#             global time_2pi
#             time_2pi = fitter.calc_2pitime(t,ex)

#         excitation_scaling = 0.99
#         nbar,nbarerr,time_2pi,excitation_scaling = fitter.fit_single_flop(heat_time,t,ex,trap_freq,time_2pi,excitation_scaling)
#         print "time, pitime:"
#         print heat_time, time_2pi 
#         if math.isnan(nbarerr):
#             nbar=0
#             nbarerr=0

#         return nbar,nbarerr



# class Heating_Rate_Rabi(pulse_sequence):

#     scannable_params = {'Heating.background_heating_time': [(0., 5., 1, 'ms'), 'heatingrate']}

#     sequence = flop