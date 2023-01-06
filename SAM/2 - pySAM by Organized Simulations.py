#!/usr/bin/env python
# coding: utf-8

# # pySAM by Organized Simulations
# 
# Runs all combinations in orga, for the 4 rows
# Calcualtes RMSE & MBD, relative and absolutes

# In[1]:


# Written for nrel-pysam 3.0.2
import PySAM.Pvsamv1 as PV
import PySAM.Grid as Grid
import PySAM.Utilityrate5 as UtilityRate
import PySAM.Cashloan as Cashloan
import pathlib
import json
import os

sif2 = 'Row2Json'
sif4 = 'Row4Json'
sif8 = 'Row8Json'
sif9 = 'Row9Json'

jsonnames = ['Row2PrismBifi', 'Row4LongiBifi', 'Row8MONOFACIALReference', 'Row9Sunpreme']


# In[35]:


import PySAM
import pvlib
print(pvlib.__version__)


# In[ ]:





# In[44]:


file_names = ["pvsamv1", "grid", "utilityrate5", "cashloan"]

pv2 = PV.new()  # also tried PVWattsSingleOwner
grid2 = Grid.from_existing(pv2)
ur2 = UtilityRate.from_existing(pv2)
so2 = Cashloan.from_existing(grid2, 'FlatPlatePVCommercial')


pv4 = PV.new()  # also tried PVWattsSingleOwner
grid4 = Grid.from_existing(pv4)
ur4 = UtilityRate.from_existing(pv4)
so4 = Cashloan.from_existing(grid4, 'FlatPlatePVCommercial')


pv8 = PV.new()  # also tried PVWattsSingleOwner
grid8 = Grid.from_existing(pv8)
ur8 = UtilityRate.from_existing(pv8)
so8 = Cashloan.from_existing(grid8, 'FlatPlatePVCommercial')


pv9 = PV.new()  # also tried PVWattsSingleOwner
grid9 = Grid.from_existing(pv9)
ur9 = UtilityRate.from_existing(pv9)
so9 = Cashloan.from_existing(grid9, 'FlatPlatePVCommercial')


# In[45]:


for count, module in enumerate([pv2, grid2, ur2, so2]):
    filetitle= 'Row2PrismBifi' + '_' + file_names[count] + ".json"
    with open(os.path.join(sif2,filetitle), 'r') as file:
        data = json.load(file)
        for k, v in data.items():
            if k == 'number_inputs':
                continue
            try:
                module.value(k, v)
            except AttributeError:
                # there is an error is setting the value for ppa_escalation
                print(module, k, v)


# In[46]:


for count, module in enumerate([pv4, grid4, ur4, so4]):
    filetitle= 'Row4LongiBifi' + '_' + file_names[count] + ".json"
    with open(os.path.join(sif4,filetitle), 'r') as file:
        data = json.load(file)
        for k, v in data.items():
            if k == 'number_inputs':
                continue
            try:
                module.value(k, v)
            except AttributeError:
                # there is an error is setting the value for ppa_escalation
                print(module, k, v)


# In[48]:


for count, module in enumerate([pv8, grid8, ur8, so8]):
    filetitle= 'Row8MONOFACIALReference' + '_' + file_names[count] + ".json"
    with open(os.path.join(sif8,filetitle), 'r') as file:
        data = json.load(file)
        for k, v in data.items():
            if k == 'number_inputs':
                continue
            try:
                module.value(k, v)
            except AttributeError:
                # there is an error is setting the value for ppa_escalation
                print(module, k, v)


# In[12]:


for count, module in enumerate([pv9, grid9, ur9, so9]):
    filetitle= 'Row9Sunpreme' + '_' + file_names[count] + ".json"
    with open(os.path.join(sif9,filetitle), 'r') as file:
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

# In[13]:


pv2.SolarResource.solar_resource_file
pv2.SolarResource.use_wf_albedo
pv2.SolarResource.irrad_mode
pv2.SolarResource.albedo


# # LOOP THROUGH COMBOS

# In[14]:


import pandas as pd


# In[15]:


# 2-Bifi: Prism 457cBSTC
# 4-Bifi: LONGi Green Energy Technology Co._Ltd. LR6-72PH-370M
# 9-Bifi: Sunpreme Inc. SNPM-HxB-400


# In[16]:


# For unknown reasons, pySAM does not calculate this number and you have to obtain it from the GUI.

system_capacity2 =  72.04280090332031   
system_capacity4 = 73.982               
system_capacity8 = 71.078
system_capacity9 = 80.089


# In[17]:


orga = pd.read_excel('..\Combinations.xlsx', skiprows = 20)
orga.fillna(method='ffill')


# In[18]:


InputFilesFolder = r'..\InputFiles'
ResultsFolder = r'..\SAM\Results'


# In[19]:


wftimestamp = pd.read_csv(os.path.join(InputFilesFolder,'WF_SAM_'+orga.loc[0]['WeatherFile_Name']+'.csv'), skiprows=2)
datelist = list(pd.to_datetime(wftimestamp.iloc[:,0:4]))
months = list(wftimestamp.iloc[:,1])
years = list(wftimestamp.iloc[:,0])
days = list(wftimestamp.iloc[:,2])
hours = list(wftimestamp.iloc[:,3])


# In[21]:


pv4.Shading.subarray1_shade_mode


# In[27]:


orga['irrad_mod'].unique()


# In[30]:


dfAll = pd.DataFrame()

for ii in range(0, len(orga)): # loop here over all the weather files or sims.

    print(ii)
    weatherfile = os.path.join(InputFilesFolder,'WF_SAM_'+orga.loc[ii]['WeatherFile_Name']+'.csv')
    savefilevar = os.path.join(ResultsFolder,'Results_pySAM_'+orga.loc[ii]['Sim']+'.csv')

