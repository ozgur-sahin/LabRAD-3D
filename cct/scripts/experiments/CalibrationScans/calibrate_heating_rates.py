from common.abstractdevices.script_scanner.scan_methods import experiment
from cct.scripts.experiments.CalibrationScans.calibrate_temperature import calibrate_temperature
from cct.scripts.scriptLibrary import scan_methods
from cct.scripts.scriptLibrary import dvParameters
from fitters import peak_fitter
from fitters import linear_fit
from labrad.units import WithUnit
from treedict import TreeDict
import time
import numpy as np
import labrad

class calibrate_heating_rates(experiment):

    name = 'CalibHeatingRates'

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

    # parameters to overwrite
    remove_parameters = [
        ('Heating', 'background_heating_time')
        ]

    @classmethod
    def all_required_parameters(cls):
        parameters = set(cls.required_parameters)
        parameters = parameters.union(set(calibrate_temperature.all_required_parameters()))
        parameters = list(parameters)
        for p in cls.remove_parameters:
            parameters.remove(p)
        return parameters
    
    
    def initialize(self, cxn, context, ident):

        self.ident = ident
        self.drift_tracker = cxn.sd_tracker
        self.calibrate_temp = self.make_experiment(calibrate_temperature)
        
        self.calibrate_temp.initialize(cxn, context, ident)

        self.save_context = cxn.context()
        self.dv = cxn.data_vault
        self.pv = cxn.parametervault
        #self.dds_cw = cxn.dds_cw
        self.cxnlab = labrad.connect('192.168.169.49', password='lab', tls_mode='off') #connection to labwide network
        
    def run(self, cxn, context):

        dv_args = {'output_size': 2,
                    'experiment_name' : self.name,
                    'window_name': 'heating_rate',
                    'dataset_name' : 'Heating_Rate'
                    }

        scan_methods.setup_data_vault(cxn, self.save_context, dv_args)

        scan_param = self.parameters.CalibrationScans.heating_rate_scan_interval

        self.scan = scan_methods.simple_scan(scan_param, 'us')

        nbar_list=[]
        nbarerror_list=[]
        heat_time_list=[]

        for i,heat_time in enumerate(self.scan):
            #should_stop = self.pause_or_stop()
            #if should_stop: break
       
            replace = TreeDict.fromdict({
                                    'Heating.background_heating_time':heat_time,
                                    'Documentation.sequence':'calibrate_heating_rates',
                                       })
            
            self.calibrate_temp.set_parameters(replace)
            #self.calibrate_temp.set_progress_limits(0, 33.0)
   
            (rsb_ex, rsb_ex_err, bsb_ex, bsb_ex_err) = self.calibrate_temp.run(cxn, context)
            # print rsb_ex_err
            # print bsb_ex_err

            fac = rsb_ex/bsb_ex
            nbar = fac/(1.0-fac)
            nbarerror=np.sqrt((bsb_ex/(bsb_ex-rsb_ex)**2)**2*rsb_ex_err**2+(-rsb_ex/(bsb_ex-rsb_ex)**2)**2*bsb_ex_err**2)
            # print nbarerror


            submission = [heat_time['us']]
            submission.extend([nbar])
            submission.extend([nbarerror])
            nbar_list=np.append(nbar_list,nbar)
            nbarerror_list=np.append(nbarerror_list,nbarerror)
            heat_time_list=np.append(heat_time_list,heat_time['us'])
            print heat_time_list, nbar_list, nbarerror_list
            self.dv.add(submission, context = self.save_context)

        return (heat_time_list, nbar_list, nbarerror_list)
        # (nbar_0, nbar_0_error, rate, rate_error) = fitters.linear_fit.fit(heat_time_list, nbar_list, nbarerror_list)
        # numpy.polyfit(heat_time_list, nbar_list, 1, rcond=None, full=False, w=1/nbarerror_list**2, cov=True)
   
    def finalize(self, cxn, context):
        self.calibrate_temp.finalize(cxn, context)

if __name__ == '__main__':
    cxn = labrad.connect()
    scanner = cxn.scriptscanner
    exprt = calibrate_heating_rates(cxn = cxn)
    ident = scanner.register_external_launch(exprt.name)
    exprt.execute(ident)
