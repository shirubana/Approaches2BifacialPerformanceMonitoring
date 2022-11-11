#!/usr/bin/env python
# coding: utf-8

# # 1 - Generating Inputfile Combinations

# In[1]:


fielddataFolder = 'FieldData'
InputFilesFolder = 'InputFiles'
debugflag = False


# In[2]:


import pandas as pd
print(f'Pandas version: {pd.__version__}')  #pandas needs to be 1.5 to be able to read the pickle file.
import matplotlib.pyplot as plt
import pvlib
import numpy as np
import os


# In[3]:


plt.rcParams.update({'font.size': 22})
plt.rcParams['figure.figsize'] = (12, 4)


# ## Read Pickle with all rows data

# This pickle is all the rows together, with data starting on 03/08 and ending on 07/29

# In[4]:


try:
    data = pd.read_pickle(os.path.join(fielddataFolder,'DATA_Release.pickle'))
except AttributeError:
    raise Exception('Error: pandas needs to be >= 1.5.0 to read this pickle file')
        
print("Clean pickle loaded for Plotting Production Data, # datapoints: ", data.__len__())
print("Spanning from", data.index[0], " to ", data.index[-1])


# In[5]:


data.keys()


# In[65]:


def saveSAM_WeatherFile(timestamps, windspeed, temp_amb, Albedo, POA=None, DHI=None, DNI=None, GHI=None, 
                        savefile='Bifacial_SAM.csv', includeminute = True):
    """
    Saves a dataframe with weather data from SRRL on SAM-friendly format.

    INPUT:
    data
    savefile
    includeminute  -- especially for hourly data, if SAM input does not have Minutes, it assuems it's TMY3 format and 
                      calculates the sun position 30 minutes prior to the hour (i.e. 12 timestamp means sun position at 11:30)
                      If minutes are included, it will calculate the sun position at the time of the timestamp (12:00 at 12:00)
                      Include minutes if resolution of data is not hourly duh. (but it will calculate at the timestamp)
                      
    Headers expected by SAM:
    ************************* 
    # Source	Location ID	City	State	Country	Latitude	Longitude	Time Zone	Elevation		

    Column names
    *************
    # Year	Month	Day	Hour	Minute	Wspd	Tdry	DHI	DNI	GHI	Albedo

    OR
    # Year	Month	Day	Hour	Wspd	Tdry	DHI	DNI	GHI	Albedo

    """

    import pandas as pd

    header = "Source,Location ID,City,State,Country,Latitude,Longitude,Time Zone,Elevation,,,,,,,,,,\n" +             "Measured,724666,DENVER/CENTENNIAL [GOLDEN - NREL],CO,USA,39.742,-105.179,-7,1829,,,,,,,,,,\n"

    savedata = pd.DataFrame({'Year':timestamps.year, 'Month':timestamps.month, 'Day':timestamps.day,
                             'Hour':timestamps.hour})
    if includeminute:
    
        savedata['Minute'] = timestamps.minute

    savedata['Wspd'] = list(windspeed.fillna(0))
    savedata['Tdry'] = list(temp_amb.fillna(20))
    
    if DHI is not None:
        savedata['DHI'] = list(DHI.fillna(0))
    
    if DNI is not None:
        savedata['DNI'] = list(DNI.fillna(0))
                            
    if GHI is not None:
        savedata['GHI'] = list(GHI.fillna(0))
    
    if POA is not None:
        savedata['POA'] = list(POA.fillna(0))
        
    if Albedo is not None:
        if type(Albedo) == pd.Series:
            #Albedo.loc[(~np.isfinite(Albedo)) & Albedo.notnull()] = np.nan
            
            Albedo = Albedo.fillna(0.99).clip(lower=0.01,upper=0.99)
        savedata['Albedo'] = list(Albedo)
        
    # reorder csv
    savedata = savedata.sort_values(by=['Month','Day','Hour'])
      
    with open(savefile, 'w', newline='') as ict:
        # Write the header lines, including the index variable for
        # the last one if you're letting Pandas produce that for you.
        # (see above).
        for line in header:
            ict.write(line)

        savedata.to_csv(ict, index=False)
   
        