#    POABOA = orga.loc[ii]['POABOA']
    irrad_mod = orga.loc[ii]['irrad_mod']
    sky_model = orga.loc[ii]['sky_model']

    # Change Weather File here
    pv2.SolarResource.solar_resource_file = weatherfile
    pv4.SolarResource.solar_resource_file = weatherfile
    pv8.SolarResource.solar_resource_file = weatherfile
    pv9.SolarResource.solar_resource_file = weatherfile
    
    pv2.SolarResource.sky_model = orga.loc[ii]['sky_model']
    pv2.SolarResource.irrad_mode = orga.loc[ii]['irrad_mod']
    pv4.SolarResource.sky_model = orga.loc[ii]['sky_model']
    pv4.SolarResource.irrad_mode = orga.loc[ii]['irrad_mod']
    pv8.SolarResource.sky_model = orga.loc[ii]['sky_model']
    pv8.SolarResource.irrad_mode = orga.loc[ii]['irrad_mod']
    pv9.SolarResource.sky_model = orga.loc[ii]['sky_model']
    pv9.SolarResource.irrad_mode = orga.loc[ii]['irrad_mod']
    
    # So that irrad_mod for POA works shading has to be inactivated.
    if orga.loc[ii]['irrad_mod'] >= 3:
        pv2.Shading.subarray1_shade_mode = 0
        pv4.Shading.subarray1_shade_mode = 0
        pv8.Shading.subarray1_shade_mode = 0
        pv9.Shading.subarray1_shade_mode = 0
    else:
        pv2.Shading.subarray1_shade_mode = 1.0
        pv4.Shading.subarray1_shade_mode = 1.0
        pv8.Shading.subarray1_shade_mode = 1.0
        pv9.Shading.subarray1_shade_mode = 1.0
    
    grid2.SystemOutput.gen = [0] * 8760  # p_out   # let's set all the values to 0
    pv2.execute()
    grid2.execute()
    ur2.execute()
    so2.execute()

    grid4.SystemOutput.gen = [0] * 8760  # p_out   # let's set all the values to 0
    pv4.execute()
    grid4.execute()
    ur4.execute()
    so4.execute()

    grid8.SystemOutput.gen = [0] * 8760  # p_out   # let's set all the values to 0
    pv8.execute()
    grid8.execute()
    ur8.execute()
    so8.execute()

    grid9.SystemOutput.gen = [0] * 8760  # p_out   # let's set all the values to 0
    pv9.execute()
    grid9.execute()
    ur9.execute()
    so9.execute()

    # SAVE RESULTS|
    # I usually save 1 all the data for 1 of the simulations, and all the others save just the main ones we need like DCP, temp. and front/rear irradiance.

    results = pv2.Outputs.export()
    power2 = list(results['subarray1_dc_gross']) # normalizing by the system_capacity
    celltemp2 = list(results['subarray1_celltemp'])
    rear2 = list(results['subarray1_poa_rear'])
    front2 = list(results['subarray1_poa_front'])

    results = pv4.Outputs.export()
    power4 = list(results['subarray1_dc_gross']) # normalizing by the system_capacity
    celltemp4 = list(results['subarray1_celltemp'])
    rear4 = list(results['subarray1_poa_rear'])
    front4 = list(results['subarray1_poa_front'])

    results = pv8.Outputs.export()
    power8 = list(results['subarray1_dc_gross']) # normalizing by the system_capacity
    celltemp8 = list(results['subarray1_celltemp'])
    #rear8 = list(results['subarray1_poa_rear'])
    front8 = list(results['subarray1_poa_front'])
    
    results = pv9.Outputs.export()
    power9 = list(results['subarray1_dc_gross']) # normalizing by the system_capacity
    celltemp9 = list(results['subarray1_celltemp'])
    rear9 = list(results['subarray1_poa_rear'])
    front9 = list(results['subarray1_poa_front'])

    dni = list(results['dn'])
    dhi = list(results['df'])
    alb = list(results['alb'])
    
    
    simtyp = [orga.loc[ii]['Sim']] * 8760

    res = pd.DataFrame(list(zip(simtyp, power2, celltemp2, rear2, front2,
                               power4, celltemp4, rear4, front4,
                               power8, celltemp8, front8,
                                power9, celltemp9, rear9, front9, dni, dhi, alb)),
           columns = ['Sim', 'Power2' , 'CellTemp2', 'Rear2', 'Front2',
                     'Power4' , 'CellTemp4', 'Rear4', 'Front4',
                     'Power8' , 'CellTemp8', 'Front8',
                     'Power9' , 'CellTemp9', 'Rear9', 'Front9', 'DNI', 'DHI', 'Alb'])

    res = res[0:8760]
    res['index'] = res.index
    res['Power2']= res['Power2']/system_capacity2 # normalizing by the system_capacity
    res['Power4']= res['Power4']/system_capacity4 # normalizing by the system_capacity
    res['Power8']= res['Power8']/system_capacity8 # normalizing by the system_capacity
    res['Power9']= res['Power9']/system_capacity9 # normalizing by the system_capacity
    res['datetimes'] = datelist
    res['Year'] = years
    res['Month'] = months
    res['Hour'] = hours

    #    res.index = timestamps
    res.to_pickle('Sim_'+orga.loc[ii]['Sim']+'.pkl')
    res.to_csv(savefilevar, float_format='%g')
    dfAll = pd.concat([dfAll, res], ignore_index=True, axis=0)
    


# In[ ]:


dfAll.to_pickle('Results_pysam.pkl')

