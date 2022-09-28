#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import style
import pvlib
import datetime
import pprint
import os


# In[2]:


path_parent = os.path.dirname(os.getcwd())
InputFilesFolder = os.path.join(path_parent,'InputFiles')
ResultsFolder = r'TEMP'
exampleflag = False
debugflag = False


# In[3]:


import bifacialvf

# Print bifacialvf Version:
bifacialvf.__version__


# In[4]:


plt.rcParams['timezone'] = 'Etc/GMT+7'
font = {'family' : 'DejaVu Sans',
'weight' : 'bold',
'size'   : 22}
plt.rc('font', **font)
plt.rcParams['figure.figsize'] = (12, 5)


# In[5]:


### Set Field parameters


# In[6]:


# Variables
tilt = 10                   # PV tilt (deg)
sazm = 180                  # PV Azimuth(deg) or tracker axis direction
albedo = None               # Calculated in previous section from SRRL data. Value is 0.28 up to 11/18/19o
hub_height=1.5/2            #1.5m / 2m collector width
pitch = 2/0.35/2              # 1 / 0.35 where 0.35 is gcr --- row to row spacing in normalized panel lengths. 
rowType = "interior"        # RowType(first interior last single)
transFactor = 0             # TransmissionFactor(open area fraction)
sensorsy = 12                # sensorsy(# hor rows in panel)   <--> THIS ASSUMES LANDSCAPE ORIENTATION 
PVfrontSurface = "glass"    # PVfrontSurface(glass or ARglass)
PVbackSurface = "glass"     # PVbackSurface(glass or ARglass)

 # Calculate PV Output Through Various Methods    
calculateBilInterpol = False   # Only works with landscape at the moment.
calculatePVMismatch = False
portraitorlandscape='portrait'   # portrait or landscape
cellsnum = 72
bififactor = 1.0

# Tracking instructions
tracking=True
backtrack=True
limit_angle = 50


# ### Simulate POA with bifacialVf

# In[7]:


TMYtoread=os.path.join(InputFilesFolder,'TMY3_00a.csv')
writefiletitle=os.path.join(ResultsFolder, 'TMY3_00a.csv') 
myTMY3, meta = bifacialvf.bifacialvf.readInputTMY(TMYtoread)
# myTMY3, meta = bifacialvf.bifacialvf.fixintervalTMY(myTMY3,meta)  # Use if data resolution is diff. than hourly

bifacialvf.simulate(myTMY3, meta, writefiletitle=writefiletitle, 
                 tilt=tilt, sazm=sazm, pitch=pitch, hub_height=hub_height, 
                 rowType=rowType, transFactor=transFactor, sensorsy=sensorsy, 
                 PVfrontSurface=PVfrontSurface, PVbackSurface=PVbackSurface, 
                 albedo=albedo, tracking=tracking, backtrack=backtrack, 
                 limit_angle=limit_angle, calculatePVMismatch=calculatePVMismatch,
                 cellsnum = cellsnum, bififactor=bififactor,
                 calculateBilInterpol=calculateBilInterpol,
                 portraitorlandscape=portraitorlandscape)
    


# ### Load and Caculate performance with PVLIB

# In[8]:


data, meta = bifacialvf.loadVFresults(writefiletitle)


# ### Retrieve module data from CEC database

# In[9]:


db = pvlib.pvsystem.retrieve_sam(name='CECMod').T

# MODIFY THIS FOR YOUR TYPE OF MODULE
modfilter1 = db.index.str.startswith('SANYO') & db.index.str.endswith('VBHN325SA16')
mymod1 = db[modfilter1]

# Sanity check, in case the database gets updated and the module name slightly changes and doesn't find it. 
if len(mymod1) != 1:
    print("Check filtering")


# ### Calculate SAPM Cell Temperature

# In[10]:


from pvlib.temperature import TEMPERATURE_MODEL_PARAMETERS
tpmBifiGG = ( TEMPERATURE_MODEL_PARAMETERS['sapm']['open_rack_glass_polymer']) # temperature_model_parameters
tpmMonoBS = ( TEMPERATURE_MODEL_PARAMETERS['sapm']['open_rack_glass_glass']) # temperature_model_parameters


# Note: need to calcualte POA average and consider bifaciality factor depending on case modeled. Using first value of front POA for this example

# In[11]:


bifacialityfactor = 0.65
data['bifi_celltemp'] = pvlib.temperature.sapm_cell(data.No_1_RowFrontGTI, data.Tamb, data.VWind, tpmBifiGG['a'], tpmBifiGG['b'], tpmBifiGG['deltaT'])
data['mono_celltemp'] = pvlib.temperature.sapm_cell(data.No_1_RowFrontGTI, data.Tamb, data.VWind, tpmMonoBS['a'], tpmMonoBS['b'], tpmMonoBS['deltaT'])


# ### Calculate Performance with PVLib

# In[12]:


def calculatePerformance(effective_irradiance, temp_cell, CECMod):
    r'''
    The module parameters are given at the reference condition. 
    Use pvlib.pvsystem.calcparams_cec() to generate the five SDM 
    parameters at your desired irradiance and temperature to use 
    with pvlib.pvsystem.singlediode() to calculate the IV curve information.:
    
    Inputs
    ------
    df : dataframe
        Dataframe with the 'effective_irradiance' columns and 'temp_cell'
        columns.
    CECMod : Dict
        Dictionary with CEC Module PArameters for the module selected. Must 
        contain at minimum  alpha_sc, a_ref, I_L_ref, I_o_ref, R_sh_ref,
        R_s, Adjust
    '''
    
    IL, I0, Rs, Rsh, nNsVth = pvlib.pvsystem.calcparams_cec(
        effective_irradiance=effective_irradiance,
        temp_cell=temp_cell,
        alpha_sc=float(CECMod.alpha_sc),
        a_ref=float(CECMod.a_ref),
        I_L_ref=float(CECMod.I_L_ref),
        I_o_ref=float(CECMod.I_o_ref),
        R_sh_ref=float(CECMod.R_sh_ref),
        R_s=float(CECMod.R_s),
        Adjust=float(CECMod.Adjust)
        )
    
    IVcurve_info = pvlib.pvsystem.singlediode(
        photocurrent=IL,
        saturation_current=I0,
        resistance_series=Rs,
        resistance_shunt=Rsh,
        nNsVth=nNsVth 
        )
    
    return IVcurve_info['p_mp']


# In[13]:


data['S1_dcP'] = calculatePerformance(data.No_1_RowFrontGTI, data.bifi_celltemp, mymod1)
data['S2_dcP'] = calculatePerformance(data.No_1_RowFrontGTI, data.mono_celltemp, mymod1)


# ### Save results

# In[ ]:




