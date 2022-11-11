#!/usr/bin/env python
# coding: utf-8

# In[1]:


import PySAM.Pvsamv1 as PV
import PySAM.Grid as Grid
import PySAM.Utilityrate5 as UtilityRate
import PySAM.Cashloan as Cashloan
import pathlib
import json
import os

sam_input_folder = 'Row2Json'


# In[2]:


file_names = ["pvsamv1", "grid", "utilityrate5", "cashloan"]

pv = PV.new()  # also tried PVWattsSingleOwner
grid = Grid.from_existing(pv)
so = Cashloan.from_existing(grid, 'FlatPlatePVCommercial')
ur = UtilityRate.from_existing(pv)


# In[3]:


for count, module in enumerate([pv, grid, ur, so]):
    filetitle= 'Row2PrismBifi_' + file_names[count] + ".json"
    with open(os.path.join(sam_input_folder,filetitle), 'r') as file:
        data = json.load(file)
        for k, v in data.items():
            if k == 'number_inputs':
                continue
            try:
                module.value(k, v)
            except AttributeError:
                # there is an error is setting the value for ppa_escalation
                print(module, k, v)


# ##### Sanity checks

# In[4]:


pv.SolarResource.solar_resource_file


# In[5]:


pv.SolarResource.use_wf_albedo


# In[6]:


pv.SolarResource.irrad_mode


# In[7]:


pv.SolarResource.albedo


# In[8]:


pv.SolarResource.solar_resource_file = r'C:\Users\sayala\Documents\GitHub\Studies\Approaches2BifacialPerformanceMonitoring\InputFiles\BEST_SAM_60_Comb_00a.csv'


# In[9]:


grid.SystemOutput.gen = [0] * 8760  # p_out   # let's set all the values to 0
pv.execute()
grid.execute()
ur.execute()
so.execute()


# # LOOP THROUGH COMBOS

# In[10]:


import pandas as pd


# In[11]:


# 2-Bifi: Prism 457cBSTC
# 4-Bifi: LONGi Green Energy Technology Co._Ltd. LR6-72PH-370M
# 9-Bifi: Sunpreme Inc. SNPM-HxB-400


# In[13]:


# Row 2
system_capacity =  72.04280090332031   # VERY important value, only obtained by GUI.

# Row 4
system_capacity = 73.982               # VERY important value, only obtained by GUI.

# 9-Bifi: Sunpreme Inc. SNPM-HxB-400
system_capacity = 80.089


# In[14]:


dfAll = pd.DataFrame()

for ii in range(0, 1): # loop here over all the weather files or sims.
    sam_input_folder = 'Row2Json'
    file_names = ["pvsamv1", "grid", "utilityrate5", "cashloan"]

    pv = PV.new()  # also tried PVWattsSingleOwner
    grid = Grid.from_existing(pv)
    so = Cashloan.from_existing(grid, 'FlatPlatePVCommercial')
    ur = UtilityRate.from_existing(pv)

    for count, module in enumerate([pv, grid, ur, so]):
        filetitle= 'Row2PrismBifi_' + file_names[count] + ".json"
        with open(os.path.join(sam_input_folder,filetitle), 'r') as file:
            data = json.load(file)
            for k, v in data.items():
                if k == 'number_inputs':
                    continue
                try:
                    module.value(k, v)
                except AttributeError:
                    # there is an error is setting the value for ppa_escalation
                    print(module, k, v)

    # Change Weather File here
    pv.SolarResource.solar_resource_file = r'C:\Users\sayala\Documents\GitHub\Studies\Approaches2BifacialPerformanceMonitoring\InputFiles\BEST_SAM_60_Comb_00a.csv'
                    
    grid.SystemOutput.gen = [0] * 8760  # p_out   # let's set all the values to 0
    pv.execute()
    grid.execute()
    ur.execute()
    so.execute()

    # SAVE RESULTS
    # I usually save 1 all the data for 1 of the simulations, and all the others save just the main ones we need like DCP, temp. and front/rear irradiance.

    results = pv.Outputs.export()
    power = list(results['subarray1_dc_gross'])
    celltemp = list(results['subarray1_celltemp'])

    alldata=True

    # Saving select columns of results as needed
    if alldata:
        ii=0
        dni = list(results['dn'])
        dhi = list(results['df'])
        alb = list(results['alb'])
        poa= list(results['subarray1_poa_eff'])
        res = pd.DataFrame(list(zip(power, celltemp, dni, dhi, alb,  poa)),
                   columns =['sim'+str(ii)+'_DCP', 'sim'+str(ii)+'_Celltemp', 'DNI','DHI','alb','POA'])
    else: 
        rear = list(results['subarray1_poa_rear'])
        front = list(results['subarray1_poa_front'])
        res = pd.DataFrame(list(zip(power, celltemp, rear, front)),
                   columns =['sim'+str(ii)+'_DCP', 'sim'+str(ii)+'_Celltemp', 'sim'+str(ii)+'Grear','sim'+str(ii)+'Gfront'])

    res['sim'+str(ii)+'_DCP']= res['sim'+str(ii)+'_DCP']/system_capacity # normalizing by the system_capacity
    res = res[0:8760]
    #res.index = timestamps

    dfAll = pd.concat([dfAll, res], axis=1)


# In[15]:


dfAll


# In[ ]:




