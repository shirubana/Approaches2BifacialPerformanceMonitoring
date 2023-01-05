#!/usr/bin/env python
# coding: utf-8

# # ANALYSIS of pySAM by Organized Simulations
# 
# Calcualtes RMSE & MBD, relative and absolutes

# In[12]:


import pandas as pd
import os
import matplotlib.pyplot as plt
import bifacial_radiance as br      # using the MBD and RMSE functions from here
import pvlib


# In[13]:


df = pd.read_pickle('Results_pysam.pkl')


# In[14]:


orga = pd.read_excel('..\Combinations.xlsx', skiprows = 20)
orga.fillna(method='ffill')


# In[15]:


#InputFilesFolder = r'C:\Users\sayala\Documents\GitHub\Studies\Approaches2BifacialPerformanceMonitoring\InputFiles'
#weatherfile = os.path.join(InputFilesFolder,'WF_SAM_'+orga.loc[0]['WeatherFile_Name']+'.csv')


# In[17]:


fielddataFolder = '..\FieldData'

try:
    data = pd.read_pickle(os.path.join(fielddataFolder,'DATA_Release.pickle'))
except AttributeError:
    raise Exception('Error: pandas needs to be >= 1.5.0 to read this pickle file')
        
print("Clean pickle loaded for Plotting Production Data, # datapoints: ", data.__len__())
print("Spanning from", data.index[0], " to ", data.index[-1])

filterdates = (data.index >= '2021-06-01')  & (data.index < '2022-06-01') 
data = data[filterdates].resample('60T', label='left', closed='left').mean().copy()


# In[18]:


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


# In[19]:


# Some plots / sanity checks


# In[ ]:





# ## MBD RMSE stuff

# In[34]:


measfront  = data.row3Gfront
measrear  = data.row3Grear_IMT_Averages
meastemp = data.row2tmod_1


# In[42]:


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
    modtemp8  = foo['Power8'].values
    
    modper9 = foo['Power9'].values
    modfront9 = foo['Front9'].values
    modrear9  = foo['Rear9'].values
    modtemp9  = foo['CellTemp9'].values

    sim_all.append(sim)

    MBD_power2.append(br.performance.MBD(data.Yf2, modper2)) 
    MBD_power4.append(br.performance.MBD(data.Yf4, modper4))
    MBD_power8.append(br.performance.MBD(data.Yf8, modper8))
    MBD_power9.append(br.performance.MBD(data.Yf9, modper9))
    
    MBD_Gfront2.append(br.performance.MBD(measfront, modfront2)) 
    MBD_Gfront4.append(br.performance.MBD(measfront, modfront4))
    MBD_Gfront8.append(br.performance.MBD(measfront, modfront8))
    MBD_Gfront9.append(br.performance.MBD(measfront, modfront9))

    MBD_Grear2.append(br.performance.MBD(measrear, modrear2))
    MBD_Grear4.append(br.performance.MBD(measrear, modrear4))
    MBD_Grear9.append(br.performance.MBD(measrear, modrear9))

    MBD_Modtemp2.append(br.performance.MBD(meastemp, modtemp2))
    MBD_Modtemp4.append(br.performance.MBD(meastemp, modtemp4))
    MBD_Modtemp8.append(br.performance.MBD(meastemp, modtemp8))
    MBD_Modtemp9.append(br.performance.MBD(meastemp, modtemp9))
    
MBDres = pd.DataFrame(list(zip(sim_all, MBD_power2, MBD_power4, MBD_power8, MBD_power9,
                               MBD_Gfront2, MBD_Gfront4, MBD_Gfront8, MBD_Gfront9,
                               MBD_Grear2, MBD_Grear4, MBD_Grear9,
                                MBD_Modtemp2, MBD_Modtemp4, MBD_Modtemp8, MBD_Modtemp9)),
           columns = ['Sim', 'MBD_power2' , 'MBD_power4', 'MBD_power8', 'MBD_power9',
                     'MBD_Gfront2' , 'MBD_Gfront4', 'MBD_Gfront8', 'MBD_Gfront9',
                     'MBD_Grear2' , 'MBD_Grear4', 'MBD_Grear9',
                     'MBD_Modtemp2' , 'MBD_Modtemp4', 'MBD_Modtemp8', 'MBD_Modtemp9'])


