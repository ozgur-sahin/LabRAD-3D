from common.devel.bum.sequences.pulse_sequence import pulse_sequence
from labrad.units import WithUnit as U
from treedict import TreeDict
import numpy as np

class Excitation729(pulse_sequence):
    scannable_params = {
        'DopplerCooling.doppler_cooling_frequency_397':  [(180., 210., .5, 'MHz'), 'doppler_freq'],
        'DopplerCooling.doppler_cooling_amplitude_397':  [(-30., -15., .5, 'dBm'), 'doppler_amp'],
        'DopplerCooling.doppler_cooling_frequency_866':  [(60., 90., .5, 'MHz'), 'doppler_freq'],
        'DopplerCooling.doppler_cooling_amplitude_866':  [(-20., -6., .5, 'dBm'), 'doppler_amp'],
        'SidebandCooling.sideband_cooling_amplitude_854': [(-30.,-10., 1., 'dBm'), 'sideband_854'],
        'SidebandCooling.stark_shift': [(-10., 10., 0.2, 'kHz'), 'sideband_stark_shift'],
        'Excitation_729.rabi_excitation_duration':  [(0., 200., 10., 'us'), 'rabi'],
        'Excitation_729.rabi_excitation_frequency': [(-50., 50., 5., 'kHz'), 'spectrum',True],
        # 'SidebandCooling.stark_shift': [(-20., 20., 2., 'kHz'), 'other'],
        # 'EmptySequence.empty_sequence_duration_readout': [(0.,1000.,100.,'us'),'rabi']
              }

    show_params= [
                  'Excitation_729.line_selection',
                  'Excitation_729.rabi_excitation_amplitude',
                  'Excitation_729.rabi_excitation_duration',
                  'Excitation_729.sideband_selection',
                  'Excitation_729.channel729',
                  'Excitation_729.frequency_selection',
                  'Excitation_729.stark_shift_729',
                  'EmptySequence.empty_sequence_duration',
                  # 'EmptySequence.empty_sequence_duration_readout'
                  ]


    def sequence(self):

      from subsequences.StatePreparation import StatePreparation
      from subsequences.EmptySequence import EmptySequence
      from subsequences.RabiExcitation import RabiExcitation
      from subsequences.StateReadout import StateReadout

      e = self.parameters.Excitation_729
      es = self.parameters.EmptySequence

        
      ## calculate the scan params
      if e.frequency_selection == "auto":
        print(e.line_selection)
        freq_729_pos = self.calc_freq_from_array(e.line_selection, [sb*e.invert_sb for sb in e.sideband_selection])
        freq_729 = freq_729_pos + e.stark_shift_729 + e.rabi_excitation_frequency
        print "FREQUENCY 729 = {}".format(freq_729)
      elif e.frequency_selection == "manual":
        freq_729 = e.rabi_excitation_frequency
      else:
        raise Exception ('Incorrect frequency selection type {0}'.format(e.frequency_selection))

      ## build the sequence
      self.addSequence(StatePreparation)
      self.addSequence(EmptySequence)
      self.addSequence(RabiExcitation,{  'Excitation_729.rabi_excitation_frequency': freq_729})
                                         # 'Excitation_729.rabi_change_DDS': True})
      # self.addSequence(EmptySequence,{'EmptySequence.empty_sequence_duration':es.empty_sequence_duration_readout})
      self.addSequence(StateReadout)  
        
    @classmethod
    def run_initial(cls, cxn, parameters_dict):
      cxn.normalpmtflow.set_mode("Normal")
      e = parameters_dict.Excitation_729
      ###### add shift for spectra purposes
      carrier_translation = {'S+1/2D-3/2':'c0',
                            'S-1/2D-5/2':'c1',
                            'S+1/2D-1/2':'c2',
                            'S-1/2D-3/2':'c3',
                            'S+1/2D+1/2':'c4',
                            'S-1/2D-1/2':'c5',
                            'S+1/2D+3/2':'c6',
                            'S-1/2D+1/2':'c7',
                            'S+1/2D+5/2':'c8',
                            'S-1/2D+3/2':'c9',
                               }

      trapfreq = parameters_dict.TrapFrequencies
      sideband_frequencies = [trapfreq.radial_frequency_1, trapfreq.radial_frequency_2, trapfreq.axial_frequency, trapfreq.rf_drive_frequency]
      shift = U(0.,'MHz')
      if parameters_dict.Display.relative_frequencies:
        # shift by sideband only (spectrum "0" will be carrier frequency)
        for order,sideband_frequency in zip([sb*e.invert_sb for sb in e.sideband_selection], sideband_frequencies):
            shift += order * sideband_frequency
      else:
        #shift by sideband + carrier (spectrum "0" will be AO center frequency)
        shift += parameters_dict.Carriers[carrier_translation[e.line_selection]]
        for order,sideband_frequency in zip([sb*e.invert_sb for sb in e.sideband_selection], sideband_frequencies):
            shift += order * sideband_frequency

      pv = cxn.parametervault
      pv.set_parameter('Display','shift', shift)

    @classmethod
    def run_in_loop(cls, cxn, parameters_dict, data, x):
      pass

    @classmethod
    def run_finally(cls, cxn, parameters_dict, data, x):
      pass
        
