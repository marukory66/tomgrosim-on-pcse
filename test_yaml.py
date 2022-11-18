#%%
import os, sys
import matplotlib
# matplotlib.style.use("ggplot")
import matplotlib.pyplot as plt
import pandas as pd
import yaml
import pcse
from pcse.models import Wofost72_WLP_FD
from pcse.fileinput import CABOFileReader, YAMLCropDataProvider
from pcse.db import NASAPowerWeatherDataProvider
from pcse.util import WOFOST72SiteDataProvider
from pcse.base import ParameterProvider
from models import sample
# crop = YAMLCropDataProvider
# p = YAMLCropDataProvider(fpath=r"C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse/")

# -*- coding: utf-8 -*-
# Copyright (c) 2004-2017 Alterra, Wageningen-UR
# Allard de Wit (allard.dewit@wur.nl), February 2017
import glob
import os, sys

v = sys.version_info
if v.major == 3:
    # For Python 3.0 and later
    from urllib.request import urlopen
    from urllib.error import URLError
    import pickle
else:
    # Fall back to Python 2's urllib2
    from urllib2 import urlopen, URLError
    import cPickle as pickle

import yaml

from pcse.base import MultiCropDataProvider
from pcse import exceptions as exc
from pcse import settings
from pcse.util import version_tuple


class my_YAMLCropDataProvider(MultiCropDataProvider):
    HTTP_OK = 200
    current_crop_name = None
    current_variety_name = None

    # Compatibility of data provider with YAML parameter file version
    compatible_version = "1.0.0"

    def __init__(self, fpath=None, repository=None, force_reload=False):
        MultiCropDataProvider.__init__(self)

        if not self._load_cache(fpath) or force_reload:
            if force_reload:  # enforce a clear state when we force a reload
                self.clear()
                self._store.clear()

            if fpath is not None:
                yaml_file_names = self._get_yaml_files(fpath)
                for crop_name, yaml_fname in yaml_file_names.items():
                    with open(yaml_fname) as fp:
                        parameters = yaml.safe_load(fp)
                    self._check_version(parameters, crop_fname=yaml_fname)
                    self._add_crop(crop_name, parameters)

            elif repository is not None:
                if not repository.endswith("/"):
                    repository += "/"
                self.repository = repository
                try:
                    url = self.repository + "crops.yaml"
                    response = urlopen(url)
                    self.crop_types = yaml.safe_load(response)["available_crops"]
                except URLError as e:
                    msg = "Unable to find crops.yaml at '%s' due to: %s" % (url, e)
                    raise exc.PCSEError(msg)

                for crop_name in self.crop_types:
                    url = self.repository + crop_name + ".yaml"
                    try:
                        response = urlopen(url)
                    except URLError as e:
                        msg = "Unable to open '%s' due to: %s" % (url, e)
                        raise exc.PCSEError(msg)
                    parameters = yaml.safe_load(response)
                    self._check_version(parameters, crop_name)
                    self._add_crop(crop_name, parameters)

            else:
                msg = "No path or URL specified where to find YAML crop parameter files"
                raise exc.PCSEError(msg)

            with open(self._get_cache_fname(fpath), "wb") as fp:
                pickle.dump((self.compatible_version, self._store), fp, pickle.HIGHEST_PROTOCOL)

    def _get_cache_fname(self, fpath):
        """Returns the name of the cache file for the CropDataProvider.
        """
        cache_fname = "%s.pkl" % self.__class__.__name__
        if fpath is None:
            cache_fname_fp = os.path.join(settings.METEO_CACHE_DIR, cache_fname)
        else:
            cache_fname_fp = os.path.join(fpath, cache_fname)
        return cache_fname_fp

    def _load_cache(self, fpath):
        """Loads the cache file if possible and returns True, else False.
        """
        try:
            cache_fname_fp = self._get_cache_fname(fpath)
            if os.path.exists(cache_fname_fp):

                # First we check that the cache file reflects the contents of the YAML files.
                # This only works for files not for github repos
                if fpath is not None:
                    yaml_file_names = self._get_yaml_files(fpath)
                    yaml_file_dates = [os.stat(fn).st_mtime for fn in yaml_file_names]
                    # retrieve modification date of cache file
                    cache_date = os.stat(cache_fname_fp).st_mtime
                    # Ensure cache file is more recent then any of the YAML files
                    if any([d > cache_date for d in yaml_file_dates]):
                        return False

                # Now start loading the cache file
                with open(cache_fname_fp, "rb") as fp:
                    version, store = pickle.load(fp)
                if version_tuple(version) != version_tuple(self.compatible_version):
                    msg = "Cache file is from a different version of YAMLCropDataProvider"
                    raise exc.PCSEError(msg)
                self._store = store
                return True

        except Exception as e:
            msg = "%s - Failed to load cache file: %s" % (self.__class__.__name__, e)
            print(msg)

        return False

    def _check_version(self, parameters, crop_fname):
        """Checks the version of the parameter input with the version supported by this data provider.
        Raises an exception if the parameter set is incompatible.
        :param parameters: The parameter set loaded by YAML
        """
        try:
            v = parameters['Version']
            if version_tuple(v) != version_tuple(self.compatible_version):
                msg = "Version supported by %s is %s, while parameter set version is %s!"
                raise exc.PCSEError(msg % (self.__class__.__name__, self.compatible_version, parameters['Version']))
        except Exception as e:
            msg = f"Version check failed on crop parameter file: {crop_fname}"
            raise exc.PCSEError(msg)

    def _add_crop(self, crop_name, parameters):
        """Store the parameter sets for the different varieties for the given crop.
        """
        variety_sets = parameters["CropParameters"]["Varieties"]
        self._store[crop_name] = variety_sets

    def _get_yaml_files(self, fpath):
        """Returns all the files ending on *.yaml in the given path.
        """
        fname = os.path.join(fpath, "crops.yaml")
        if not os.path.exists(fname):
            msg = "Cannot find 'crops.yaml' at {f}".format(f=fname)
            raise exc.PCSEError(msg)
        crop_names = yaml.safe_load(open(fname))["available_crops"]
        crop_yaml_fnames = {crop: os.path.join(fpath, crop + ".yaml") for crop in crop_names}
        return crop_yaml_fnames

    def set_active_crop(self, crop_name, variety_name):
        """Sets the parameters in the internal dict for given crop_name and variety_name
        It first clears the active set of crop parameter sin the internal dict.
        :param crop_name: the name of the crop
        :param variety_name: the variety for the given crop
        """
        self.clear()
        if crop_name not in self._store:
            msg = "Crop name '%s' not available in %s " % (crop_name, self.__class__.__name__)
            raise exc.PCSEError(msg)
        variety_sets = self._store[crop_name]
        if variety_name not in variety_sets:
            msg = "Variety name '%s' not available for crop '%s' in " \
                  "%s " % (variety_name, crop_name, self.__class__.__name__)
            raise exc.PCSEError(msg)

        self.current_crop_name = crop_name
        self.current_variety_name = variety_name

        # Retrieve parameter name/values from input (ignore description and units)
        parameters = {k: v[0] for k, v in variety_sets[variety_name].items() if k != "Metadata"}
        # update internal dict with parameter values for this variety
        self.update(parameters)

    def get_crops_varieties(self):
        """Return the names of available crops and varieties per crop.
        :return: a dict of type {'crop_name1': ['variety_name1', 'variety_name1', ...],
                                 'crop_name2': [...]}
        """
        return {k: v.keys() for k, v in self._store.items()}

    def print_crops_varieties(self):
        """Gives a printed list of crops and varieties on screen.
        """
        msg = ""
        for crop, varieties in self.get_crops_varieties().items():
            msg += "crop '%s', available varieties:\n" % crop
            for var in varieties:
                msg += (" - '%s'\n" % var)
        print(msg)

    def __str__(self):
        if not self:
            msg = "%s - crop and variety not set: no activate crop parameter set!\n" % self.__class__.__name__
            return msg
        else:
            msg = "%s - current active crop '%s' with variety '%s'\n" % \
                  (self.__class__.__name__, self.current_crop_name, self.current_variety_name)
            msg += "Available crop parameters:\n %s" % str(dict.__str__(self))
            return msg
