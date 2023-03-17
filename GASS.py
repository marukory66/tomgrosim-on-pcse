# %%
#csvをyamlに記載するコード

import datetime
from pathlib import Path
from ruamel.yaml import YAML, add_constructor, resolver
# import ruamel.yaml
from collections import OrderedDict
import csv
import pandas as pd
import re
import glob
import os

# 入力時に順序を保持する
add_constructor(resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    lambda loader, node: OrderedDict(loader.construct_pairs(node)))
yaml = YAML()
yaml.default_flow_style = True
# yaml = ruamel.yaml.YAML()

with open(Path("C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse/tomato.yaml"), 'r+', encoding='utf-8') as f:
    yamldata = yaml.load(f)
    add_yamldata = yamldata["CropParameters"]['EcoTypes']["tomato"]
    
csv_file_path = "C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse/asai_plantation_data/出力用"
csv_paths = glob.glob(csv_file_path + "/*.csv")

for csv in csv_paths:
    df = pd.read_csv(csv,header=0)
    tmp_data = []
    csv_name = os.path.splitext(os.path.basename(csv))[0]
    for data in df.itertuples(name=None):
        data = list(data)
        data = data[2:]
        tmp_data.append(data)
    tmp_data = yaml.load(" - " + str(tmp_data) + "\n")
    
    # tmp_data = ruamel.yaml.scalarstring.LiteralScalarString(tmp_data)
    add_yamldata[csv_name]= tmp_data


# ファイルに出力。出力順序はデフォルトで保持される
with open(Path('C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse/sam.yaml'), 'w', encoding='utf-8') as f:
    yaml.dump(yamldata, f)

# %%

# yamlに代入
#一つのcsvファイルに複数記載想定，２重リスト無し想定

import csv
import pandas as pd
import re
# import yaml
import datetime
from pathlib import Path
from ruamel.yaml import YAML, add_constructor, resolver
from collections import OrderedDict

# 入力時に順序を保持する
add_constructor(resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    lambda loader, node: OrderedDict(loader.construct_pairs(node)))

yaml = YAML()
yaml.default_flow_style = False

with open(Path("C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse/tomato.yaml"), 'r+', encoding='utf-8') as f:
    yamldata = yaml.load(f)
    add_yamldata = yamldata["CropParameters"]['EcoTypes']["tomato"]

# 単数
def get_singular(yamlname,singular):
    add_yamldata[yamlname]=singular[0]

# list 
def get_list(yamlname,list_value):
    float_lst = [float(item) for item in list_value]
    add_yamldata[yamlname]=float_lst
    
# day
def get_day(yamlname,day):
    days_values = []
    for d in day:
        d = str(d)
        tdatetime = datetime.datetime.strptime(d,'%Y/%m/%d')
        d = datetime.date(tdatetime.year, tdatetime.month, tdatetime.day) 
        days_values.append(d)
    return days_values
    
#　辞書をyamlに出力
def export_dict(yamldata,day_dict):
    add_yamldata[yamldata]=day_dict
    
row = []
path = ("C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse/asai_plantation_data/出力用/ASSIM.csv")
df = pd.read_csv(path,header=0)
df = df.fillna("")
cols = []
for col in df.columns: 
    df_ex = df[col]
    df_ex = list(df_ex.values) 
    df_ex = list(filter(None,df_ex))
    cols.append(col)
    if len(df_ex) == 1:
        get_singular(col,df_ex)
    else:
        if type(df_ex[0]) == str:
            days_values = get_day(col,df_ex) 
        elif len(df_ex) >= 2:
            before_df_name = df[cols[-2]]
            before_df_name = list(before_df_name.values) 
            before_df_name = list(filter(None,before_df_name))
            before_df_name = before_df_name[0]
            if type(before_df_name) == str:
                float_df_ex = [float(item) for item in df_ex]
                day_dict = (dict(zip(days_values,float_df_ex)))
                export_dict(col,day_dict)
            elif type(before_df_name) != str:
                get_list(col, df_ex)
        else:
            print("想定外")

# ファイルに出力。出力順序はデフォルトで保持される
with open(Path('C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse/sam.yaml'), 'w', encoding='utf-8') as f:
    yaml.dump(yamldata, f)

# %%
# csvを読み込み
import csv
import pandas as pd
import re
import yaml
import datetime

 
# 単数
def get_singular(yamlname,singular):
    print("singular")
    print(yamlname)
    print(singular)

# list 
def get_list(yamlname,list):
    print("list")
    print(yamlname)
    print(list)
    pass

# day
def get_day(yamlname,day):
    days_values = []
    for d in day:
        d = str(d)
        tdatetime = datetime.datetime.strptime(d,'%Y/%m/%d')
        d = datetime.date(tdatetime.year, tdatetime.month, tdatetime.day) 
        days_values.append(str(d))
    return days_values

#　辞書をyamlに出力
def export_dict(yamldata,day_dict):
    pass

row = []
path = ("C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse/Book.csv")
df = pd.read_csv(path,header=0)
df = df.fillna("")
cols = []
for col in df.columns: 
    df_ex = df[col]
    df_ex = list(df_ex.values) 
    df_ex = list(filter(None,df_ex))
    cols.append(col)
    if len(df_ex) == 1:
        get_singular(col,df_ex)
    else:
        if type(df_ex[0]) == str:
            days_values = get_day(col,df_ex) 
        elif len(df_ex) >= 2:
            before_df_name = df[cols[-2]]
            before_df_name = list(before_df_name.values) 
            before_df_name = list(filter(None,before_df_name))
            before_df_name = before_df_name[0]
            if type(before_df_name) == str:
                day_dict = (dict(zip(days_values,df_ex)))
                export_dict(col,day_dict)

            elif type(before_df_name) != str:
                get_list(col, df_ex)
        else:
            print("想定外")
