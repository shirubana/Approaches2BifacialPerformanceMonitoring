#!/usr/bin/env python
# coding: utf-8

# # 1 - Generating Inputfile Combinations

# In[1]:


fielddataFolder = 'FieldData'
InputFilesFolder = 'InputFiles'
debugflag = False


# In[2]:


import pandas as pd
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


data = pd.read_pickle(os.path.join(fielddataFolder,'DATA_Release.pickle'))
print("Clean pickle loaded for Plotting Production Data, # datapoints: ", data.__len__())
print("Spanning from", data.index[0], " to ", data.index[-1])


# In[5]:


data.keys()


# In[6]:


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

    windspeed = list(windspeed)
    temp_amb = list(temp_amb)
    savedata['Wspd'] = windspeed
    savedata['Tdry'] = temp_amb
    
    if DHI is not None:
        DHI = list(DHI)
        savedata['DHI'] = DHI
    
    if DNI is not None:
        DNI = list(DNI)
        savedata['DNI'] = DNI
                            
    if GHI is not None:
        GHI = list(GHI)
        savedata['GHI'] = GHI
    
    if POA is not None:
        POA = list(POA)
        savedata['POA'] = POA
        
    if Albedo is not None:
        Albedo = list(Albedo)
        savedata['Albedo'] = Albedo
      
    with open(savefile, 'w', newline='') as ict:
        # Write the header lines, including the index variable for
        # the last one if you're letting Pandas produce that for you.
        # (see above).
        for line in header:
            ict.write(line)

        savedata.to_csv(ict, index=False)

        
def save_TMY3(srrl15, savefile='Bifacial_TMYfileAll2019_15.csv', includeTrackerData=False):
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

    savedata = pd.DataFrame({'Date (MM/DD/YYYY)':srrl15['Date (MM/DD/YYYY)'],
                             'Time (HH:MM)':srrl15['Time (HH:MM)'],
                             'Wspd (m/s)':srrl15['Avg Wind Speed @ 6ft [m/s]'],
                             'Dry-bulb (C)':srrl15['Tower Dry Bulb Temp [deg C]'],
                             'DHI (W/m^2)':srrl15['Diffuse 8-48 (vent) [W/m^2]'],
                             'DNI (W/m^2)':srrl15['Direct CHP1-1 [W/m^2]'],
                             'GHI (W/m^2)':srrl15['Global CMP22 (vent/cor) [W/m^2]'],
                             'Alb (unitless)':srrl15['Albedo (CMP11)']})

    if includeTrackerData:
        savedata['Tracker Angle (degrees)'] = srrl15['Tracker Angle (degrees)']

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


# In[9]:


data2.keys()


# In[10]:


# 00a - Baseline
saveSAM_WeatherFile(timestamps = data2.index, windspeed = data2.row7wind_speed, temp_amb = data2.temp_ambient_FieldAverage, 
                    Albedo = data2.sunkitty_GRI_CM22, 
                    DHI = data2.SRRL_DHI, DNI = data2.SRRL_DNI, GHI = data2.SRRL_GHI,
                    savefile = 'BEST_SAM_60_Comb_00a.csv', includeminute = False)


# In[11]:


# 00b - Baseline sunkitty_albedo_IMT
saveSAM_WeatherFile(timestamps = data2.index, windspeed = data2.row7wind_speed, temp_amb = data2.temp_ambient_FieldAverage, 
                    Albedo = data2.sunkitty_albedo_IMT, 
                    DHI = data2.SRRL_DHI, DNI = data2.SRRL_DNI, GHI = data2.SRRL_GHI,
                    savefile = 'BEST_SAM_60_Comb_00b.csv', includeminute = False)


# In[12]:


# 00c - Baseline sunkitty_albedo_AP
saveSAM_WeatherFile(timestamps = data2.index, windspeed = data2.row7wind_speed, temp_amb = data2.temp_ambient_FieldAverage, 
                    Albedo = data2.sunkitty_albedo_AP, 
                    DHI = data2.SRRL_DHI, DNI = data2.SRRL_DNI, GHI = data2.SRRL_GHI,
                    savefile = 'BEST_SAM_60_Comb_00c.csv', includeminute = False)


# In[13]:


# 00d - Baseline SRRL_albedo
saveSAM_WeatherFile(timestamps = data2.index, windspeed = data2.row7wind_speed, temp_amb = data2.temp_ambient_FieldAverage, 
                    Albedo = data2.SRRL_albedo, 
                    DHI = data2.SRRL_DHI, DNI = data2.SRRL_DNI, GHI = data2.SRRL_GHI,
                    savefile = 'BEST_SAM_60_Comb_00d.csv', includeminute = False)


# In[ ]:


# 00e - Baseline Albedo = 0.22
saveSAM_WeatherFile(timestamps = data2.index, windspeed = data2.row7wind_speed, temp_amb = data2.temp_ambient_FieldAverage, 
                    Albedo = 0.22,
                    DHI = data2.SRRL_DHI, DNI = data2.SRRL_DNI, GHI = data2.SRRL_GHI,
                    savefile = 'BEST_SAM_60_Comb_00e.csv', includeminute = False)


# In[ ]:


## FINISH
# 00f - Baseline MONTHLY ALBEDOS
saveSAM_WeatherFile(timestamps = data2.index, windspeed = data2.row7wind_speed, temp_amb = data2.temp_ambient_FieldAverage, 
                    Albedo = data2.SRRL_albedo, 
                    DHI = data2.SRRL_DHI, DNI = data2.SRRL_DNI, GHI = data2.SRRL_GHI,
                    savefile = 'BEST_SAM_60_Comb_00f.csv', includeminute = False)


# In[16]:


foo2 = data2['SRRL_albedo']
foo2 = foo2.resample('1M').mean()
foo2 = foo2.resample('60T', label='left', closed='left').fillna('ffill')
foo['index'] = pd.to_datetime(data2.index)
foo['SRRL_albedo'] = (data2.groupby(foo['index'].dt.to_period('M'))['SRRL_albedo'].transform('mean'))


# In[ ]:





# In[ ]:


## ??? Interest NSRDB Satellite data ---> 
# 00g - Baseline SATELLITE ALBEDOS FOR A TYPICAL YEAR? 
saveSAM_WeatherFile(timestamps = data2.index, windspeed = data2.row7wind_speed, temp_amb = data2.temp_ambient_FieldAverage, 
                    Albedo = data2.SRRL_albedo, 
                    DHI = data2.SRRL_DHI, DNI = data2.SRRL_DNI, GHI = data2.SRRL_GHI,
                    savefile = 'BEST_SAM_60_Comb_00g.csv', includeminute = False)


# ### 0 POA Front:

# In[18]:


# 01a - POA row5Gfront
saveSAM_WeatherFile(timestamps = data2.index, windspeed = data2.row7wind_speed, temp_amb = data2.temp_ambient_FieldAverage, 
                    Albedo = data2.sunkitty_GRI_CM22, 
                    POA = data2.row5Gfront,
                    savefile = 'BEST_SAM_60_Comb_01a.csv', includeminute = False)


# In[19]:


# 01b - POA row2Gfront
saveSAM_WeatherFile(timestamps = data2.index, windspeed = data2.row7wind_speed, temp_amb = data2.temp_ambient_FieldAverage, 
                    Albedo = data2.sunkitty_GRI_CM22, 
                    POA = data2.row2Gfront,
                    savefile = 'BEST_SAM_60_Comb_01b.csv', includeminute = False)


# In[20]:


# 01c - POA row3Gfront
saveSAM_WeatherFile(timestamps = data2.index, windspeed = data2.row7wind_speed, temp_amb = data2.temp_ambient_FieldAverage, 
                    Albedo = data2.sunkitty_GRI_CM22, 
                    POA = data2.row3Gfront,
                    savefile = 'BEST_SAM_60_Comb_01c.csv', includeminute = False)


# In[21]:


# 01d - POA row7Gfront
saveSAM_WeatherFile(timestamps = data2.index, windspeed = data2.row7wind_speed, temp_amb = data2.temp_ambient_FieldAverage, 
                    Albedo = data2.sunkitty_GRI_CM22, 
                    POA = data2.row7Gfront,
                    savefile = 'BEST_SAM_60_Comb_01d.csv', includeminute = False)


# In[22]:


# 01e - POA row9Gfront
saveSAM_WeatherFile(timestamps = data2.index, windspeed = data2.row7wind_speed, temp_amb = data2.temp_ambient_FieldAverage, 
                    Albedo = data2.sunkitty_GRI_CM22, 
                    POA = data2.row9Gfront,
                    savefile = 'BEST_SAM_60_Comb_01e.csv', includeminute = False)


# In[23]:


# 01f - POA row3Gfront_CM11
saveSAM_WeatherFile(timestamps = data2.index, windspeed = data2.row7wind_speed, temp_amb = data2.temp_ambient_FieldAverage, 
                    Albedo = data2.sunkitty_GRI_CM22, 
                    POA = data2.row3Gfront_CM11,
                    savefile = 'BEST_SAM_60_Comb_01f.csv', includeminute = False)


# In[24]:


# 01g - POA row3Gfront_Licor
saveSAM_WeatherFile(timestamps = data2.index, windspeed = data2.row7wind_speed, temp_amb = data2.temp_ambient_FieldAverage, 
                    Albedo = data2.sunkitty_GRI_CM22, 
                    POA = data2.row3Gfront_Licor,
                    savefile = 'BEST_SAM_60_Comb_01f.csv', includeminute = False)


# ### POA Front + Rear

# In[25]:


# 02a - POA row5Gfront + data2.Grear,
saveSAM_WeatherFile(timestamps = data2.index, windspeed = data2.row7wind_speed, temp_amb = data2.temp_ambient_FieldAverage, 
                    Albedo = data2.sunkitty_GRI_CM22, 
                    POA = data2.Gfront + data2.Grear,
                    savefile = 'BEST_SAM_60_Comb_02a.csv', includeminute = False)


# In[26]:


# 02b - POA row2Gfront + data2.Grear,
saveSAM_WeatherFile(timestamps = data2.index, windspeed = data2.row7wind_speed, temp_amb = data2.temp_ambient_FieldAverage, 
                    Albedo = data2.sunkitty_GRI_CM22, 
                    POA = data2.row2Gfront + data2.Grear,
                    savefile = 'BEST_SAM_60_Comb_02b.csv', includeminute = False)


# In[27]:


# 02c - POA row3Gfront + data2.Grear,
saveSAM_WeatherFile(timestamps = data2.index, windspeed = data2.row7wind_speed, temp_amb = data2.temp_ambient_FieldAverage, 
                    Albedo = data2.sunkitty_GRI_CM22, 
                    POA = data2.row3Gfront + data2.Grear,
                    savefile = 'BEST_SAM_60_Comb_02c.csv', includeminute = False)


# In[28]:


# 02d - POA row7Gfront + data2.Grear,
saveSAM_WeatherFile(timestamps = data2.index, windspeed = data2.row7wind_speed, temp_amb = data2.temp_ambient_FieldAverage, 
                    Albedo = data2.sunkitty_GRI_CM22, 
                    POA = data2.row7Gfront + data2.Grear,
                    savefile = 'BEST_SAM_60_Comb_02d.csv', includeminute = False)


# In[29]:


# 02e - POA row9Gfront + data2.Grear,
saveSAM_WeatherFile(timestamps = data2.index, windspeed = data2.row7wind_speed, temp_amb = data2.temp_ambient_FieldAverage, 
                    Albedo = data2.sunkitty_GRI_CM22, 
                    POA = data2.row9Gfront + data2.Grear,
                    savefile = 'BEST_SAM_60_Comb_02e.csv', includeminute = False)


# In[30]:


# 02f - POA row3Gfront_CM11 + data2.row3Grear_CM11,
saveSAM_WeatherFile(timestamps = data2.index, windspeed = data2.row7wind_speed, temp_amb = data2.temp_ambient_FieldAverage, 
                    Albedo = data2.sunkitty_GRI_CM22, 
                    POA = data2.row3Gfront_CM11 + data2.row3Grear_CM11,
                    savefile = 'BEST_SAM_60_Comb_02f.csv', includeminute = False)


# In[31]:


# 02g - POA row3Gfront_Licor + data2.row3Grear_Licor,
saveSAM_WeatherFile(timestamps = data2.index, windspeed = data2.row7wind_speed, temp_amb = data2.temp_ambient_FieldAverage, 
                    Albedo = data2.sunkitty_GRI_CM22, 
                    POA = data2.row3Gfront_Licor + data2.row3Grear_Licor,
                    savefile = 'BEST_SAM_60_Comb_02f.csv', includeminute = False)


# ### 3 POA Front + Grear single locations

# In[32]:


# 03a - POA Gfront + data2.row3Grear_IMT_West,
saveSAM_WeatherFile(timestamps = data2.index, windspeed = data2.row7wind_speed, temp_amb = data2.temp_ambient_FieldAverage, 
                    Albedo = data2.sunkitty_GRI_CM22, 
                    POA = data2.Gfront + data2.row3Grear_IMT_West,
                    savefile = 'BEST_SAM_60_Comb_03a.csv', includeminute = False)


# In[33]:


# 03b - POA Gfront + data2.row3Grear_IMT_CenterWest,
saveSAM_WeatherFile(timestamps = data2.index, windspeed = data2.row7wind_speed, temp_amb = data2.temp_ambient_FieldAverage, 
                    Albedo = data2.sunkitty_GRI_CM22, 
                    POA = data2.Gfront + data2.row3Grear_IMT_CenterWest,
                    savefile = 'BEST_SAM_60_Comb_03b.csv', includeminute = False)


# In[34]:


# 03c - POA Gfront + data2.row3Grear_IMT_CenterEast,
saveSAM_WeatherFile(timestamps = data2.index, windspeed = data2.row7wind_speed, temp_amb = data2.temp_ambient_FieldAverage, 
                    Albedo = data2.sunkitty_GRI_CM22, 
                    POA = data2.Gfront + data2.row3Grear_IMT_CenterEast,
                    savefile = 'BEST_SAM_60_Comb_03c.csv', includeminute = False)


# In[35]:


# 03d - POA Gfront + data2.row3Grear_IMT_East,
saveSAM_WeatherFile(timestamps = data2.index, windspeed = data2.row7wind_speed, temp_amb = data2.temp_ambient_FieldAverage, 
                    Albedo = data2.sunkitty_GRI_CM22, 
                    POA = data2.Gfront + data2.row3Grear_IMT_East,
                    savefile = 'BEST_SAM_60_Comb_03d.csv', includeminute = False)


# In[36]:


# 03e - POA Gfront + data2.row5Grear,
saveSAM_WeatherFile(timestamps = data2.index, windspeed = data2.row7wind_speed, temp_amb = data2.temp_ambient_FieldAverage, 
                    Albedo = data2.sunkitty_GRI_CM22, 
                    POA = data2.Gfront + data2.row5Grear,
                    savefile = 'BEST_SAM_60_Comb_03e.csv', includeminute = False)


# In[37]:


# 03f - POA Gfront + data2.row7Grear_IMT_CenterEast,
saveSAM_WeatherFile(timestamps = data2.index, windspeed = data2.row7wind_speed, temp_amb = data2.temp_ambient_FieldAverage, 
                    Albedo = data2.sunkitty_GRI_CM22, 
                    POA = data2.Gfront + data2.row7Grear_IMT_CenterEast,
                    savefile = 'BEST_SAM_60_Comb_03f.csv', includeminute = False)


# In[38]:


# 03g - POA Gfront + data2.row7Grear_IMT_East,
saveSAM_WeatherFile(timestamps = data2.index, windspeed = data2.row7wind_speed, temp_amb = data2.temp_ambient_FieldAverage, 
                    Albedo = data2.sunkitty_GRI_CM22, 
                    POA = data2.Gfront + data2.row7Grear_IMT_East,
                    savefile = 'BEST_SAM_60_Comb_03g.csv', includeminute = False)


# In[39]:


# 03h - POA Gfront + data2.row9Grear
saveSAM_WeatherFile(timestamps = data2.index, windspeed = data2.row7wind_speed, temp_amb = data2.temp_ambient_FieldAverage, 
                    Albedo = data2.sunkitty_GRI_CM22, 
                    POA = data2.Gfront + data2.row9Grear,
                    savefile = 'BEST_SAM_60_Comb_03h.csv', includeminute = False)


# In[ ]:




