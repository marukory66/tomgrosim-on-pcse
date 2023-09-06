from pcse.engine import Engine
from pcse.base import BaseEngine
import datetime
import gc
from pcse.traitlets import Instance, Bool, List, Dict
from pcse.base import (VariableKiosk, WeatherDataProvider,
                           AncillaryObject, SimulationObject,
                           BaseEngine, ParameterProvider)
from pcse.util import ConfigurationLoader, check_date
from pcse.timer import Timer
from pcse import signals
from pcse import exceptions as exc
from pcse import settings
import pandas as pd
import os

class my_Engine(BaseEngine):
    """Simulation engine for simulating the combined soil/crop system.

    :param parameterprovider: A `ParameterProvider` object providing model
        parameters as key/value pairs. The parameterprovider encapsulates
        the different parameter sets for crop, soil and site parameters.
    :param weatherdataprovider: An instance of a WeatherDataProvider that can
        return weather data in a  for a given date.
    :param agromanagement: AgroManagement data. The data format is described
        in the section on agronomic management.
    :param config: A string describing the model configuration file to use.
        By only giving a filename PCSE assumes it to be located in the 'conf/'
        folder in the main PCSE folder.
        If you want to provide you own configuration file, specify
        it as an absolute or a relative path (e.g. with a leading '.')

    `Engine` handles the actual simulation of the combined soil-
    crop system. The central part of the  `Engine` is the soil
    water balance which is continuously simulating during the entire run. In
    contrast, `CropSimulation` objects are only initialized after receiving a
    "CROP_START" signal from the AgroManagement unit. From that point onward,
    the combined soil-crop is simulated including the interactions between
    the soil and crop such as root growth and transpiration.

    Similarly, the crop simulation is finalized when receiving a "CROP_FINISH"
    signal. At that moment the `finalize()` section on the cropsimulation is
    executed. Moreover, the "CROP_FINISH" signal can specify that the
    crop simulation object should be deleted from the hierarchy. The latter is
    useful for further extensions of PCSE for running crop rotations.

    Finally, the entire simulation is terminated when a "TERMINATE" signal is
    received. At that point, the `finalize()` section on the water balance is
    executed and the simulation stops.

    **Signals handled by Engine:**

    `Engine` handles the following signals:
        * CROP_START: Starts an instance of `CropSimulation` for simulating crop
          growth. See the `_on_CROP_START` handler for details.
        * CROP_FINISH: Runs the `finalize()` section an instance of
          `CropSimulation` and optionally deletes the cropsimulation instance.
          See the `_on_CROP_FINISH` handler for details.
        * TERMINATE: Runs the `finalize()` section on the waterbalance module
          and terminates the entire simulation.
          See the `_on_TERMINATE` handler for details.
        * OUTPUT:  Preserves a copy of the value of selected state/rate
          variables during simulation for later use.
          See the `_on_OUTPUT` handler for details.
        * SUMMARY_OUTPUT:  Preserves a copy of the value of selected state/rate
          variables for later use. Summary output is usually requested only
          at the end of the crop simulation.
          See the `_on_SUMMARY_OUTPUT` handler for details.

    """
    # system configuration
    mconf = Instance(ConfigurationLoader)
    parameterprovider = Instance(ParameterProvider)

    #追加
    cropinitiallist = None
    modelkinds = None

    # sub components for simulation
    crop = Instance(SimulationObject)
    soil = Instance(SimulationObject)
    agromanager = Instance(AncillaryObject)
    weatherdataprovider = Instance(WeatherDataProvider)
    drv = None
    my_drv = None
    kiosk = Instance(VariableKiosk)
    timer = Instance(Timer)
    day = Instance(datetime.date)

    # flags that are being set by signals
    flag_terminate = Bool(False)
    flag_crop_finish = Bool(False)
    flag_crop_start = Bool(False)
    flag_crop_delete = Bool(False)
    flag_output = Bool(False)
    flag_summary_output = Bool(False)

    # placeholders for variables saved during model execution
    _saved_output = List()
    _saved_summary_output = List()
    _saved_terminal_output = Dict()
    DMC_saved_output = pd.DataFrame(columns=["DAY","params"])
    DOEF_saved_output = pd.DataFrame(columns=["DAY","params"])
    DOEL_saved_output = pd.DataFrame(columns=["DAY","params"])
    DOHF_saved_output = pd.DataFrame(columns=["DAY","params"])
    DOHL_saved_output = pd.DataFrame(columns=["DAY","params"])
    DVSF_saved_output = pd.DataFrame(columns=["DAY","params"])
    # DVSL_saved_output = pd.DataFrame(columns=["DAY","params"])
    FD_saved_output = pd.DataFrame(columns=["DAY","params"])
    FF_saved_output = pd.DataFrame(columns=["DAY","params"])
    LA_saved_output = pd.DataFrame(columns=["DAY","params"])
    LV_saved_output = pd.DataFrame(columns=["DAY","params"])
    SLA_saved_output = pd.DataFrame(columns=["DAY","params"])
    params_List = pd.DataFrame(columns=["DAY","WSO","DWSO","YWSO","TWSO","SDMC","TDM","GASST","MREST","ASA","AF","CAF","DMI","CVF","DMA","GASS","MRES","ASRC","WRO","TWRO","GRRO","TWST","WST","GRST","LAI","WLV","DWLV","SSLA","FR","FL","FS","FO","TPGR","TMPGR","TPGRLV","TMPGRLV","TPGRFR","TMPGRFR","TPGRST","TPGRRO","PF","DVS","DVR","RGR"])

    def __init__(self, parameterprovider, weatherdataprovider, agromanagement, weathertimeseries, cropinitiallist,modelkinds, config=None):

        BaseEngine.__init__(self)

        # Load the model configuration
        self.mconf = ConfigurationLoader(config)
        self.parameterprovider = parameterprovider
        self.cropinitiallist = cropinitiallist
        self.modelkinds = modelkinds
        # Variable kiosk for registering and publishing variables
        self.kiosk = VariableKiosk()

        # Placeholder for variables to be saved during a model run
        self._saved_output = list()
        self._saved_summary_output = list()
        self._saved_terminal_output = dict()

        self.DMC_saved_output = pd.DataFrame(columns=["DAY","params"])
        self.DOEF_saved_output = pd.DataFrame(columns=["DAY","params"])
        self.DOEL_saved_output = pd.DataFrame(columns=["DAY","params"])
        self.DOHF_saved_output = pd.DataFrame(columns=["DAY","params"])
        self.DOHL_saved_output = pd.DataFrame(columns=["DAY","params"])
        self.DVSF_saved_output = pd.DataFrame(columns=["DAY","params"])
        # self.DVSL_saved_output = pd.DataFrame(columns=["DAY","params"])
        self.FD_saved_output = pd.DataFrame(columns=["DAY","params"])
        self.FF_saved_output = pd.DataFrame(columns=["DAY","params"])
        self.LA_saved_output = pd.DataFrame(columns=["DAY","params"])
        self.LV_saved_output = pd.DataFrame(columns=["DAY","params"])
        self.SLA_saved_output = pd.DataFrame(columns=["DAY","params"])

        # register handlers for starting/finishing the crop simulation, for
        # handling output and terminating the system
        self._connect_signal(self._on_CROP_START, signal=signals.crop_start)
        self._connect_signal(self._on_CROP_FINISH, signal=signals.crop_finish)
        self._connect_signal(self._on_OUTPUT, signal=signals.output)
        self._connect_signal(self._on_TERMINATE, signal=signals.terminate)

        # Component for agromanagement
        self.agromanager = self.mconf.AGROMANAGEMENT(self.kiosk, agromanagement)
        start_date = self.agromanager.start_date
        end_date = self.agromanager.end_date

        # change_date = self.agromanager.change_date

        # Timer: starting day, final day and model output
        self.timer = Timer(self.kiosk, start_date, end_date, self.mconf)
        self.day, delt = self.timer()

        # Driving variables
        self.weatherdataprovider = weatherdataprovider
        self.drv = self._get_driving_variables(self.day)
        self.my_drv = weathertimeseries

        # Component for simulation of soil processes
        if self.mconf.SOIL is not None:
            self.soil = self.mconf.SOIL(self.day, self.kiosk, parameterprovider)

        # Call AgroManagement module for management actions at initialization
        self.agromanager(self.day, self.drv)

        # Calculate initial rates
        self.calc_rates(self.day, self.drv, self.my_drv,self.modelkinds)

        self.output_lists(self.day,self.kiosk)

    def output_lists(self,day,kiosk):

        self.DMC_saved_output = self.DMC_saved_output.append({"DAY":day,"params":kiosk.DMC}, ignore_index=True)
        self.DOEL_saved_output = self.DOEL_saved_output.append({"DAY":day,"params":kiosk.DOEL}, ignore_index=True)
        self.DOHF_saved_output = self.DOHF_saved_output.append({"DAY":day,"params":kiosk.DOHF}, ignore_index=True)
        self.DOHL_saved_output = self.DOHF_saved_output.append({"DAY":day,"params":kiosk.DOEL}, ignore_index=True)
        self.DVSF_saved_output = self.DVSF_saved_output.append({"DAY":day,"params":kiosk.DVSF}, ignore_index=True)
        self.FD_saved_output = self.FD_saved_output.append({"DAY":day,"params":kiosk.FD}, ignore_index=True)
        self.FF_saved_output = self.FF_saved_output.append({"DAY":day,"params":kiosk.FF}, ignore_index=True)
        self.LA_saved_output = self.LA_saved_output.append({"DAY":day,"params":kiosk.LA}, ignore_index=True)
        self.LV_saved_output = self.LV_saved_output.append({"DAY":day,"params":kiosk.LV}, ignore_index=True)
        self.SLA_saved_output = self.LV_saved_output.append({"DAY":day,"params":kiosk.SLA}, ignore_index=True)
        self.DOEF_saved_output = self.DOEF_saved_output.append({"DAY":day,"params":kiosk.DOEF}, ignore_index=True)
        self.params_List = self.params_List.append({"DAY":day,"WSO":kiosk.WSO,"DWSO":kiosk.DWSO,"YWSO":kiosk.YWSO,"TWSO":kiosk.TWSO,"SDMC":kiosk.SDMC,"TDM":kiosk.TDM,"GASST":kiosk.GASST,"MREST":kiosk.MREST,"ASA":kiosk.ASA,"AF":kiosk.AF,"CAF":kiosk.CAF,"DMI":kiosk.DMI,"CVF":kiosk.CVF,"DMA":kiosk.DMA,"GASS":kiosk.GASS,"MRES":kiosk.MRES,"ASRC":kiosk.ASRC,"WRO":kiosk.WRO,"TWRO":kiosk.TWRO,"GRRO":kiosk.GRRO,"TWST":kiosk.TWST,"WST":kiosk.WST,"GRST":kiosk.GRST,"LAI":kiosk.LAI,"WLV":kiosk.WLV,"DWLV":kiosk.DWLV,"SSLA":kiosk.SSLA,"FR":kiosk.FR,"FL":kiosk.FL,"FS":kiosk.FS,"FO":kiosk.FO,"TPGR":kiosk.TPGR,"TMPGR":kiosk.TMPGR,"TPGRLV":kiosk.TPGRLV,"TMPGRLV":kiosk.TMPGRLV,"TPGRFR":kiosk.TPGRFR,"TMPGRFR":kiosk.TMPGRFR,"TPGRST":kiosk.TPGRST,"TPGRRO":kiosk.TPGRRO,"PF":kiosk.PF,"DVS":kiosk.DVS,"DVR":kiosk.DVR,"RGR":kiosk.RGR}, ignore_index=True)

    def my_get_output(self,path):
        os.makedirs(path,exist_ok=True)
        self.DMC_saved_output.to_csv(path+"/"+"DMC.csv")
        self.DOEF_saved_output.to_csv(path+"/"+"DOEF.csv")
        self.DOEL_saved_output.to_csv(path+"/"+"DMEL.csv")
        self.DOHF_saved_output.to_csv(path+"/"+"DOHF.csv")
        self.DOHL_saved_output.to_csv(path+"/"+"DOHL.csv")
        self.DVSF_saved_output.to_csv(path+"/"+"DVSF.csv")
        self.FD_saved_output.to_csv(path+"/"+"FD.csv")
        self.FF_saved_output.to_csv(path+"/"+"FF.csv")
        self.LA_saved_output.to_csv(path+"/"+"LA.csv")
        self.LV_saved_output.to_csv(path+"/"+"LV.csv")
        self.SLA_saved_output.to_csv(path+"/"+"SLA.csv")
        self.params_List.to_csv(path+"/"+"params.csv")


        return self.FF_saved_output


    def calc_rates(self, day, drv, my_drv,modelkinds):

        # Start rate calculation on individual components
        if self.crop is not None:
            self.crop.calc_rates(day, drv,my_drv,modelkinds)

        if self.soil is not None:
            self.soil.calc_rates(day, drv)

        # Save state variables of the model
        if self.flag_output:
            self._save_output(day)

        # Check if flag is present to finish crop simulation
        if self.flag_crop_finish:
            self._finish_cropsimulation(day)



    def integrate(self, day, delt):

        # Flush state variables from the kiosk before state updates
        self.kiosk.flush_states()

        if self.crop is not None:
            self.crop.integrate(day, delt)

        if self.soil is not None:
            self.soil.integrate(day, delt)

        # Set all rate variables to zero
        if settings.ZEROFY:
            self.zerofy()

        # Flush rate variables from the kiosk after state updates
        self.kiosk.flush_rates()

    def _run(self):
        """Make one time step of the simulation.
        """

        # Update timer
        self.day, delt = self.timer()

        # State integration
        self.integrate(self.day, delt)

        self.output_lists(self.day,self.kiosk)

        # Driving variables
        self.drv = self._get_driving_variables(self.day)

        # Agromanagement decisions
        self.agromanager(self.day, self.drv)

        # Rate calculation
        self.calc_rates(self.day, self.drv, self.my_drv,self.modelkinds)


        if self.flag_terminate is True:
            self._terminate_simulation(self.day)


    def run(self, days=1):
        """Advances the system state with given number of days"""

        days_done = 0
        while (days_done < days) and (self.flag_terminate is False):
            days_done += 1
            self._run()

    def run_till_terminate(self):
        """Runs the system until a terminate signal is sent."""

        while self.flag_terminate is False:
            self._run()

    def run_till(self, rday):
        """Runs the system until rday is reached."""

        try:
            rday = check_date(rday)
        except KeyError as e:
            msg = "run_till() function needs a date object as input"
            print(msg)
            return

        if rday <= self.day:
            msg = "date argument for run_till() function before current model date."
            print(msg)
            return

        while self.flag_terminate is False and self.day < rday:
            self._run()

    def _on_CROP_FINISH(self, day, crop_delete=False):
        """Sets the variable 'flag_crop_finish' to True when the signal
        CROP_FINISH is received.

        The flag is needed because finishing the crop simulation is deferred to
        the correct place in the processing loop and is done by the routine
        _finish_cropsimulation().

        If crop_delete=True the CropSimulation object will be deleted from the
        hierarchy in _finish_cropsimulation().

        Finally, summary output will be generated depending on
        conf.SUMMARY_OUTPUT_VARS
        """
        self.flag_crop_finish = True
        self.flag_crop_delete = crop_delete

    def _on_CROP_START(self, day, crop_name=None, variety_name=None,
                       crop_start_type=None, crop_end_type=None):
        """Starts the crop
        """
        self.logger.debug("Received signal 'CROP_START' on day %s" % day)

        if self.crop is not None:
            msg = ("A CROP_START signal was received while self.cropsimulation "
                   "still holds a valid cropsimulation object. It looks like "
                   "you forgot to send a CROP_FINISH signal with option "
                   "crop_delete=True")
            raise exc.PCSEError(msg)

        self.parameterprovider.set_active_crop(crop_name, variety_name, crop_start_type,
                                               crop_end_type)
        self.crop = self.mconf.CROP(day, self.kiosk, self.parameterprovider,self.cropinitiallist)

    def _on_TERMINATE(self):
        """Sets the variable 'flag_terminate' to True when the signal TERMINATE
        was received.
        """
        self.flag_terminate = True

    def _on_OUTPUT(self):
        """Sets the variable 'flag_output to True' when the signal OUTPUT
        was received.
        """
        self.flag_output = True

    def _finish_cropsimulation(self, day):
        """Finishes the CropSimulation object when variable 'flag_crop_finish'
        has been set to True based on the signal 'CROP_FINISH' being
        received.
        """
        self.flag_crop_finish = False

        # Run the finalize section of the cropsimulation and sub-components
        self.crop.finalize(day)

        # Generate summary output after finalize() has been run.
        self._save_summary_output()

        # Clear any override parameters in the ParameterProvider to avoid
        # lagging parameters for the next crop
        self.parameterprovider.clear_override()

        # Only remove the crop simulation object from the system when the crop
        # is finished, when explicitly asked to do so.
        if self.flag_crop_delete:
            self.flag_crop_delete = False
            self.crop._delete()
            self.crop = None
            # Run a dedicated garbage collection, because it was demonstrated
            # that the standard python GC did not garbage collect the crop
            # simulation object. This caused signals to be received by crop simulation
            # objects that were supposed to be garbage collected already.
            gc.collect()

    def _terminate_simulation(self, day):
        """Terminates the entire simulation.

        First the finalize() call on the soil component is executed.
        Next, the TERMINAL_OUTPUT is collected and stored.
        """

        if self.soil is not None:
            self.soil.finalize(self.day)
        self._save_terminal_output()

    def _get_driving_variables(self, day):
        """Get driving variables, compute derived properties and return it.
        """
        drv = self.weatherdataprovider(day)

        # average temperature and average daytemperature (if needed)
        if not hasattr(drv, "TEMP"):
            drv.add_variable("TEMP", (drv.TMIN + drv.TMAX)/2., "Celcius")
        if not hasattr(drv, "DTEMP"):
            drv.add_variable("DTEMP", (drv.TEMP + drv.TMAX)/2., "Celcius")

        return drv

    def _save_output(self, day):
        """Appends selected model variables to self._saved_output for this day.
        """
        # Switch off the flag for generating output
        self.flag_output = False

        # find current value of variables to are to be saved
        states = {"day":day}
        for var in self.mconf.OUTPUT_VARS:
            states[var] = self.get_variable(var)
        self._saved_output.append(states)

    def _save_summary_output(self):
        """Appends selected model variables to self._saved_summary_output.
        """
        # find current value of variables to are to be saved
        states = {}
        for var in self.mconf.SUMMARY_OUTPUT_VARS:
            states[var] = self.get_variable(var)
        self._saved_summary_output.append(states)

    def _save_terminal_output(self):
        """Appends selected model variables to self._saved_terminal_output.
        """
        # find current value of variables to are to be saved
        for var in self.mconf.TERMINAL_OUTPUT_VARS:
            self._saved_terminal_output[var] = self.get_variable(var)

    def set_variable(self, varname, value):
        """Sets the value of the specified state or rate variable.

        :param varname: Name of the variable to be updated (string).
        :param value: Value that it should be updated to (float)

        :returns: a dict containing the increments of the variables
            that were updated (new - old). If the call was unsuccessful
            in finding the class method (see below) it will return an empty
            dict.

        Note that 'setting' a variable (e.g. updating a model state) is much more
        complex than just `getting` a variable, because often some other
        internal variables (checksums, related state variables) must be updated
        as well. As there is no generic rule to 'set' a variable it is up to
        the model designer to implement the appropriate code to do the update.

        The implementation of `set_variable()` works as follows. First it will
        recursively search for a class method on the simulationobjects with the
        name `_set_variable_<varname>` (case sensitive). If the method is found,
        it will be called by providing the value as input.

        So for updating the crop leaf area index (varname 'LAI') to value '5.0',
        the call will be: `set_variable('LAI', 5.0)`. Internally, this call will
        search for a class method `_set_variable_LAI` which will be executed
        with the value '5.0' as input.
        """
        increments = {}
        if self.soil is not None:
            self.soil.set_variable(varname, value, increments)
        if self.crop is not None:
            self.crop.set_variable(varname, value, increments)

        return increments

    def get_output(self):
        """Returns the variables have have been stored during the simulation.

        If no output is stored an empty list is returned. Otherwise, the output is
        returned as a list of dictionaries in chronological order. Each dictionary is
        a set of stored model variables for a certain date. """

        return self._save_output

    def get_summary_output(self):
        """Returns the summary variables have have been stored during the simulation.
        """

        return self._saved_summary_output

    def get_terminal_output(self):
        """Returns the terminal output variables have have been stored during the simulation.
        """

        return self._saved_terminal_output

Engine = my_Engine



def my_integrate(self, day, delt):
    # Flush state variables from the kiosk before state updates
        # self.kiosk.flush_states()

        if self.crop is not None:
            self.crop.integrate(day, delt)

        if self.soil is not None:
            self.soil.integrate(day, delt)

        # Set all rate variables to zero
        # if settings.ZEROFY:
        #     self.zerofy()

        # Flush rate variables from the kiosk after state updates
        # self.kiosk.flush_rates()
Engine.integrate = my_integrate



from pcse.fileinput import CSVWeatherDataProvider
# def my_get_driving_variables(self, day):
#     """Get driving variables, compute derived properties and return it.
#     """
#     drv = self.weatherdataprovider(day)

#     # average temperature and average daytemperature (if needed)
#     if not hasattr(drv, "TEMP"):
#         drv.add_variable("TEMP", (drv.TMIN + drv.TMAX)/2., "Celcius")
#     if not hasattr(drv, "DTEMP"):
#         drv.add_variable("DTEMP", (drv.TEMP + drv.TMAX)/2., "Celcius")
#     drv.add_variable("DTEMP", (drv.TEMP + drv.TMAX)/2., "Celcius")

#     return drv

# Engine._get_driving_variables = my_get_driving_variables



def my_on_CROP_START(self, day, crop_name=None, variety_name=None,
                    crop_start_type=None, crop_end_type=None):
    """Starts the crop
    """
    self.logger.debug("Received signal 'CROP_START' on day %s" % day)

    if self.crop is not None:
        msg = ("A CROP_START signal was received while self.cropsimulation "
                "still holds a valid cropsimulation object. It looks like "
                "you forgot to send a CROP_FINISH signal with option "
                "crop_delete=True")
        raise exc.PCSEError(msg)

    # self.parameterprovider.set_active_crop(crop_name, variety_name, crop_start_type,
    #                                         crop_end_type)
    self.crop = self.mconf.CROP(day, self.kiosk, self.parameterprovider,self.cropinitiallist,self.modelkinds)

Engine._on_CROP_START = my_on_CROP_START


class tomatomato(Engine):
    #使用したいconfigファイルを指定
    config = "C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse_pypl/PCSE/tomatomato.conf"


    def __init__(self, parameterprovider, weatherdataprovider, agromanagement,weathertimeseries,cropinitiallist,modelkinds):
        Engine.__init__(self, parameterprovider, weatherdataprovider, agromanagement, weathertimeseries,cropinitiallist,modelkinds,config=self.config)