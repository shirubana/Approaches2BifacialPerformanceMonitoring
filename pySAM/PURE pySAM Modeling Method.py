#!/usr/bin/env python
# coding: utf-8

# # PURE pySAM Modeling 
# 
# This journal shows hwo to model on pysam starting from default values. It DOES NOT use SAM exported Jsons, and instead modifies all variables manually. 
# 
# 
# <div class="alert alert-block alert-danger">
# <b>pySAM Error:</b> Since October '22, this method started failing pysam. However, it does not report the issue of the error. The SAM team is aware of this.
# </div>
# 
# 
# <ol>
#     <li> <a href='#step1'> Create a default pySAM PV simulation </a></li>
#     <li> <a href='#step2'> Set our baseline system values, including Inverter </a></li>
#     <li> <a href='#step3'> Loop for each module type, for yearly data at hourly resolution </a></li>
#     <li> <a href='#step4'> Loop for each module type, for yearly data at 15 min resolution  </a></li>
# </ol>
# 
# <ul>
#     <li> <a href='#step5'> NOT WORKING: All years together </a></li>
# </ul>
# 
# 
# <div class="alert alert-block alert-warning">
# <b>SAM-only variables:</b> 
# </div>
# 
# Please note there is an accompanying SAM file, that is used to get values from the ``GUI`` that are needed (and that pysam does not provide/calculate) of the system:
# * inv_snl_eff_cec 
# * inverter_count 
# * inv_tdc_cec_db  (Temperature derate curves for CEC Database [(Vdc, C, %/C)])
# * system_capacity (different for each Row modeled)
# 
# 
#     

# In[1]:


# PySAM downloaded by either `pip install nrel-pysam` or `conda install -c nrel nrel-pysam`
import PySAM.Pvsamv1 as pv
import PySAM
import xlsxwriter
import json
import pandas as pd
import os
import pprint as pp
import requests
import numpy as np


# In[2]:


Resultsfolder = r'TEMP'
path_parent = os.path.dirname(os.getcwd())
InputFiles = os.path.join(path_parent,'InputFiles')
exampleflag = False
debugflag = False


# In[3]:



PySAM.__version__


# <a id='step1'></a>

# ## Create a default pySAM PV simulation </a></li>

# In[4]:


sam1 = pv.default("FlatPlatePVCommercial")
solar_resource_file = os.path.join(InputFiles,'BEST_SAM_60_Comb_00a.csv')
sam1.SolarResource.solar_resource_file = solar_resource_file


# <a id='step2'></a>

# ## Set our baseline system values, including Inverter
# 
# !!! UPDATE THIS TO USE PVLIB DONWLOAD
# 

# In[5]:


#url = 'https://raw.githubusercontent.com/NREL/SAM/develop/deploy/libraries/CEC%20Modules.csv'
url = 'https://raw.githubusercontent.com/NREL/SAM/patch/deploy/libraries/CEC%20Inverters.csv'
url = 'https://raw.githubusercontent.com/NREL/SAM/master/deploy/libraries/CEC%20Inverters.csv'

df = pd.read_csv(url, index_col=0)
modfilter = df.index.str.startswith('Fronius USA') & df.index.str.contains('480V')  & df.index.str.contains('10.0')
myinv = df[modfilter]

if len(myinv) != 1:
    print("Error selecting inverter, check filtering")


# In[6]:


# assigning our simulation params
pitch = 5.7
cec_bifacial_ground_clearance_height = 1.5
cec_bifacial_transmission_factor = 0

subarray1_track_mode = 1
subarray1_backtrack = 1
subarray1_rotlim = 50

subarray1_modules_per_string = 20
subarray1_nstrings = 10
subarray1_nmodx = 20
subarray1_nmody = 1
subarray1_shade_mode = 1

inverter_count = 10

subarray1_rear_irradiance_loss = 10
subarray1_soiling = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
use_wf_albedo = 1
# cec_a_ref = 1.885731
# inv_snl_vdco = 310
#  part of Inverter mppt_low_inverter = 100
subarray1_tilt = 0 


# In[7]:


inv_snl_c0 = float(myinv['C0'])
inv_snl_c1 = float(myinv['C1'])
inv_snl_c2 = float(myinv['C2'])
inv_snl_c3 = float(myinv['C3'])
inv_snl_paco = float(myinv['Paco'])
inv_snl_pdco = float(myinv['Pdco']) 
inv_snl_pnt = float(myinv['Pnt'])
inv_snl_pso = float(myinv['Pso'])
inv_snl_vdcmax = float(myinv['Vdcmax'])
inv_snl_vdco =  float(myinv['Vdco'])
mppt_low_inverter = float(myinv['Mppt_low'])
mppt_hi_inverter = float(myinv['Mppt_high'])

