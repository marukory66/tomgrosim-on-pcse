#%%
from pcse.fileinput import CABOFileReader
# cropfile = os.path.join(data_dir, 'crop', 'SUG0601.crop')
cropfile = os.path.join("C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse/SUG0601.crop")
cropd = CABOFileReader(cropfile)
print(cropd)
#%%
from pcse.fileinput import CABOFileReader
import re

class read_lists(dict):
    # RE patterns for parsing scalar, table and string parameters
    # tbpar = "[a-zA-Z0-9_]+[\s]*=[\s]*(\[)?[\s]*[0-9,.\s\-+]+(\])?"
    tbpar = "[a-zA-Z0-9_]+[\s]*=[\s]*[0-9,.\s\-+]+"
    strpar = "[a-zA-Z0-9_]+[\s]*=[\s]*'.*?'"
    scpar = "[a-zA-Z0-9_]+[\s]*=[\s]*[a-zA-Z0-9_.\-]+"

    def _remove_empty_lines(self, filecontents):
        t = []
        for line in filecontents:
            line = line.strip(" \n\r")
            if len(line)>0:
                t.append(line)
        return t
        
    def _remove_inline_comments(self, filecontents):
        t = []
        for line in filecontents:
            line = line.split("!")[0]
            line.strip()
            if len(line) > 0:
                t.append(line)
        return t
    
    def _is_comment(self, line):
        if line.startswith("*"):
            return True
        else:
            return False

    def _find_header(self, filecontents):
        """Parses and strips header marked with '*' at the beginning of 
        the file. Further lines marked with '*' are deleted."""

        header = []
        other_contents = []
        inheader = True
        for line in filecontents:
            if inheader is True:
                if self._is_comment(line):
                    header.append(line)
                else:
                    other_contents.append(line)
                    inheader = False
            else:
                if self._is_comment(line):
                    pass
                else:
                    other_contents.append(line)
        # print("other",other_contents)
        return (header, other_contents)
        
    def _parse_table_values(self, parstr):
        """Parses table parameter into a list of floats."""
        
        tmpstr = parstr.strip()
        print(tmpstr)
        valuestrs = tmpstr.split(",")
        tblvalues = []
        for vstr in valuestrs:
            if vstr != '':    
                # value = float(vstr)
                tblvalues.append(vstr)
        return tblvalues
        
        # tmpstr = parstr.strip()
        # valuestrs = tmpstr.split(",")
        # tblvalues = []
        # for vstr in valuestrs:
        #     if vstr != '':    
        #         value = float(vstr)
        #         tblvalues.append(value)
        # return tblvalues
        
        
        
    def _find_parameter_sections(self, filecontents):
        "returns the sections defining float, string and table parameters."
        scalars = ""
        strings = ""
        tables = ""
        for line in filecontents:
            if line.find("'") != -1: # string parameter
                strings += (line + " ")
            elif line.find(",") != -1: # table parameter
                tables += (line + " ")
            else:
                scalars += (line + " ")
              
        return scalars, strings, tables

    def _find_individual_pardefs(self, regexp, parsections):
        """Splits the string into individual parameters definitions.
        """
        par_definitions = re.findall(regexp, parsections)
        rest = re.sub(regexp, "", parsections)
        rest = rest.replace(";", "")
        if rest.strip() != "":
            msg = "Failed to parse the CABO file!\n" +\
                  ("Found the following parameter definitions:\n %s" % par_definitions) + \
                  ("Failed to parse:\n %s" % rest)
            raise PCSEError(msg)
        return par_definitions
    
    def my_find_individual_pardefs(self,tables):
        m = re.findall('[A-Z]+', tables)
        place_param_names = []
        for place_param_name in  m:
            place_param_names.append(tables.find(place_param_name))
        tables =list(tables)
        for index , p_index in enumerate(range(1,len(m))):
            replace = place_param_names[p_index] + index*3
            tables.insert(replace, "'")
            tables.insert(replace, ",")
            tables.insert(replace, "'")
        tables = ''.join(tables)
        tables = [tables]
        tables = str(tables)
        tables = re.split("','",tables)
        for i in tables:
            i = i.replace('["',"")
            i = i.replace('"',"")
        return tables


    def __init__(self,fname):
        with open(fname) as fp:
            filecontents = fp.readlines()
        filecontents = self._remove_empty_lines(filecontents)
        filecontents = self._remove_inline_comments(filecontents)
        if len(filecontents) == 0:
            msg = "Empty CABO file!"
            raise PCSEError(msg)

        # Split between file header and parameters
        self.header, filecontents = self._find_header(filecontents)
        # Find parameter sections using string methods
        
        # print(filecontents)

        scalars, strings, tables = self._find_parameter_sections(filecontents)
        # Parse into individual parameter definitions
        
        # table_defs = self._find_individual_pardefs(self.tbpar, tables)
        table_defs = self.my_find_individual_pardefs(tables)
        scalar_defs = self._find_individual_pardefs(self.scpar, scalars)
        string_defs = self._find_individual_pardefs(self.strpar, strings)

        # Parse individual parameter definitions into name & value.
        for parstr in table_defs:
            parname, valuestr = parstr.split("=")
            parname = parname.strip()
            value = self._parse_table_values(valuestr)
            self[parname] = value

        for parstr in scalar_defs:
            try:
                parname, valuestr = parstr.split("=")
                parname = parname.strip()
                if valuestr.find(".") != -1:
                    value = float(valuestr)
                else:
                    value = int(valuestr)
                self[parname] = value
            except (ValueError) as exc:
                msg = "Failed to parse parameter, value: %s, %s" 
                raise PCSEError(msg % (parstr, valuestr))
        for parstr in string_defs:
            try:
                parname, valuestr = parstr.split("=", 1)
                parname = parname.strip()
                value = (valuestr.replace("'","")).replace('"','')
                self[parname] = value
            except (ValueError) as exc:
                msg = "Failed to parse parameter, value: %s, %s" 
                raise PCSEError(msg % (parstr, valuestr))
            
            
    def __str__(self):
        msg = ""
        for line in self.header:
            msg += line+"\n"
        msg += "------------------------------------\n"
        for key, value in self.items():
            msg += ("%s: %s %s\n" % (key, value, type(value)))
        return msg
      