def save_TMY3(datecol, timecol, windspeed, temp_amb, Albedo, POA=None, DHI=None, DNI=None, GHI=None, 
                        savefile='TMY3.csv', trackerdata=None):
    """
    NEW Routine to save TMY3 , assuming the columns Date and Time already exist and are in the right
    1-24 hour format. (this can be done previous to submitting to this function by
    reading a real CSV and joining those columns)
    
    Saves a dataframe with weathe data from SRRL in TMY3 data format.
    
    if includeTrackerData is True, it will also save the tracker data column.
    

    Headers expected by TMY3:
    ************************* 
    # Location ID	City	State	Time Zone	Latitude	Longitude	Elevation

    Column names
    *************
    # Date (MM/DD/YYYY)		Time (HH:MM)	GHI (W/m^2))	DNI (W/m^2))	DHI (W/m^2)		Wspd (m/s)	
    Dry-bulb (C)	Alb (unitless)	

    """

    import pandas as pd

    header = "724666, DENVER/CENTENNIAL [GOLDEN - NREL], CO, -7, 39.742,-105.179, 1829\n"

    savedata = pd.DataFrame({'Date (MM/DD/YYYY)':datecol,
                             'Time (HH:MM)':timecol,
                             'Wspd (m/s)':windspeed,
                             'Dry-bulb (C)':temp_amb,
                             'DHI (W/m^2)':DHI,
                             'DNI (W/m^2)':DNI,
                             'GHI (W/m^2)':GHI,
                             'Alb (unitless)':Albedo})

    if trackerdata is not None:
        savedata['Tracker Angle (degrees)'] = trackerdata

    with open(savefile, 'w', newline='') as ict:
        # Write the header lines, including the index variable for
        # the last one if you're letting Pandas produce that for you.
        # (see above).
        for line in header:
            ict.write(line)

        savedata.to_csv(ict, index=False)


# In[7]:


filterdates = (data.index >= '2021-06-01')  & (data.index < '2022-06-01') 
data2 = data[filterdates].copy()


# In[8]:


data2 = data[filterdates].resample('60T', label='left', closed='left').mean().copy()
data3 = data[filterdates].resample('60T', label='right', closed='right').mean().copy()


# In[9]:


data2.keys()


# In[66]:


# 00a - Baseline
saveSAM_WeatherFile(timestamps = data2.index, windspeed = data2.row7wind_speed, temp_amb = data2.temp_ambient_FieldAverage, 
                    Albedo = data2.sunkitty_GRI_CM22/data2.SRRL_GHI, 
                    DHI = data2.SRRL_DHI, DNI = data2.SRRL_DNI, GHI = data2.SRRL_GHI,
                    savefile = os.path.join(InputFilesFolder,'BEST_SAM_60_Comb_00a.csv'), includeminute = False)


# In[13]:


# 00b - Baseline sunkitty_albedo_IMT
saveSAM_WeatherFile(timestamps = data2.index, windspeed = data2.row7wind_speed, temp_amb = data2.temp_ambient_FieldAverage, 
                    Albedo = data2.sunkitty_albedo_IMT, 
                    DHI = data2.SRRL_DHI, DNI = data2.SRRL_DNI, GHI = data2.SRRL_GHI,
                    savefile = os.path.join(InputFilesFolder,'BEST_SAM_60_Comb_00b.csv'), includeminute = False)


# In[14]:


# 00c - Baseline sunkitty_albedo_AP
saveSAM_WeatherFile(timestamps = data2.index, windspeed = data2.row7wind_speed, temp_amb = data2.temp_ambient_FieldAverage, 
                    Albedo = data2.sunkitty_albedo_AP, 
                    DHI = data2.SRRL_DHI, DNI = data2.SRRL_DNI, GHI = data2.SRRL_GHI,
                    savefile = os.path.join(InputFilesFolder,'BEST_SAM_60_Comb_00c.csv'), includeminute = False)