# In[43]:


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
           columns = ['Sim', 'MBD_power2' , 'MBD_power4', 'MBD_power8', 'MBD_power9',
                     'MBD_Gfront2' , 'MBD_Gfront4', 'MBD_Gfront8', 'MBD_Gfront9',
                     'MBD_Grear2' , 'MBD_Grear4', 'MBD_Grear9',
                     'MBD_Modtemp2' , 'MBD_Modtemp4', 'MBD_Modtemp8', 'MBD_Modtemp9'])


# In[44]:


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
           columns = ['Sim', 'MBD_power2' , 'MBD_power4', 'MBD_power8', 'MBD_power9',
                     'MBD_Gfront2' , 'MBD_Gfront4', 'MBD_Gfront8', 'MBD_Gfront9',
                     'MBD_Grear2' , 'MBD_Grear4', 'MBD_Grear9',
                     'MBD_Modtemp2' , 'MBD_Modtemp4', 'MBD_Modtemp8', 'MBD_Modtemp9'])


# In[45]:


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
           columns = ['Sim', 'MBD_power2' , 'MBD_power4', 'MBD_power8', 'MBD_power9',
                     'MBD_Gfront2' , 'MBD_Gfront4', 'MBD_Gfront8', 'MBD_Gfront9',
                     'MBD_Grear2' , 'MBD_Grear4', 'MBD_Grear9',
                     'MBD_Modtemp2' , 'MBD_Modtemp4', 'MBD_Modtemp8', 'MBD_Modtemp9'])


# In[46]:


RMSE_abs
MBDres
MBD_abs
RMSE
RMSE_abs


# In[47]:


RMSE


# In[48]:


data.keys()


# In[49]:


df['Sim'].unique()


# In[50]:


df.keys()


# In[68]:


foo = df.loc[df['Sim'] == 'P00'].set_index('datetimes').sort_index()

plt.plot(data.row3Gfront.iloc[100:200], label='meas')
plt.plot(foo['Front2'].iloc[100:200], '.',label='model')
plt.legend()


# In[89]:


foo = df.loc[df['Sim'] == 'P00'].set_index('datetimes').sort_index()

plt.plot(data.row3Gfront.iloc[100:200], label='meas')
plt.plot(foo['Front2'].iloc[100:200], '.',label='model')
plt.legend()


# In[83]:


foo.keys()


# In[91]:


df.loc[df['Sim'] == 'P00']['Front4'].head(14)


# In[85]:


foo = df.loc[df['Sim'] == 'P03'].set_index('datetimes').sort_index()

plt.plot(data.Yf4.iloc[0:100], label='meas')
plt.plot(foo['Power9'].iloc[0:100], '.',label='model')
plt.legend()


# In[71]:


foo = df.loc[df['Sim'] == '00'].set_index('datetimes').sort_index()

plt.plot(data.Yf4.iloc[100:200], label='meas')
plt.plot(foo['Power4'].iloc[100:200], '.',label='model')
plt.legend()


# In[ ]:


plt.plot(data.Yf4.values, label='meas')
plt.plot(df.loc[df['Sim'] == '00']['Power4'].values, label='model')
plt.legend()


# In[ ]:


plt.plot(df.loc[df['Sim'] == '00']['Power9'].values, label='model')
plt.plot(data.Yf9.values, label='meas')
plt.legend()


# In[ ]:


plt.plot(data.PR9.values, df.loc[df['Sim'] == '00']['Power9'].values, '.')
plt.xlim([0, 1.2])

