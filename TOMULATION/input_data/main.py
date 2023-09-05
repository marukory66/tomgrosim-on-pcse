#%%
import pandas as pd
import os
import glob

def _create_input_data(csv_lists):
    return_dict = {}
    parames = str
    for i in range(len(csv_lists)):
        name = os.path.basename(csv_lists[i])
        name = os.path.splitext(name)[0]
        if name == "parames":
            data = pd.read_csv(csv_lists[i],header=None,index_col=None).values.tolist()
            for d_row in data:
                return_dict[d_row[0]]=d_row[1]
        elif name == "measured_photosynthesis":
            data = pd.read_csv(csv_lists[i],header=None).values.tolist()
            return_dict[name] = data

        else:
            data = read_two_dimensions_csv(csv_lists[i],name)
            return_dict[name] = data

    return return_dict

def read_two_dimensions_csv(path,name):
    data = pd.read_csv(path,index_col=None).values.tolist()
    for i,row in enumerate(range(len(data))):
        data[row].pop(0)
    return data