# In[15]:


# 00d - Baseline SRRL_albedo
saveSAM_WeatherFile(timestamps = data2.index, windspeed = data2.row7wind_speed, temp_amb = data2.temp_ambient_FieldAverage, 
                    Albedo = data2.SRRL_albedo, 
                    DHI = data2.SRRL_DHI, DNI = data2.SRRL_DNI, GHI = data2.SRRL_GHI,
                    savefile = os.path.join(InputFilesFolder,'BEST_SAM_60_Comb_00d.csv'), includeminute = False)


# In[17]:


# 00e - Baseline Albedo = 0.22
saveSAM_WeatherFile(timestamps = data2.index, windspeed = data2.row7wind_speed, temp_amb = data2.temp_ambient_FieldAverage, 
                    Albedo = 0.22,
                    DHI = data2.SRRL_DHI, DNI = data2.SRRL_DNI, GHI = data2.SRRL_GHI,
                    savefile = os.path.join(InputFilesFolder,'BEST_SAM_60_Comb_00e.csv'), includeminute = False)


# In[27]:


## FINISH
# 00f - Baseline MONTHLY ALBEDOS
saveSAM_WeatherFile(timestamps = data2.index, windspeed = data2.row7wind_speed, temp_amb = data2.temp_ambient_FieldAverage, 
                    Albedo = data2.SRRL_albedo, 
                    DHI = data2.SRRL_DHI, DNI = data2.SRRL_DNI, GHI = data2.SRRL_GHI,
                    savefile = os.path.join(InputFilesFolder,'BEST_SAM_60_Comb_00f.csv'), includeminute = False)


# In[59]:


"""
foo2 = data2['SRRL_albedo']
foo2 = foo2.resample('1M').mean()
foo2 = foo2.resample('60T', label='left', closed='left').fillna('ffill')
foo['index'] = pd.to_datetime(data2.index)
foo['SRRL_albedo'] = (data2.groupby(foo['index'].dt.to_period('M'))['SRRL_albedo'].transform('mean'))
"""


# In[ ]:





# In[29]:


## ??? Interest NSRDB Satellite data ---> 
# 00g - Baseline SATELLITE ALBEDOS FOR A TYPICAL YEAR? 
saveSAM_WeatherFile(timestamps = data2.index, windspeed = data2.row7wind_speed, temp_amb = data2.temp_ambient_FieldAverage, 
                    Albedo = data2.SRRL_albedo, 
                    DHI = data2.SRRL_DHI, DNI = data2.SRRL_DNI, GHI = data2.SRRL_GHI,
                    savefile = os.path.join(InputFilesFolder,'BEST_SAM_60_Comb_00g.csv'), includeminute = False)


# ### 0 POA Front:

# In[30]:


# 01a - POA row5Gfront
saveSAM_WeatherFile(timestamps = data2.index, windspeed = data2.row7wind_speed, temp_amb = data2.temp_ambient_FieldAverage, 
                    Albedo = data2.sunkitty_GRI_CM22, 
                    POA = data2.row5Gfront,
                    savefile = os.path.join(InputFilesFolder,'BEST_SAM_60_Comb_01a.csv'), includeminute = False)


# In[31]:


# 01b - POA row2Gfront
saveSAM_WeatherFile(timestamps = data2.index, windspeed = data2.row7wind_speed, temp_amb = data2.temp_ambient_FieldAverage, 
                    Albedo = data2.sunkitty_GRI_CM22, 
                    POA = data2.row2Gfront,
                    savefile = os.path.join(InputFilesFolder,'BEST_SAM_60_Comb_01b.csv'), includeminute = False)


# In[32]:


# 01c - POA row3Gfront
saveSAM_WeatherFile(timestamps = data2.index, windspeed = data2.row7wind_speed, temp_amb = data2.temp_ambient_FieldAverage, 
                    Albedo = data2.sunkitty_GRI_CM22, 
                    POA = data2.row3Gfront,
                    savefile = os.path.join(InputFilesFolder,'BEST_SAM_60_Comb_01c.csv'), includeminute = False)


