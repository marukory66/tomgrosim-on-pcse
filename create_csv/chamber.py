#%%
import pandas as pd

plantdata_excel = "C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse_pypl/plantation_data/pi01_20191023_2hour - コピー.csv"




df_2hour = "C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse_pypl/Diffusion_2hour.csv"

def pick_up_chamber_data(plantdata_excel,df_2hour):
#チャンバデータの加工
    df_plantdata_excel = pd.read_csv(plantdata_excel)
    df_plantdata_excel["date"] = df_plantdata_excel["Date"].str.split(pat=' ', expand=True)[0]
    df_plantdata_excel["hour"] = df_plantdata_excel["Date"].str.split(pat=' ', expand=True)[1]
    df_plantdata_excel_date = df_plantdata_excel[["date","hour","Solar radiation","CO2 concentration air sampling average","Temperature inside chamber"]]
    df_plantdata_excel_date["hour"] = df_plantdata_excel_date["hour"].str.split(pat=':', expand=True)[0]
    df_plantdata_excel_date["PAR"] =  df_plantdata_excel_date["Solar radiation"].apply(lambda x: x*0.475)

    #2時間環境データの追加
    df_2hour = df_2hour[["h","FRACDF"]]
    df_plantdata_excel_date = pd.concat([df_2hour,df_plantdata_excel_date],axis=1)
    lengeth_plantdata_excel_date = len(df_plantdata_excel_date)-1
    df_plantdata_excel_date["PARDIR"] = 0
    df_plantdata_excel_date["PARDIF"] = 0

    for i1,i in enumerate(range(lengeth_plantdata_excel_date)):
        tmp = df_plantdata_excel_date.iloc[i1]
        PAR = tmp["PAR"]
        FRACDF = tmp["FRACDF"]
        PARDIR = PAR*(1-FRACDF)
        PARDIF = PAR*FRACDF
        df_plantdata_excel_date["PARDIR"].loc[i1] = PARDIR
        df_plantdata_excel_date["PARDIF"].loc[i1] = PARDIF

    df = df_plantdata_excel_date.dropna(how="any",axis=0)
    df = (df.loc[:,~df.columns.duplicated()])

    return df

# df = pick_up_chamber_data(plantdata_excel,df_2hour)
# df.to_csv('C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse_pypl/df.csv')