# Values from GUI
inv_snl_eff_cec = 96.776
inverter_count = 10
inv_tdc_cec_db = [[1, 52.79999923706055, -0.020999999716877937]] # Temperature derate curves for CEC Database [(Vdc, C, %/C)]


# In[8]:


newval = { 'SolarResource': {
                            'use_wf_albedo': use_wf_albedo},
           'SystemDesign' : {
                            'inverter_count':inverter_count,
                            'subarray1_backtrack':subarray1_backtrack,
                            'subarray1_modules_per_string':subarray1_modules_per_string,
                            'subarray1_nstrings':subarray1_nstrings,
                            'subarray1_rotlim':subarray1_rotlim,
                            'subarray1_track_mode':subarray1_track_mode,
                            'subarray1_tilt': subarray1_tilt},
            'Layout':      {
                            'subarray1_nmodx':subarray1_nmodx,
                            'subarray1_nmody':subarray1_nmody},
            'Shading' :    {'subarray1_shade_mode':subarray1_shade_mode},
            'Losses' :     {
                            'subarray1_soiling':subarray1_soiling,
                            'subarray1_rear_irradiance_loss':subarray1_rear_irradiance_loss},
          'Inverter':  { 'inv_snl_paco': inv_snl_paco,
                                   'mppt_low_inverter': mppt_low_inverter,
                                   'mppt_hi_inverter': mppt_hi_inverter,
                                   'inv_snl_eff_cec':inv_snl_eff_cec,
                                   'inverter_count':inverter_count},
            'InverterCECDatabase': {
                                    'inv_snl_c0': inv_snl_c0,
                                    'inv_snl_c1': inv_snl_c1,
                                    'inv_snl_c2': inv_snl_c2,
                                    'inv_snl_c3': inv_snl_c3,
                                    'inv_snl_paco': inv_snl_paco,
                                    'inv_snl_pdco': inv_snl_pdco,
                                    'inv_snl_pnt': inv_snl_pnt,
                                    'inv_snl_pso': inv_snl_pso,
                                    'inv_snl_vdcmax': inv_snl_vdcmax,
                                    'inv_snl_vdco': inv_snl_vdco,
                                    'inv_tdc_cec_db':inv_tdc_cec_db
             }}

          


# In[9]:


sam1.assign(newval)


# In[10]:


#url = 'https://raw.githubusercontent.com/NREL/SAM/develop/deploy/libraries/CEC%20Modules.csv'
url = 'https://raw.githubusercontent.com/NREL/SAM/patch/deploy/libraries/CEC%20Modules.csv'
url = 'https://raw.githubusercontent.com/NREL/SAM/master/deploy/libraries/CEC%20Modules.csv'
df = pd.read_csv(url, index_col=0)


# <a id='step3'></a>

# ## Loop for each module type, for yearly data at hourly resolution 
# 

# In[11]:


solar_resource_file = os.path.join(InputFiles,'BEST_SAM_60_Comb_00a.csv')
weatherfile = pd.read_csv(solar_resource_file, skiprows=2)


# In[12]:


#timestamps = pd.to_datetime(weatherfile[['Year','Month','Day','Hour']])

dfAll = pd.DataFrame()
solarresource = 'BEST_SAM_60_Comb_00a.csv'

