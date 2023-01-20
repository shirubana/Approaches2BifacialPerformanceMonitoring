#!/usr/bin/env python
# coding: utf-8

# # ANALYSIS of bifacialVF by Organized Simulations
# 
# Calcualtes RMSE & MBD, relative and absolutes

# In[14]:


import pandas as pd
import os
import matplotlib.pyplot as plt
import bifacial_radiance as br      # using the MBD and RMSE functions from here
import pvlib


# In[15]:


df = pd.read_pickle('Results_bifacialVFpvlib.pkl')


# In[16]:


df.keys()


# In[19]:


orga = pd.read_excel('..\Combinations.xlsx', skiprows = 20)
orga.fillna(method='ffill')


# In[20]:


#InputFilesFolder = r'C:\Users\sayala\Documents\GitHub\Studies\Approaches2BifacialPerformanceMonitoring\InputFiles'
#weatherfile = os.path.join(InputFilesFolder,'WF_SAM_'+orga.loc[0]['WeatherFile_Name']+'.csv')


# In[21]:


fielddataFolder = '..\FieldData'

try:
    data = pd.read_pickle(os.path.join(fielddataFolder,'DATA_Release.pickle'))
except AttributeError:
    raise Exception('Error: pandas needs to be >= 1.5.0 to read this pickle file')
        
print("Clean pickle loaded for Plotting Production Data, # datapoints: ", data.__len__())
print("Spanning from", data.index[0], " to ", data.index[-1])

filterdates = (data.index >= '2021-06-01')  & (data.index < '2022-06-01') 
data = data[filterdates].resample('60T', label='left', closed='left').mean().copy()


# In[22]:


# Add other rows of calculations

# FRONT POA
#1
data['rowGfront_IMT_Average'] = data[['row3Gfront', 'row2Gfront', 'row5Gfront', 'row7Gfront', 'row9Gfront']].mean(axis=1)

# 9 --> NOTE: INCLUDED ROTATING ALBEDOMETER
data['rowGfront_ALL_Averages'] = data[['row3Gfront', 'row2Gfront', 'row3Gfront_CM11', 'row3Gfront_Licor',
                                      'row5Gfront', 'row7Gfront', 'row9Gfront', 'row7RotatingAlbedometer_CM11_Up']].mean(axis=1)

#10  --> NOTE: INCLUDED ROTATING ALBEDOMETER
data['rowGfront_Broadband_Averages'] = data[['row3Gfront_CM11', 'row3Gfront_Licor', 'row7RotatingAlbedometer_CM11_Up']].mean(axis=1)

# REAR POA

#0
data['row3Grear_IMT_Averages'] = data[['row3Grear_IMT_West', 'row3Grear_IMT_CenterWest', 
                                      'row3Grear_IMT_CenterEast', 'row3Grear_IMT_East']].mean(axis=1)

#14
data['rowGrear_IMT_Averages'] = data[['row3Grear_IMT_West', 'row3Grear_IMT_CenterWest', 
                                      'row3Grear_IMT_CenterEast', 'row3Grear_IMT_East',
                                     'row5Grear', 'row7Grear', 'row7Grear_IMT_CenterEast', 'row7Grear_IMT_East']].mean(axis=1)

#15  --> NOTE: DID NOT INCLUDE ROTATING ALBEDOMETER
data['rowGrear_ALL_Averages'] = data[['row3Grear_IMT_West', 'row3Grear_IMT_CenterWest', 
                                      'row3Grear_IMT_CenterEast', 'row3Grear_IMT_East',
                                     'row5Grear', 'row7Grear', 'row7Grear_IMT_CenterEast', 'row7Grear_IMT_East',
                                     'row3Grear_CM11', 'row3Grear_Licor']].mean(axis=1)

data['rowGrear_Broadband_Averages'] = data[['row3Grear_CM11', 'row3Grear_Licor']].mean(axis=1)


# WIND
data['rowFieldWindSpeedAverage'] = data[['row7wind_speed','row2wind_speed']].mean(axis=1)


# ALBEDO BASELINE..?

data['sunkity_CM11_GRI_over_SRRL_GHI'] = data['sunkitty_GRI_CM22'] / data['SRRL_GHI']


# In[23]:


# Some plots / sanity checks


# ## MBD RMSE stuff

# In[24]:


measfront  = data.row3Gfront
measrear  = data.row3Grear_IMT_Averages
meastemp = data.row2tmod_1


# In[26]:


df.keys()