cropfile = os.path.join("C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse/sample.crop")
cropd = read_lists(cropfile)
print(cropd)
import sys, os
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import pcse
from pcse.fileinput import CABOFileReader
from pcse.util import WOFOST72SiteDataProvider
from pcse.base import ParameterProvider
from pcse.fileinput import YAMLAgroManagementReader
from pcse.fileinput import ExcelWeatherDataProvider,PCSEFileReader,CABOWeatherDataProvider
from models import sample 
from pcse.fileinput import PCSEFileReader
from pcse.base import ParameterProvider
soil = PCSEFileReader("C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse/test_data/lintul3_springwheat.soil")
site = PCSEFileReader("C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse/test_data/lintul3_springwheat.site")
parameters = ParameterProvider(sitedata=site, soildata=soil, cropdata=cropd)
weatherfile = os.path.join("C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse/nl1.xlsx")

agromanagement_file = os.path.join("C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse/test_data/sugarbeet_calendar.agro")
sited = WOFOST72SiteDataProvider(WAV=10, CO2=360) # site parameters
agromanagement = YAMLAgroManagementReader(agromanagement_file) # agromanagement
# Daily environmental conditions
# Solar radiation, air temperature, vapor pressure, wind speed, precipitation, and snow depth.
wdp = ExcelWeatherDataProvider(weatherfile)
wofsim = sample(parameters, wdp, agromanagement)
wofsim.run_till_terminate()
df_results = pd.DataFrame(wofsim.get_output())
df_results = df_results.set_index("day")



#%%




from pcse.fileinput import YAMLCropDataProvider

p = YAMLCropDataProvider(repository="https://github.com/marukory66/tomgrosim-on-pcse/tree/develop/test_data")
# p = YAMLCropDataProvider()
print(p)
p.set_active_crop('sample', 'cassava')
print(p)







#%%
import pcse
from pcse.fileinput import CABOFileReader
from pcse.util import WOFOST72SiteDataProvider
from pcse.base import ParameterProvider
from pcse.fileinput import YAMLAgroManagementReader
from pcse.fileinput import ExcelWeatherDataProvider,PCSEFileReader,CABOWeatherDataProvider
from models import sample 
#%%
import re
from pcse.fileinput import CABOFileReader
print("OK")
class my_CABOFileReader(dict):
    
    # RE patterns for parsing scalar, table and string parameters
    scpar = "[a-zA-Z0-9_]+[\s]*=[\s]*[a-zA-Z0-9_.\-]+"
    tbpar = "[a-zA-Z0-9_]+[\s]*=[\s]*[0-9,.\s\-+]+"
    strpar = "[a-zA-Z0-9_]+[\s]*=[\s]*'.*?'"
    
    def _remove_empty_lines(self, filecontents):
        t = []
        for line in filecontents:
            line = line.strip(" \n\r")
            if len(line)>0:
                t.append(line)
        return t
        
    def _remove_inline_comments(self, filecontents):
        t = []
        for line in filecontents:
            line = line.split("!")[0]
            line.strip()
            if len(line) > 0:
                t.append(line)
        return t
    
    def _is_comment(self, line):
        if line.startswith("*"):
            return True
        else:
            return False

    def _find_header(self, filecontents):
        """Parses and strips header marked with '*' at the beginning of 
        the file. Further lines marked with '*' are deleted."""

        header = []
        other_contents = []
        inheader = True
        for line in filecontents:
            if inheader is True:
                if self._is_comment(line):
                    header.append(line)
                else:
                    other_contents.append(line)
                    inheader = False
            else:
                if self._is_comment(line):
                    pass
                else:
                    other_contents.append(line)
        return (header, other_contents)
 
    def _parse_table_values(self, parstr):
        """Parses table parameter into a list of floats."""
        
        tmpstr = parstr.strip()
        # print("aaa",tmpstr)
        valuestrs = tmpstr.split(",")
        # if len(valuestrs) < 4:
        #     raise LengthError((len(valuestrs), valuestrs))
        if (len(valuestrs) % 2) != 0:
            raise XYPairsError((len(valuestrs), valuestrs))
        # print(valuestrs)
        tblvalues = []
        for vstr in valuestrs:
            value = float(vstr)
            tblvalues.append(value)
        return tblvalues
        
    def _find_parameter_sections(self, filecontents):
        "returns the sections defining float, string and table parameters."
        scalars = ""
        strings = ""
        tables = ""
        
        for line in filecontents:
            if line.find("'") != -1: # string parameter
                strings += (line + " ")
            elif line.find(",") != -1: # table parameter
                tables += (line + " ")
            else:
                scalars += (line + " ")
        return scalars, strings, tables
        
       
    def _find_individual_pardefs(self, regexp, parsections):
        """Splits the string into individual parameters definitions.
        """
        par_definitions = re.findall(regexp, parsections)
        rest = re.sub(regexp, "", parsections)
        rest = rest.replace(";", "")
        if rest.strip() != "":
            msg = "Failed to parse the CABO file!\n" +\
                  ("Found the following parameter definitions:\n %s" % par_definitions) + \
                  ("Failed to parse:\n %s" % rest)
            raise PCSEError(msg)
        return par_definitions

        
    def __init__(self, fname):
        with open(fname) as fp:
            filecontents = fp.readlines()
        filecontents = self._remove_empty_lines(filecontents)
        filecontents = self._remove_inline_comments(filecontents)
        # print(filecontents)
        if len(filecontents) == 0:
            msg = "Empty CABO file!"
            raise PCSEError(msg)

        # Split between file header and parameters
        self.header, filecontents = self._find_header(filecontents)
        
        # Find parameter sections using string methods
        scalars, strings, tables = self._find_parameter_sections(filecontents)
        scalar_defs = self._find_individual_pardefs(self.scpar, scalars)
        print(tables)
        table_defs = self._find_individual_pardefs(self.tbpar, tables)
        string_defs = self._find_individual_pardefs(self.strpar, strings)
        print("table_defs",table_defs)
        # Parse individual parameter definitions into name & value.
        for parstr in scalar_defs:
            try:
                parname, valuestr = parstr.split("=")
                parname = parname.strip()
                if valuestr.find(".") != -1:
                    value = float(valuestr)
                else:
                    value = int(valuestr)
                self[parname] = value
            except (ValueError) as exc:
                msg = "Failed to parse parameter, value: %s, %s" 
                raise PCSEError(msg % (parstr, valuestr))

        for parstr in string_defs:
            try:
                parname, valuestr = parstr.split("=", 1)
                parname = parname.strip()
                value = (valuestr.replace("'","")).replace('"','')
                self[parname] = value
            except (ValueError) as exc:
                msg = "Failed to parse parameter, value: %s, %s" 
                raise PCSEError(msg % (parstr, valuestr))

        for parstr in table_defs:
            parname, valuestr = parstr.split("=")
            parname = parname.strip()
            try:
                value = self._parse_table_values(valuestr)
                self[parname] = value
            except (ValueError) as exc:
                msg = "Failed to parse table parameter %s: %s" % (parname, valuestr)
                raise PCSEError(msg)
            except (LengthError) as exc:
                msg = "Failed to parse table parameter %s: %s. \n" % (parname, valuestr)
                msg += "Table parameter should contain at least 4 values "
                msg += "instead got %i" 
                raise PCSEError(msg % exc.value[0])
            except (XYPairsError) as exc:
                msg = "Failed to parse table parameter %s: %s\n" % (parname, valuestr)
                msg += "Parameter should be have even number of positions."
                raise XYPairsError(msg)
      
    def __str__(self):
        msg = ""
        for line in self.header:
            msg += line+"\n"
        msg += "------------------------------------\n"
        for key, value in self.items():
            msg += ("%s: %s %s\n" % (key, value, type(value)))
        return msg
      
# CABOFileReader= my_CABOFileReader
#%%

from pcse.fileinput import CABOFileReader
# cropfile = os.path.join(data_dir, 'crop', 'SUG0601.crop')
cropfile = os.path.join("C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse/sample.crop")
cropd = my_CABOFileReader(cropfile)
print(cropd)

from pcse.fileinput import PCSEFileReader
from pcse.base import ParameterProvider
# parameters = ParameterProvider(cropdata=cropd, soildata=soild, sitedata=sited)
soil = PCSEFileReader("C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse/test_data/lintul3_springwheat.soil")
site = PCSEFileReader("C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse/test_data/lintul3_springwheat.site")
# crop_hujiuchi = PCSEFileReader("C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse/test_data/SUG0601_modified.crop")
parameters = ParameterProvider(sitedata=site, soildata=soil, cropdata=cropd)

#%%