YAMLCropDataProvider = my_YAMLCropDataProvider
#%%
p = YAMLCropDataProvider(fpath=r"C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse/yamls")
p.set_active_crop('tomato','tomato_01')
# print(ProcessLookupError())
crop = p
soil = CABOFileReader("C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse/test_data/ec3.soil")
site = WOFOST72SiteDataProvider(WAV=100,CO2=360)
parameterprovider = ParameterProvider(soildata=soil, cropdata=crop, sitedata=site)

#%%
from pcse.fileinput import ExcelWeatherDataProvider
yaml_agro = """
- 2006-01-01:
    CropCalendar:
        crop_name: sugarbeet
        variety_name: Sugarbeet_603
        crop_start_date: 2006-03-31
        crop_start_type: emergence
        crop_end_date: 2006-10-20
        crop_end_type: harvest
        max_duration: 300
    TimedEvents:
    -   event_signal: irrigate
        name: Irrigation application table
        comment: All irrigation amounts in cm
        events_table:
        - 2006-07-10: {amount: 10, efficiency: 0.7}
        - 2006-08-05: {amount:  5, efficiency: 0.7}
    StateEvents: null
"""
weatherfile = ("C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse/test_data/nl1.xls")
weatherdataprovider = ExcelWeatherDataProvider(weatherfile)
agromanagement = yaml.load(yaml_agro,Loader=yaml.Loader)
wofost = sample(parameterprovider, weatherdataprovider, agromanagement)

wofost.run_till_terminate()
output = wofost.get_output()
df = pd.DataFrame(output).set_index("day")
df.tail()
# %%