# In[28]:


# br.performance.MBD("meas", "model")
MBD_power2 = []
MBD_power4 = []
MBD_power8 = []
MBD_power9 = []

MBD_Gfront2478 = []
MBD_Gfront4 = []
MBD_Gfront8 = []
MBD_Gfront9 = []

MBD_GrearRear249 = []
MBD_Grear4 = []
MBD_Grear9 = []

MBD_Modtemp2 = []
MBD_Modtemp4 = []
MBD_Modtemp8 = []
MBD_Modtemp9 = []

sim_all = []  

SimsM1 = orga.loc[orga['Method']==1]['Sim']

for sim in SimsM1:
    foo = df.loc[df['Sim'] == sim].set_index('datetimes').sort_index()
    modper2 = foo['Power2'].values
    modfront2478 = foo['Front2489'].values
    modrearRear249  = foo['Rear249'].values
    modtemp2  = foo['CellTemp2'].values
    
    modper4 = foo['Power4'].values
    modtemp4  = foo['CellTemp4'].values
    
    modper8 = foo['Power8'].values
    modtemp8  = foo['Power8'].values
    
    modper9 = foo['Power9'].values
    modtemp9  = foo['CellTemp9'].values

    sim_all.append(sim)

    MBD_power2.append(br.performance.MBD(data.Yf2, modper2)) 
    MBD_power4.append(br.performance.MBD(data.Yf4, modper4))
    MBD_power8.append(br.performance.MBD(data.Yf8, modper8))
    MBD_power9.append(br.performance.MBD(data.Yf9, modper9))
    
    MBD_Gfront2489.append(br.performance.MBD(measfront, modfront2478)) 

    MBD_GrearRear249.append(br.performance.MBD(measrear, modrearRear249))

    MBD_Modtemp2.append(br.performance.MBD(meastemp, modtemp2))
    MBD_Modtemp4.append(br.performance.MBD(meastemp, modtemp4))
    MBD_Modtemp8.append(br.performance.MBD(meastemp, modtemp8))
    MBD_Modtemp9.append(br.performance.MBD(meastemp, modtemp9))
    
MBD = pd.DataFrame(list(zip(sim_all, MBD_power2, MBD_power4, MBD_power8, MBD_power9,
                               MBD_Gfront2489, 
                               MBD_GrearRear249, MBD_Grear4, MBD_Grear9,
                                MBD_Modtemp2, MBD_Modtemp4, MBD_Modtemp8, MBD_Modtemp9)),
           columns = ['Sim', 'MBD_power2' , 'MBD_power4', 'MBD_power8', 'MBD_power9',
                     'MBD_Gfront2489' 
                     'MBD_GrearRear249' 
                     'MBD_Modtemp2' , 'MBD_Modtemp4', 'MBD_Modtemp8', 'MBD_Modtemp9'])


# In[ ]:


# br.performance.MBD("meas", "model")
MBD_power2 = []
MBD_power4 = []
MBD_power8 = []
MBD_power9 = []

MBD_Gfront2 = []
MBD_Gfront4 = []
MBD_Gfront8 = []
MBD_Gfront9 = []

MBD_Grear249 = []
MBD_Grear4 = []
MBD_Grear9 = []

MBD_Modtemp2 = []
MBD_Modtemp4 = []
MBD_Modtemp8 = []
MBD_Modtemp9 = []

sim_all = []  

SimsM1 = orga.loc[orga['Method']==1]['Sim']

