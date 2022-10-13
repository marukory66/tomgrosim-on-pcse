
#%%
import yaml

sample = {'key1': 'value', 'key2': 'valuess'}

with open("C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse/tomato.yaml") as file:
    yamldata = yaml.safe_load(file)
    # print(yamldata)
    y = (yamldata["CropParameters"]['EcoTypes'])
    # yamldata["ss"].append(sample)
    print(y)
    for y_out in y:
        print(y_out)




#%%