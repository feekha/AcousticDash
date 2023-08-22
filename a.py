import pandas as pd
from copy import deepcopy
import pickle

def dump_df(df):
    
    with open('cache/df_data.pickle', 'wb') as handle:
        pickle.dump(df, handle, protocol=pickle.HIGHEST_PROTOCOL)

def dump_org_cols(df_original_cols): 
    
    with open('cache/df_oroginal_cols.pickle', 'wb') as handle:
        pickle.dump(df_original_cols, handle, protocol=pickle.HIGHEST_PROTOCOL)
  
if __name__ == "__main__":
    # ------ load data initialy

    df = pd.read_excel(r"Projectdata_rev3.xlsx")

    #print(df)
    
    #print(df.columns)

    
    df = df[['Priority 1-6 (low - high)', 'Status (messklar/on hold)', 'Messort',
       'Art', 'Hersteller', 'WEA-Typ',
       'Projektnumber  (link to PowerBI PM Dashboard)', 'Projectname',
       'DNV PM', 'Auftragsdatum', 'Kunde',
       'Ansprechpartner Kunde (E-Mail, phone)', 'WEA X von Y', 'Ser.-Nr.',
       'WP-Nr.:', 'Hubheight', 'Rotordiameter', 'HB', 'LK', 'BImschG',
       'Modi Liste', 'Beschwerdelage ja/nein Bemerkungen',
       'min. Wind speed needed', 'max. Wind speed needed',
       'bevorz.  WR (falls bekannt)',
       'Landowner of  Turbine or Measurment area',
       'Owner of neighbour turbines which have to be shut down',
       'Gridoperator EisMan', 'sonst. Bemerkungen', 'Messung 1 Datum/ MA',
       'Messung 2 Datum/ MA', 'Messung 3 Datum/ MA.1', 'Stand x = close',
       'Link project folder Acoustics', 'Breitengrad', 'Längengrad',
       'L2C/ Salesforce (Link)']]

    

    df_original_cols = deepcopy(df.columns)
    cols=[]
    for col in df.columns:
        cols.append(str(col).replace('\n',' '))

    
    cols = ['Priority 1-6 (low - high)', 'Status (messklar/on hold)',
                        'Messort', 'Art', 'Hersteller', 'WEA-Typ',
                        'Projektnumber  (link to PowerBI PM Dashboard)', 'Projectname',
                        'DNV PM', 'Auftragsdatum', 'Kunde',
                        'Ansprechpartner Kunde (E-Mail, phone)', 'WEA X von Y', 'Ser.-Nr.',
                        'WP-Nr.:', 'Hubheight', 'Rotordiameter', 'HB', 'LK', 'BImschG',
                        'Modi Liste', 'Beschwerdelage ja/nein Bemerkungen',
                        'min. Wind speed needed', 'max. Wind speed needed',
                        'bevorz.  WR (falls bekannt)',
                        'Landowner of  Turbine or Measurment area',
                        'Owner of neighbour turbines which have to be shut down',
                        'Gridoperator EisMan', 'sonst. Bemerkungen', 'Messung 1 Datum/ MA',
                        'Messung 2 Datum/ MA', 'Messung 3 Datum/ MA.1', 'Stand x = close',
                        'Link project folder Acoustics', 'Breitengrad', 'Längengrad',
                        'L2C/ Salesforce (Link)']
    

    df.columns = cols
    dump_org_cols(df_original_cols)
    dump_df(df)

    project_managers = df["DNV PM"].unique()

    print(project_managers)