for sim in SimsM1:
    foo = df.loc[df['Sim'] == sim].set_index('datetimes').sort_index()
    modper2 = foo['Power2'].values
    modfront2 = foo['Front2'].values
    modrear2  = foo['Rear2'].values
    modtemp2  = foo['CellTemp2'].values
    
    modper4 = foo['Power4'].values
    modfront4 = foo['Front4'].values
    modrear4  = foo['Rear4'].values
    modtemp4  = foo['CellTemp4'].values
    
    modper8 = foo['Power8'].values
    modfront8 = foo['Front8'].values
    modtemp8  = foo['CellTemp8'].values
    
    modper9 = foo['Power9'].values
    modfront9 = foo['Front9'].values
    modrear9  = foo['Rear9'].values
    modtemp9  = foo['CellTemp9'].values
    
    measfront  = data.row3Gfront
    measrear  = data.row3Grear_IMT_Averages
    meastemp = data.row2tmod_1


    sim_all.append(sim)

    MBD_power2.append(br.performance.RMSE(data.Yf2, modper2)) 
    MBD_power4.append(br.performance.RMSE(data.Yf4, modper4))
    MBD_power8.append(br.performance.RMSE(data.Yf8, modper8))
    MBD_power9.append(br.performance.RMSE(data.Yf9, modper9))
    
    MBD_Gfront2.append(br.performance.RMSE(measfront, modfront2)) 
    MBD_Gfront4.append(br.performance.RMSE(measfront, modfront4))
    MBD_Gfront8.append(br.performance.RMSE(measfront, modfront8))
    MBD_Gfront9.append(br.performance.RMSE(measfront, modfront9))

    MBD_Grear2.append(br.performance.RMSE(measrear, modrear2))
    MBD_Grear4.append(br.performance.RMSE(measrear, modrear4))
    MBD_Grear9.append(br.performance.RMSE(measrear, modrear9))

    MBD_Modtemp2.append(br.performance.RMSE(meastemp, modtemp2))
    MBD_Modtemp4.append(br.performance.RMSE(meastemp, modtemp4))
    MBD_Modtemp8.append(br.performance.RMSE(meastemp, modtemp8))
    MBD_Modtemp9.append(br.performance.RMSE(meastemp, modtemp9))

RMSE = pd.DataFrame(list(zip(sim_all, MBD_power2, MBD_power4, MBD_power8, MBD_power9,
                               MBD_Gfront2, MBD_Gfront4, MBD_Gfront8, MBD_Gfront9,
                               MBD_Grear2, MBD_Grear4, MBD_Grear9,
                                MBD_Modtemp2, MBD_Modtemp4, MBD_Modtemp8, MBD_Modtemp9)),
           columns = ['Sim', 'RMSE_power2' , 'RMSE_power4', 'RMSE_power8', 'RMSE_power9',
                     'RMSE_Gfront2' , 'RMSE_Gfront4', 'RMSE_Gfront8', 'RMSE_Gfront9',
                     'RMSE_Grear2' , 'RMSE_Grear4', 'RMSE_Grear9',
                     'RMSE_Modtemp2' , 'RMSE_Modtemp4', 'RMSE_Modtemp8', 'RMSE_Modtemp9'])


# In[ ]:


# br.performance.MBD("meas", "model")
MBD_power2 = []
MBD_power4 = []
MBD_power8 = []
MBD_power9 = []

MBD_Gfront2 = []
MBD_Gfront4 = []
MBD_Gfront8 = []
MBD_Gfront9 = []

MBD_Grear2 = []
MBD_Grear4 = []
MBD_Grear9 = []

MBD_Modtemp2 = []
MBD_Modtemp4 = []
MBD_Modtemp8 = []
MBD_Modtemp9 = []

sim_all = []  

SimsM1 = orga.loc[orga['Method']==1]['Sim']

for sim in SimsM1:
    foo = df.loc[df['Sim'] == sim].set_index('datetimes').sort_index()
    modper2 = foo['Power2'].values
    modfront2 = foo['Front2'].values
    modrear2  = foo['Rear2'].values
    modtemp2  = foo['CellTemp2'].values
    
    modper4 = foo['Power4'].values
    modfront4 = foo['Front4'].values
    modrear4  = foo['Rear4'].values
    modtemp4  = foo['CellTemp4'].values
    
    modper8 = foo['Power8'].values
    modfront8 = foo['Front8'].values
    modtemp8  = foo['CellTemp8'].values
    
    modper9 = foo['Power9'].values
    modfront9 = foo['Front9'].values
    modrear9  = foo['Rear9'].values
    modtemp9  = foo['CellTemp9'].values
    
    measfront  = data.row3Gfront
    measrear  = data.row3Grear_IMT_Averages
    meastemp = data.row2tmod_1


    sim_all.append(sim)

    MBD_power2.append(br.performance.MBD_abs(data.Yf2, modper2)) 
    MBD_power4.append(br.performance.MBD_abs(data.Yf4, modper4))
    MBD_power8.append(br.performance.MBD_abs(data.Yf8, modper8))
    MBD_power9.append(br.performance.MBD_abs(data.Yf9, modper9))
    
    MBD_Gfront2.append(br.performance.MBD_abs(measfront, modfront2)) 
    MBD_Gfront4.append(br.performance.MBD_abs(measfront, modfront4))
    MBD_Gfront8.append(br.performance.MBD_abs(measfront, modfront8))
    MBD_Gfront9.append(br.performance.MBD_abs(measfront, modfront9))

    MBD_Grear2.append(br.performance.MBD_abs(measrear, modrear2))
    MBD_Grear4.append(br.performance.MBD_abs(measrear, modrear4))
    MBD_Grear9.append(br.performance.MBD_abs(measrear, modrear9))

    MBD_Modtemp2.append(br.performance.MBD_abs(meastemp, modtemp2))
    MBD_Modtemp4.append(br.performance.MBD_abs(meastemp, modtemp4))
    MBD_Modtemp8.append(br.performance.MBD_abs(meastemp, modtemp8))
    MBD_Modtemp9.append(br.performance.MBD_abs(meastemp, modtemp9))

MBD_abs = pd.DataFrame(list(zip(sim_all, MBD_power2, MBD_power4, MBD_power8, MBD_power9,
                               MBD_Gfront2, MBD_Gfront4, MBD_Gfront8, MBD_Gfront9,
                               MBD_Grear2, MBD_Grear4, MBD_Grear9,
                                MBD_Modtemp2, MBD_Modtemp4, MBD_Modtemp8, MBD_Modtemp9)),
           columns = ['Sim', 'MBD_abs_power2' , 'MBD_abs_power4', 'MBD_abs_power8', 'MBD_abs_power9',
                     'MBD_abs_Gfront2' , 'MBD_abs_Gfront4', 'MBD_abs_Gfront8', 'MBD_abs_Gfront9',
                     'MBD_abs_Grear2' , 'MBD_abs_Grear4', 'MBD_abs_Grear9',
                     'MBD_abs_Modtemp2' , 'MBD_abs_Modtemp4', 'MBD_abs_Modtemp8', 'MBD_abs_Modtemp9'])


# In[ ]:


# br.performance.MBD("meas", "model")
MBD_power2 = []
MBD_power4 = []
MBD_power8 = []
MBD_power9 = []

MBD_Gfront2 = []
MBD_Gfront4 = []
MBD_Gfront8 = []
MBD_Gfront9 = []

MBD_Grear2 = []
MBD_Grear4 = []
MBD_Grear9 = []

MBD_Modtemp2 = []
MBD_Modtemp4 = []
MBD_Modtemp8 = []
MBD_Modtemp9 = []

sim_all = []  

SimsM1 = orga.loc[orga['Method']==1]['Sim']

for sim in SimsM1:
    foo = df.loc[df['Sim'] == sim].set_index('datetimes').sort_index()
    modper2 = foo['Power2'].values
    modfront2 = foo['Front2'].values
    modrear2  = foo['Rear2'].values
    modtemp2  = foo['CellTemp2'].values
    
    modper4 = foo['Power4'].values
    modfront4 = foo['Front4'].values
    modrear4  = foo['Rear4'].values
    modtemp4  = foo['CellTemp4'].values
    
    modper8 = foo['Power8'].values
    modfront8 = foo['Front8'].values
    modtemp8  = foo['CellTemp8'].values
    
    modper9 = foo['Power9'].values
    modfront9 = foo['Front9'].values
    modrear9  = foo['Rear9'].values
    modtemp9  = foo['CellTemp9'].values
    
    measfront  = data.row3Gfront
    measrear  = data.row3Grear_IMT_Averages
    meastemp = data.row2tmod_1


    sim_all.append(sim)

    MBD_power2.append(br.performance.RMSE_abs(data.Yf2, modper2)) 
    MBD_power4.append(br.performance.RMSE_abs(data.Yf4, modper4))
    MBD_power8.append(br.performance.RMSE_abs(data.Yf8, modper8))
    MBD_power9.append(br.performance.RMSE_abs(data.Yf9, modper9))
    
    MBD_Gfront2.append(br.performance.RMSE_abs(measfront, modfront2)) 
    MBD_Gfront4.append(br.performance.RMSE_abs(measfront, modfront4))
    MBD_Gfront8.append(br.performance.RMSE_abs(measfront, modfront8))
    MBD_Gfront9.append(br.performance.RMSE_abs(measfront, modfront9))

    MBD_Grear2.append(br.performance.RMSE_abs(measrear, modrear2))
    MBD_Grear4.append(br.performance.RMSE_abs(measrear, modrear4))
    MBD_Grear9.append(br.performance.RMSE_abs(measrear, modrear9))

    MBD_Modtemp2.append(br.performance.RMSE_abs(meastemp, modtemp2))
    MBD_Modtemp4.append(br.performance.RMSE_abs(meastemp, modtemp4))
    MBD_Modtemp8.append(br.performance.RMSE_abs(meastemp, modtemp8))
    MBD_Modtemp9.append(br.performance.RMSE_abs(meastemp, modtemp9))

RMSE_abs = pd.DataFrame(list(zip(sim_all, MBD_power2, MBD_power4, MBD_power8, MBD_power9,
                               MBD_Gfront2, MBD_Gfront4, MBD_Gfront8, MBD_Gfront9,
                               MBD_Grear2, MBD_Grear4, MBD_Grear9,
                                MBD_Modtemp2, MBD_Modtemp4, MBD_Modtemp8, MBD_Modtemp9)),
           columns = ['Sim', 'RMSE_abs_power2' , 'RMSE_abs_power4', 'RMSE_abs_power8', 'RMSE_abs_power9',
                     'RMSE_abs_Gfront2' , 'RMSE_abs_Gfront4', 'RMSE_abs_Gfront8', 'RMSE_abs_Gfront9',
                     'RMSE_abs_Grear2' , 'RMSE_abs_Grear4', 'RMSE_abs_Grear9',
                     'RMSE_abs_Modtemp2' , 'RMSE_abs_Modtemp4', 'RMSE_abs_Modtemp8', 'RMSE_abs_Modtemp9'])


# In[ ]:


RMSE.to_csv('RMSE.csv')
RMSE_abs.to_csv('RMSE_abs.csv')
MBD.to_csv('MBD.csv')
MBD_abs.to_csv('MBD_abs.csv')


# In[ ]:


RMSE


# In[ ]:


RMSE_abs


# In[ ]:


data.keys()


# In[ ]:


df['Sim'].unique()


# In[ ]:


df.keys()


# In[ ]:


foo = df.loc[df['Sim'] == 'P00'].set_index('datetimes').sort_index()

plt.plot(data.row3Gfront.iloc[100:200], label='meas')
plt.plot(foo['Front2'].iloc[100:200], '.',label='model')
plt.legend()


# In[ ]:


len(data)


# In[ ]:


foo = df.loc[df['Sim'] == '00'].set_index('datetimes').sort_index()

plt.plot(data.Yf4.iloc[8590:8760], label='meas')
plt.plot(foo['Power4'].iloc[8590:8760], '.',label='model')
plt.legend()


# In[ ]:


foo.keys()


# In[ ]:


foo = df.loc[df['Sim'] == 'P03'].set_index('datetimes').sort_index()

plt.plot(data.Yf4.iloc[0:100], label='meas')
plt.plot(foo['Power9'].iloc[0:100], '.',label='model')
plt.legend()


# In[ ]:


foo = df.loc[df['Sim'] == '00'].set_index('datetimes').sort_index()

plt.plot(data.Yf4.iloc[100:200], label='meas')
plt.plot(foo['Power4'].iloc[100:200], '.',label='model')
plt.legend()


# In[ ]:


foo = df.loc[df['Sim'] == '00'].set_index('datetimes').sort_index()

plt.plot(data.Yf4.values, label='meas')
plt.plot(foo['Power4'].values, label='model')
plt.legend()


# In[ ]:


foo = df.loc[df['Sim'] == '00'].set_index('datetimes').sort_index()

plt.plot(foo['Power9'].values, label='model')
plt.plot(data.Yf9.values, label='meas')
plt.legend()


# In[ ]:


foo = df.loc[df['Sim'] == '00'].set_index('datetimes').sort_index()

plt.plot(data.Yf2.values, foo['Power2'].values, '.', alpha=0.1)
plt.xlabel('Measured')
plt.ylabel('Model')
plt.xlim([0, 1.2])
plt.title('Row 2 Power')

plt. figure()
plt.plot(data.Yf4.values, foo['Power4'].values, '.', alpha=0.1)
plt.xlabel('Measured')
plt.ylabel('Model')
plt.xlim([0, 1.2])
plt.title('Row 4 Power')

plt. figure()
plt.plot(data.Yf8.values, foo['Power8'].values, '.', alpha=0.1)
plt.xlabel('Measured')
plt.ylabel('Model')
plt.xlim([0, 1.2])
plt.title('Row 8 Power')

plt. figure()
plt.plot(data.Yf9.values, foo['Power9'].values, '.', alpha=0.1)
plt.xlabel('Measured')
plt.ylabel('Model')
plt.xlim([0, 1.2])
plt.title('Row 9 Power')


# In[ ]:




