from common.abstractdevices.script_scanner.scan_methods import experiment
from cct.scripts.experiments.CalibrationScans.calibrate_heating_rates import calibrate_heating_rates
from cct.scripts.scriptLibrary import scan_methods
from cct.scripts.scriptLibrary import dvParameters
# from fitters import peak_fitter
from fitters import linear_fit
from labrad.units import WithUnit
from treedict import TreeDict
import time
import numpy as np
import labrad

class calibrate_heating_rates_fit(experiment):

    name = 'CalibHeatingRatesFit'

    required_parameters = [('DriftTracker', 'line_selection_1'),
                           ('DriftTracker', 'line_selection_2'),
                           ('CalibrationScans', 'do_rabi_flop_carrier'),
                           ('CalibrationScans', 'do_rabi_flop_radial1'),
                           ('CalibrationScans', 'do_rabi_flop_radial2'),
                           ('CalibrationScans', 'carrier_time_scan'),
                           ('CalibrationScans', 'radial1_time_scan'),
                           ('CalibrationScans', 'radial2_time_scan'),
                           ('CalibrationScans', 'carrier_excitation_power'),
                           ('CalibrationScans', 'radial1_excitation_power'),
                           ('CalibrationScans', 'radial2_excitation_power'),
                           ('CalibrationScans', 'heating_rate_scan_interval')
                           ]

    # # parameters to overwrite
    remove_parameters = [
        # ('Heating', 'background_heating_time')
        ]

    @classmethod
    def all_required_parameters(cls):
        parameters = set(cls.required_parameters)
        parameters = parameters.union(set(calibrate_heating_rates.all_required_parameters()))
        parameters = list(parameters)
        for p in cls.remove_parameters:
            parameters.remove(p)
        return parameters
    
    
    def initialize(self, cxn, context, ident):

        self.ident = ident
        self.drift_tracker = cxn.sd_tracker
        self.calibrate_heating = self.make_experiment(calibrate_heating_rates)
        
        self.calibrate_heating.initialize(cxn, context, ident)
        self.fitter = linear_fit()

        self.save_context = cxn.context()
        self.dv = cxn.data_vault
        self.pv = cxn.parametervault
        #self.dds_cw = cxn.dds_cw
        self.cxnlab = labrad.connect('192.168.169.49', password='lab', tls_mode='off') #connection to labwide network
        
    def run(self, cxn, context):

        dv_args = {'output_size': 1,
                    'experiment_name' : self.name,
                    'window_name': 'fit_result',
                    'dataset_name' : 'Heating_Rate'
                    }

        scan_methods.setup_data_vault(cxn, self.save_context, dv_args)

        # scan_param = self.parameters.CalibrationScans.heating_rate_scan_interval

        (heat_time_list, nbar_list, nbarerror_list) = self.calibrate_heating.run(cxn, context)

        # heat_time_list = np.array(heat_time_list)
        # nbar_list = np.array(nbar_list)
        # nbarerror_list = np.array(nbarerror_list)
        # nbar_list = nbar_list.flatten()
        # nbarerror_list = nbarerror_list.flatten()

        print nbar_list
        print nbarerror_list
        heat_time_list=heat_time_list/1000.
        print heat_time_list

        (rate, rate_error, nbar_0, nbar_0_error) = self.fitter.fit(heat_time_list, nbar_list, nbarerror_list)
        print nbar_0
        print nbar_0_error
        print rate
        print rate_error

        # submission = [testing]
        submission = [rate]
        submission.extend([rate_error])

        self.dv.add(submission, context = self.save_context)
        # numpy.polyfit(heat_time_list, nbar_list, 1, rcond=None, full=False, w=1/nbarerror_list**2, cov=True)
   
    def finalize(self, cxn, context):
        self.calibrate_heating.finalize(cxn, context)

if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = calibrate_heating_rates_fit(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