for ii in range(0,4):
    if ii==0:
        # 2-Bifi: Prism 
        modfilter = df.index.str.startswith('Prism') & df.index.str.contains('457BSTC')
        system_capacity =  72.04280090332031   # VERY important value, only obtained by GUI.
        cec_is_bifacial = 1
        cec_bifaciality = 0.694 

    elif ii==1:
        # 4-Bifi: LONGi Green Energy Technology Co._Ltd. LR6-72PH-370M
        modfilter = df.index.str.startswith('LONGi') & df.index.str.contains('LR6-72PH-370M')
        system_capacity = 73.982               # VERY important value, only obtained by GUI.
        cec_is_bifacial = 1
        cec_bifaciality = 0.73

    elif ii==2:
        # 9-Bifi: Sunpreme Inc. SNPM-HxB-400
        modfilter = df.index.str.startswith('Sunpreme') & df.index.str.endswith('SNPM-HxB-400')
        system_capacity = 80.089
        cec_is_bifacial = 1
        cec_bifaciality = 0.87

    solar_resource_file = os.path.join(InputFiles,solarresource)
    sam1.SolarResource.solar_resource_file = solar_resource_file

    mymod = df[modfilter]

    cec_a_ref = float(mymod.a_ref[0])
    cec_adjust = float(mymod.Adjust[0]) 
    cec_alpha_sc = float(mymod.alpha_sc[0]) 
    cec_area = float(mymod.A_c[0]) 

    cec_beta_oc = float(mymod.beta_oc[0]) 
    cec_gamma_r = float(mymod.gamma_r[0]) 
    cec_i_l_ref = float(mymod.I_L_ref[0])
    cec_i_mp_ref = float(mymod.I_mp_ref[0]) 
    cec_i_o_ref = float(mymod.I_o_ref[0]) 
    cec_i_sc_ref = float(mymod.I_sc_ref[0]) 
    #cec_is_bifacial = int(mymod.Bifacial[0]) # Assigning manually from the if statements above
    if np.isnan(float(mymod.Length[0])): # Adjusting size of module to standard size if not in catalogue
        cec_module_length = 2.0
    else:
        cec_module_length = float(mymod.Length[0]) 
    if np.isnan(float(mymod.Width[0])):
        cec_module_width = 1.0
    else: 
        cec_module_width = float(mymod.Width[0]) 
    module_aspect_ratio = cec_module_length/cec_module_width    # Adjusting module aspect ratio

    cec_n_s = float(mymod.N_s[0]) 
    cec_r_s = float(mymod.R_s[0]) 
    cec_r_sh_ref = float(mymod.R_sh_ref[0])
    cec_t_noct = float(mymod.T_NOCT[0]) 
    cec_v_mp_ref = float(mymod.V_mp_ref[0]) 
    cec_v_oc_ref = float(mymod.V_oc_ref[0]) 

    subarray1_gcr = cec_module_length/pitch        # Adjusting the gcr slightly for the module length.

    newval = {'SystemDesign':{'system_capacity':system_capacity, # VERY important value, only obtained by GUI.
                             'subarray1_gcr':subarray1_gcr}, 
              'Layout':{'module_aspect_ratio':module_aspect_ratio},
                'CECPerformanceModelWithModuleDatabase': {
                    'cec_a_ref': cec_a_ref,
                    'cec_adjust': cec_adjust,
                    'cec_alpha_sc': cec_alpha_sc,
                    'cec_area': cec_area,
                    'cec_beta_oc': cec_beta_oc,
                    'cec_gamma_r': cec_gamma_r,
                    'cec_i_l_ref': cec_i_l_ref,
                    'cec_i_mp_ref': cec_i_mp_ref,
                    'cec_i_o_ref': cec_i_o_ref,
                    'cec_i_sc_ref': cec_i_sc_ref,
                    'cec_is_bifacial': cec_is_bifacial,
                    'cec_module_length': cec_module_length,
                    'cec_module_width': cec_module_width,
                    'cec_n_s': cec_n_s,
                    'cec_r_s': cec_r_s,
                    'cec_r_sh_ref': cec_r_sh_ref,
                    'cec_t_noct': cec_t_noct,
                    'cec_v_mp_ref': cec_v_mp_ref,
                    'cec_v_oc_ref': cec_v_oc_ref,
                    'cec_bifacial_ground_clearance_height': cec_bifacial_ground_clearance_height,
                    'cec_bifacial_transmission_factor': cec_bifacial_transmission_factor,
                    'cec_bifaciality': cec_bifaciality
                }
             }

    sam1.assign(newval)

    sam1.execute()
    results = sam1.Outputs.export()

    power = list(results['subarray1_dc_gross'])
    celltemp = list(results['subarray1_celltemp'])

    # Saving select columns of results as needed
    if ii == 0:
        dni = list(results['dn'])
        dhi = list(results['df'])
        alb = list(results['alb'])
        rear = list(results['subarray1_poa_rear'])
        front = list(results['subarray1_poa_front'])
        poa= list(results['subarray1_poa_eff'])
        res = pd.DataFrame(list(zip(power, celltemp, dni, dhi, alb, rear, front, poa)),
                   columns =['row'+str(ii)+'_DCP', 'row'+str(ii)+'_Celltemp', 'DNI','DHI','alb','Grear','Gfront','POA'])
    else:
        res = pd.DataFrame(list(zip(power, celltemp)),
                   columns =['row'+str(ii)+'_DCP', 'row'+str(ii)+'_Celltemp'])

    res['row'+str(ii)+'_DCP']= res['row'+str(ii)+'_DCP']/system_capacity # normalizing by the system_capacity
    res = res[0:8760]
    #res.index = timestamps

    dfAll = pd.concat([dfAll, res], axis=1)


# In[ ]:


# Shifting back so results match the provided timestamps
df_results = dfAllyears.shift(60, freq='T')
df_results = df_results.tz_localize('Etc/GMT+7')

df_results.to_pickle(os.path.join(testfolder,'pySAM_results.pickle'))


# <a id='step4'></a>
