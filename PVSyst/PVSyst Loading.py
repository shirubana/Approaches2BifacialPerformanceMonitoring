#!/usr/bin/env python
# coding: utf-8

# # PVSyst 

# In[1]:


import pandas as pd
import numpy as np


# In[3]:


def definePVsystOutputDecoder():
    
    PVsystOutputDecoder = {'NormFac' : 'Normalised performance index (ref. to STC)',
    'Yr' : 'Reference Incident Energy in coll. Plane',
    'Ya' : 'Normalized Array Production',
    'Yf' : 'Normalized System Production',
    'Lc' : 'Normalized Array Losses',
    'Ls' : 'Normalized System Losses',
    'Lcr' : 'Array Loss / Incident Energy Ratio',
    'Lsr' : 'System Loss / Incident Enregy Ratio',
    'PR' : 'Performance Ratio',
    'Effic' : 'Efficiencies',
    'EffArrR' : 'Effic. Eout array / rough area',
    'EffArrC' : 'Effic. Eout arra / cells area',
    'EffSysR' : 'Effic. Eout system / rough area',
    'EffSysC' : 'Effic Eout system / cells area',
    'EffInvB' : 'Inverter effic., threshold loss included',
    'EffInvR' : 'Inverter efficiency (operating)',
    'System' : 'System Operating Conditions',
    'Syst_ON' : 'System operating duration',
    'EOutInv' : 'Available Energy at Inverter Output',
    'E_Grid' : 'Energy injected into grid',
    'Invert' : 'Inverter Losses',
    'InvLoss' : 'Global inverter losses',
    'IL_Oper' : 'Inverter Loss during operation(efficiency)',
    'IL_Pmin' : 'Inverter Loss due to power threshold',
    'IL_Vmin' : 'Inverter Loss due to voltage threshold',
    'IL_Pmax' : 'Inverter Loss over nominal inv. Power',
    'IL_Vmax' : 'Inverter Loss over nominal inv. Voltage',
    'IL_Imax' : 'Inverter Loss due to max. input current',
    'Array' : 'PV array (field behaviour)',
    'EArrRef' : 'Array refernece energy for PR',
    'EArrNom' : 'Array nominal energy (at STC effic.)',
    'GIncLss' : 'PV loss due to irradiance level',
    'TempLss' : 'PV loss due to temperature',
    'OP_Pmin' : 'No Description',
    'OP_Pmax' : 'No Description',
    'OP_Oper' : 'No Description',
    'ModQual' : 'Module quality loss',
    'LIDLoss' : 'LID - Light induced degradation',
    'MisLoss' : 'Module array mismatch loss',
    'MismBak' : 'Mismatch for back irradiance',
    'OhmLoss' : 'Ohmic wiring loss',
    'EArrMPP' : 'Array virtual energy at MPP',
    'EArray' : 'Effective energy at the output of the array',
    'TExtON' : 'Average Ambient Temperature during running',
    'TArray' : 'Average Module Temperature during running',
    'TArrWtd' : 'Module Temper., weighted by GlobInc',
    'DTArr' : 'Temper. Difference modules-ambient during running',
    'DTArrGl' : 'DTArr weighted by "effective" incident Global',
    'IArray' : 'Array Current',
    'UArray' : 'Array Voltage',
    'ArrayON' : 'Duration of the PV production of the array',
    'IncFact' : 'Incident energy factors',
    'FTransp' : 'Transpostiion factor GlobInc / GlobHor',
    'FShdGl' : 'Near Shading Factor on global',
    'FShdBm' : 'Near Shading Factor on beam',
    'FShdDif' : 'Near Shading Factor on sky diffuse',
    'FShdAlb' : 'Near Shading Factor on albedo',
    'FIAMGl' : 'IAM factor on global',
    'FIAMBm' : 'IAM factor on beam',
    'FIAMDif' : 'IAM facotr on sky diffuse',
    'FIAMAlb' : 'IAM factor on albedo',
    'FSlgGl' : 'Soiling loss factor',
    'FSlgBm' : 'Soiling factor on beam',
    'FSlgDif' : 'Soiling loss factor on diffuse',
    'FSlgAlb' : 'Soiling loss factor on albedo',
    'FIAMShd' : 'Combined IAM and shading factors on global',
    'FEffDif' : 'IAM and shading factors on diffuse',
    'FEffAlb' : 'IAM and shading factors on albedo',
    'Angles' : 'Solar geometry',
    'HSol' : 'Sun height',
    'AzSol' : 'Sun azimuth',
    'AngInc' : 'Incidence angle',
    'AngProf' : 'Profile angle',
    'PhiAng' : 'Tracking: phi angle',
    'Transpo' : 'Transposition Variables',
    'BeamTrp' : 'Beam, Transposed',
    'DifITrp' : 'Diffuse Isotropic, Transposed',
    'CircTrp' : 'Circumsolar, Transposed',
    'HBndTrp' : 'Horizon Band, Transposed',
    'AlbTrp' : 'Albedo, Transposed',
    'GlobTrp' : 'Global, Tranpsosed',
    'MetData' : 'Meteorological Data',
    'GlobHor' : 'Horizontal global irradiation',
    'DiffHor' : 'Horizontal diffuse irradiation',
    'BeamHor' : 'Horizontal beam irradiation',
    'T_Amb' : 'T amb.',
    'WindVel' : 'Wind velocity',
    'IncColl' : 'Incident irradiance in collector plane',
    'GincThr' : 'Global incident below threshold',
    'GlobInc' : 'Global incident in coll. Plane',
    'BeamInc' : 'Beam incident in coll. Plane',
    'DifSInc' : 'Sky Diffuse incident in coll. Plane',
    'Alb_Inc' : 'Albedo incident in coll. Plane',
    'Bm_Gl' : 'Incident Beam / Global ratio',
    'DifA_Gl' : 'Incident Diffuse / Global ratio',
    'DifS_Gl' : 'Incident Sky Diffuse / Global ratio',
    'Alb_Gl' : 'Incident Albedo / Global ratio',
    'GlobShd' : 'Global corrected for shading',
    'ShdLoss' : 'Near shadings loss',
    'ShdBLss' : 'Near shadings beam loss',
    'ShdDLss' : 'Near shadings diffuse loss',
    'ShdALss' : 'Near shadings albedo loss',
    'GlobIAM' : 'Global corrected for incidente (IAM)',
    'IAMLoss' : 'Incidence (IAM) loss',
    'IAMBLss' : 'Incidence beam loss',
    'IAMDLss' : 'Incidence diffuse loss',
    'IAMALss' : 'Incidence albedo loss',
    'GlobSlg' : 'Global corrected for soiling',
    'SlgLoss' : 'Soiling loss',
    'SlgBLss' : 'Soiling beam loss',
    'SlgDLss' : 'Soiling diffuse loss',
    'SlgALss' : 'Soiling albedo loss',
    'GlobEff' : 'Effective Global, corr. For IAM and shadings',
    'BeamEff' : '"Effective" Beam, corr. For IAM and shadings',
    'DiffEff' : 'Effective Diffuse, corr. For IAM shadings',
    'Alb_Eff' : '"Effective" Albedo, corr. For IAM and shadings',
    'GlobGnd' : 'Global incident on ground',
    'ReflLss' : 'Ground reflection loss (albedo)',
    'BkVFLss' : 'View Factor for rear side',
    'DifSBak' : 'Sky diffuse on the rear side',
    'BackShd' : 'Shadings loss on rear side',
    'GlobBak' : 'Global Irradiance on rear side',
    'ReflFrt' : 'Ground reflection on front side',
    'ReflBck' : 'Ground reflection on back side',
    'BmIncBk' : 'Beamincident on the rear side',
    'BmSFBak' : 'Beam shading factor on the rear side',
    'BIAMFBk' : 'Beam IAM factor on the rear side',
    'BeamBak' : 'Beam effective on the rear side'}

    return PVsystOutputDecoder

def readPVSystOutputFile(filename):
    '''
    Reads a PVSYSt hourly output file, puts it in dataframe format and returns a 
    column header decoder to understand all the variables that name the columns.
    Also returns any metadata included in the file.
    
    Input
    -----
    filename       PVsyst hourly simulation output file(.csv)
    
    Returns
    -------
    df             Dataframe with the hourly simulation results. Columns are named for each variable.
    columnheaders  Decoder for the column header names, which are variables. This ties the available columns with the description of that variable.
    metdata        metdata included in the pvsyst file.
    
    '''
    
    import pandas as pd
    import csv
    
    f = open(filename)
    
    # Save metdata from file
    metdata=[]
    for i in range(10):  # skip the first 13 lines that are useless for the columns definition
        metdata.append(f.readline())  # use the resulting string for metadata extraction
      
    headers = f.readline().split(";")
    headers[-1] = headers[-1].strip()

    units = f.readline().split(";")
    units[-1] = units[-1].strip()

    PVsystOutputDecoder = definePVsystOutputDecoder()
    
    # Creating a dictionary for headers, units and their definition
    columnheaders = {}    
    for i in range (1, len(headers)):
        columnheaders[headers[i]] = {'Definition' : PVsystOutputDecoder[headers[i]],
                     'Units': units[i]}
    
    df = pd.read_csv(f, sep=";", names=headers)   
    df.index = pd.to_datetime(df['date'], dayfirst=True)
    
    return df, columnheaders, metdata


# ## PVSyst Irradiances Sanity Checks
# Old notes
# 
# GlobEff is supposed to have Shd, IAM, and SLG losses in it, but it's higher value than Sosses... IAM - Slg.Loss gives Slg indeed.)
# 
# IMPORTANT: Choosing Globeff for Gfront and Globbak for Grear

# In[ ]:


print('Inc', PVSystres.iloc[2091]['5_GlobInc']) 
print('Shd', PVSystres.iloc[14]['5_GlobShd']) # Gfront?
print('IAM', PVSystres.iloc[14]['5_GlobIAM'])
print('Slg', PVSystres.iloc[14]['5_GlobSlg']) # Gfront?
print('Eff', PVSystres.iloc[14]['5_GlobEff']) # Gfront?
print('Slg Loss', PVSystres.iloc[14]['5_SlgLoss']) # Grear
print('Rear', PVSystres.iloc[14]['5_GlobBack']) # Grear
print('Rear', PVSystres.iloc[14]['5_GlobBack']*0.63) # Grear