# In[33]:


# 01d - POA row7Gfront
saveSAM_WeatherFile(timestamps = data2.index, windspeed = data2.row7wind_speed, temp_amb = data2.temp_ambient_FieldAverage, 
                    Albedo = data2.sunkitty_GRI_CM22, 
                    POA = data2.row7Gfront,
                    savefile = os.path.join(InputFilesFolder,'BEST_SAM_60_Comb_01d.csv'), includeminute = False)


# In[34]:


# 01e - POA row9Gfront
saveSAM_WeatherFile(timestamps = data2.index, windspeed = data2.row7wind_speed, temp_amb = data2.temp_ambient_FieldAverage, 
                    Albedo = data2.sunkitty_GRI_CM22, 
                    POA = data2.row9Gfront,
                    savefile = os.path.join(InputFilesFolder,'BEST_SAM_60_Comb_01e.csv'), includeminute = False)


# In[35]:


# 01f - POA row3Gfront_CM11
saveSAM_WeatherFile(timestamps = data2.index, windspeed = data2.row7wind_speed, temp_amb = data2.temp_ambient_FieldAverage, 
                    Albedo = data2.sunkitty_GRI_CM22, 
                    POA = data2.row3Gfront_CM11,
                    savefile = os.path.join(InputFilesFolder,'BEST_SAM_60_Comb_01f.csv'), includeminute = False)


# In[36]:


# 01g - POA row3Gfront_Licor
saveSAM_WeatherFile(timestamps = data2.index, windspeed = data2.row7wind_speed, temp_amb = data2.temp_ambient_FieldAverage, 
                    Albedo = data2.sunkitty_GRI_CM22, 
                    POA = data2.row3Gfront_Licor,
                    savefile = os.path.join(InputFilesFolder,'BEST_SAM_60_Comb_01f.csv'), includeminute = False)


# ### POA Front + Rear

# In[37]:


# 02a - POA row5Gfront + data2.Grear,
saveSAM_WeatherFile(timestamps = data2.index, windspeed = data2.row7wind_speed, temp_amb = data2.temp_ambient_FieldAverage, 
                    Albedo = data2.sunkitty_GRI_CM22, 
                    POA = data2.Gfront + data2.Grear,
                    savefile = os.path.join(InputFilesFolder,'BEST_SAM_60_Comb_02a.csv'), includeminute = False)


# In[38]:


# 02b - POA row2Gfront + data2.Grear,
saveSAM_WeatherFile(timestamps = data2.index, windspeed = data2.row7wind_speed, temp_amb = data2.temp_ambient_FieldAverage, 
                    Albedo = data2.sunkitty_GRI_CM22, 
                    POA = data2.row2Gfront + data2.Grear,
                    savefile = os.path.join(InputFilesFolder,'BEST_SAM_60_Comb_02b.csv'), includeminute = False)


# In[39]:


# 02c - POA row3Gfront + data2.Grear,
saveSAM_WeatherFile(timestamps = data2.index, windspeed = data2.row7wind_speed, temp_amb = data2.temp_ambient_FieldAverage, 
                    Albedo = data2.sunkitty_GRI_CM22, 
                    POA = data2.row3Gfront + data2.Grear,
                    savefile = os.path.join(InputFilesFolder,'BEST_SAM_60_Comb_02c.csv'), includeminute = False)


# In[40]:


# 02d - POA row7Gfront + data2.Grear,
saveSAM_WeatherFile(timestamps = data2.index, windspeed = data2.row7wind_speed, temp_amb = data2.temp_ambient_FieldAverage, 
                    Albedo = data2.sunkitty_GRI_CM22, 
                    POA = data2.row7Gfront + data2.Grear,
                    savefile = os.path.join(InputFilesFolder,'BEST_SAM_60_Comb_02d.csv'), includeminute = False)


# In[41]:


# 02e - POA row9Gfront + data2.Grear,
saveSAM_WeatherFile(timestamps = data2.index, windspeed = data2.row7wind_speed, temp_amb = data2.temp_ambient_FieldAverage, 
                    Albedo = data2.sunkitty_GRI_CM22, 
                    POA = data2.row9Gfront + data2.Grear,
                    savefile = os.path.join(InputFilesFolder,'BEST_SAM_60_Comb_02e.csv'), includeminute = False)


# In[42]:


# 02f - POA row3Gfront_CM11 + data2.row3Grear_CM11,
saveSAM_WeatherFile(timestamps = data2.index, windspeed = data2.row7wind_speed, temp_amb = data2.temp_ambient_FieldAverage, 
                    Albedo = data2.sunkitty_GRI_CM22, 
                    POA = data2.row3Gfront_CM11 + data2.row3Grear_CM11,
                    savefile = os.path.join(InputFilesFolder,'BEST_SAM_60_Comb_02f.csv'), includeminute = False)


# In[43]:


# 02g - POA row3Gfront_Licor + data2.row3Grear_Licor,
saveSAM_WeatherFile(timestamps = data2.index, windspeed = data2.row7wind_speed, temp_amb = data2.temp_ambient_FieldAverage, 
                    Albedo = data2.sunkitty_GRI_CM22, 
                    POA = data2.row3Gfront_Licor + data2.row3Grear_Licor,
                    savefile = os.path.join(InputFilesFolder,'BEST_SAM_60_Comb_02f.csv'), includeminute = False)


# ### 3 POA Front + Grear single locations

# In[44]:


# 03a - POA Gfront + data2.row3Grear_IMT_West,
saveSAM_WeatherFile(timestamps = data2.index, windspeed = data2.row7wind_speed, temp_amb = data2.temp_ambient_FieldAverage, 
                    Albedo = data2.sunkitty_GRI_CM22, 
                    POA = data2.Gfront + data2.row3Grear_IMT_West,
                    savefile = os.path.join(InputFilesFolder,'BEST_SAM_60_Comb_03a.csv'), includeminute = False)


# In[45]:


# 03b - POA Gfront + data2.row3Grear_IMT_CenterWest,
saveSAM_WeatherFile(timestamps = data2.index, windspeed = data2.row7wind_speed, temp_amb = data2.temp_ambient_FieldAverage, 
                    Albedo = data2.sunkitty_GRI_CM22, 
                    POA = data2.Gfront + data2.row3Grear_IMT_CenterWest,
                    savefile = os.path.join(InputFilesFolder,'BEST_SAM_60_Comb_03b.csv'), includeminute = False)


# In[46]:


# 03c - POA Gfront + data2.row3Grear_IMT_CenterEast,
saveSAM_WeatherFile(timestamps = data2.index, windspeed = data2.row7wind_speed, temp_amb = data2.temp_ambient_FieldAverage, 
                    Albedo = data2.sunkitty_GRI_CM22, 
                    POA = data2.Gfront + data2.row3Grear_IMT_CenterEast,
                    savefile = os.path.join(InputFilesFolder,'BEST_SAM_60_Comb_03c.csv'), includeminute = False)


# In[47]:


# 03d - POA Gfront + data2.row3Grear_IMT_East,
saveSAM_WeatherFile(timestamps = data2.index, windspeed = data2.row7wind_speed, temp_amb = data2.temp_ambient_FieldAverage, 
                    Albedo = data2.sunkitty_GRI_CM22, 
                    POA = data2.Gfront + data2.row3Grear_IMT_East,
                    savefile = os.path.join(InputFilesFolder,'BEST_SAM_60_Comb_03d.csv'), includeminute = False)


# In[48]:


# 03e - POA Gfront + data2.row5Grear,
saveSAM_WeatherFile(timestamps = data2.index, windspeed = data2.row7wind_speed, temp_amb = data2.temp_ambient_FieldAverage, 
                    Albedo = data2.sunkitty_GRI_CM22, 
                    POA = data2.Gfront + data2.row5Grear,
                    savefile = os.path.join(InputFilesFolder,'BEST_SAM_60_Comb_03e.csv'), includeminute = False)


# In[49]:


# 03f - POA Gfront + data2.row7Grear_IMT_CenterEast,
saveSAM_WeatherFile(timestamps = data2.index, windspeed = data2.row7wind_speed, temp_amb = data2.temp_ambient_FieldAverage, 
                    Albedo = data2.sunkitty_GRI_CM22, 
                    POA = data2.Gfront + data2.row7Grear_IMT_CenterEast,
                    savefile = os.path.join(InputFilesFolder,'BEST_SAM_60_Comb_03f.csv'), includeminute = False)


# In[50]:


# 03g - POA Gfront + data2.row7Grear_IMT_East,
saveSAM_WeatherFile(timestamps = data2.index, windspeed = data2.row7wind_speed, temp_amb = data2.temp_ambient_FieldAverage, 
                    Albedo = data2.sunkitty_GRI_CM22, 
                    POA = data2.Gfront + data2.row7Grear_IMT_East,
                    savefile = os.path.join(InputFilesFolder,'BEST_SAM_60_Comb_03g.csv'), includeminute = False)


# In[51]:


# 03h - POA Gfront + data2.row9Grear
saveSAM_WeatherFile(timestamps = data2.index, windspeed = data2.row7wind_speed, temp_amb = data2.temp_ambient_FieldAverage, 
                    Albedo = data2.sunkitty_GRI_CM22, 
                    POA = data2.Gfront + data2.row9Grear,
                    savefile = os.path.join(InputFilesFolder,'BEST_SAM_60_Comb_03h.csv'), includeminute = False)


# ## TMY3 FORMAT

# In[52]:


real_tmy=r'Other\724010TYA.CSV'
real_tmy = pd.read_csv(real_tmy, skiprows = [0])
real_tmy = real_tmy.reset_index()


# In[53]:


data3 = data3[1:]  # removing the first 0 index
data3 = data3.reset_index()
data3['Date (MM/DD/YYYY)'] = real_tmy['Date (MM/DD/YYYY)']
data3['Time (HH:MM)'] = real_tmy['Time (HH:MM)']
#data3['Date (MM/DD/YYYY)']=data3['Date (MM/DD/YYYY)'].map(lambda x: str(x)[:-4]+dates.year)+'2021'
dates = pd.DatetimeIndex(data3['index'])
#data3['year'] = dates.year
#data3['year'] = data3['year'].apply(str)
#data3['month'] = dates.month
#data3['month'] = data3['month'].apply(str)
#data3['day'] = dates.day
#data3['day'] = data3['day'].apply(str:2)
#data3['Date (MM/DD/YYYY)'] = data3['Date (MM/DD/YYYY)'].map(lambda x: str(x)[:-4])+data3.year
#data3['Date (MM/DD/YYYY)'] = dates.strftime("%m/%d/%Y")


# In[54]:


data3['Date (MM/DD/YYYY)'] = dates.strftime("%m/%d/%Y")


# In[55]:


data3['month'] = dates.month
data3['month'] = data3['month'].apply(str)
data3['day'] = dates.day
data3['day'] = data3['day'].apply(str)


# In[56]:


data3['Date (MM/DD/YYYY)']


# In[57]:


dates.strftime("%m/%d/%Y")


# In[58]:


# 00a - Baseline

save_TMY3( datecol=data3['Date (MM/DD/YYYY)'], timecol = data3['Time (HH:MM)'], 
                   windspeed = data3.row7wind_speed, temp_amb = data3.temp_ambient_FieldAverage, 
                   Albedo = data3.sunkitty_GRI_CM22, 
                   DHI = data3.SRRL_DHI, DNI = data3.SRRL_DNI, GHI = data3.SRRL_GHI,
                   savefile='TMY3_00a.csv', trackerdata = None)


# In[ ]:




