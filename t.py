import pandas as pd

df = pd.read_excel(r"Projectdata_rev3.xlsx")

locs = df['Messort']
lats = df['Breitengrad']
lons = df['Längengrad']
    
for i in [locs, lats, lons]:
       idx = i[i.isna()].index
       print(idx , i)
       locs = locs.drop(idx, errors='ignore')
       lats = lats.drop(idx, errors='ignore')
       lons = lons.drop(idx, errors='ignore')


'''
df = pd.read_csv('df.csv')

df['Auftragsdatum']= df['Auftragsdatum'].str.extract(r"(\d{4}-\d{2}-\d{2})").fillna('')
df['Messung 1 Datum/ MA']= df['Messung 1 Datum/ MA'].str.extract(r"(\d{4}-\d{2}-\d{2})").fillna('')
df['Messung 2 Datum/ MA']= df['Messung 2 Datum/ MA'].str.extract(r"(\d{4}-\d{2}-\d{2})").fillna('')
df['Messung 3 Datum/ MA.1']= df['Messung 3 Datum/ MA.1'].str.extract(r"(\d{4}-\d{2}-\d{2})").fillna('')

print(df.loc[df.Messort == 'WP Thüle' , 'Auftragsdatum'])

df1 = pd.read_csv('df1.csv')

df1['Auftragsdatum']= df1['Auftragsdatum'].str.extract(r"(\d{4}-\d{2}-\d{2})").fillna('')
df1['Messung 1 Datum/ MA']= df1['Messung 1 Datum/ MA'].str.extract(r"(\d{4}-\d{2}-\d{2})").fillna('')
df1['Messung 2 Datum/ MA']= df1['Messung 2 Datum/ MA'].str.extract(r"(\d{4}-\d{2}-\d{2})").fillna('')
df1['Messung 3 Datum/ MA.1']= df1['Messung 3 Datum/ MA.1'].str.extract(r"(\d{4}-\d{2}-\d{2})").fillna('')


print(df1.loc[df.Messort == 'WP Thüle' , 'Auftragsdatum'])

df2 = pd.concat([df , df1])

df2['Auftragsdatum']= df2['Auftragsdatum'].str.extract(r"(\d{4}-\d{2}-\d{2})").fillna('')
df2['Messung 1 Datum/ MA']= df2['Messung 1 Datum/ MA'].str.extract(r"(\d{4}-\d{2}-\d{2})").fillna('')
df2['Messung 2 Datum/ MA']= df2['Messung 2 Datum/ MA'].str.extract(r"(\d{4}-\d{2}-\d{2})").fillna('')
df2['Messung 3 Datum/ MA.1']= df2['Messung 3 Datum/ MA.1'].str.extract(r"(\d{4}-\d{2}-\d{2})").fillna('')

df2 = df2[['Priority 1-6 (low - high)', 'Status (messklar/on hold)',
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
       'L2C/ Salesforce (Link)']]



df2 = df2.reset_index(drop=True)
df2.drop_duplicates(inplace=True)
df2 = df2.reset_index(drop=True)
df2 = df2.drop_duplicates()

df2.loc[df2.Messort == 'WP Thüle'].to_csv('b.csv')
#df2['Auftragsdatum']= pd.to_datetime(df2['Auftragsdatum'][0:10])
print(df2.loc[df2.Messort == 'WP Thüle'])
#print(df2['Auftragsdatum'].str.split(' '))

print(df1.loc[df2.Messort == 'WP Thüle' , ['Auftragsdatum' , 'sonst. Bemerkungen', 'Messung 1 Datum/ MA','Messung 2 Datum/ MA', 'Messung 3 Datum/ MA.1']])
'''