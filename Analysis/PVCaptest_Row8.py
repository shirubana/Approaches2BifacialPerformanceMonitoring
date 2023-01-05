#!/usr/bin/env python
# coding: utf-8

# # Load Field data, PVSyst and DAS result files and run cap test

# In[1]:


import pandas as pd
import matplotlib.pyplot as plt
import pvlib
import numpy as np
import os
import re
from pathlib import Path
from datetime import datetime
from copy import deepcopy


# In[2]:


fielddataFolder = 'FieldData'
InputFilesFolder = 'InputFiles'
#SAMResultsFolder = os.path.join(os.path.dirname(os.getcwd()), 'SAM','Results')


# In[3]:


plt.rcParams.update({'font.size': 22})
plt.rcParams['figure.figsize'] = (12, 4)


# In[4]:


# pip install pvcaptest and holoviews if you don't have it installed already.
# following example from https://pvcaptest.readthedocs.io/en/latest/examples/complete_capacity_test.html

#import captest as pvc
from captest import capdata as pvc
from bokeh.io import output_notebook, show

# uncomment below two lines to use cptest.scatter_hv in notebook
import holoviews as hv
hv.extension('bokeh')

#if working offline with the CapData.plot() method may fail
#run 'export BOKEH_RESOURCES=inline' at the command line before
#running the jupyter notebook

output_notebook()


# In[5]:


samfile = 'Results_pySAM_00.csv'
#samfile = 'Row9_SAM_60_Comb_00a.csv'


# In[6]:


# Open the SAM simulation file, and save to the Analysis/data folder with updated header names

df = pd.read_csv(r'../SAM/Results/'+ samfile)
weatherfile = os.path.join(Path(os.getcwd()).parent,InputFilesFolder,'WF_SAM_00.csv')
df_weather = pd.read_csv(weatherfile, skiprows=2)

# remove duplicate columns if they exist
cols_to_use = df_weather.columns.difference(df.columns)
df = pd.merge(df, df_weather[cols_to_use], left_index=True, right_index=True, how='outer')

print(df.head())


# In[7]:


print(df.columns)


# In[8]:


# set index and rename columns to something Captest will understand
df.rename(columns={'Tdry':'Tamb', 'Wspd':'Wind'}, inplace=True)
df.rename(columns=lambda x: re.sub('Power','power_dc_inv', x), inplace=True)
df.rename(columns=lambda x: re.sub('CellTemp','tmod', x), inplace=True)
df.rename(columns=lambda x: re.sub('Rear','rear_irr', x), inplace=True)
df.rename(columns=lambda x: re.sub('Front','poa', x), inplace=True)

#raw_data = raw_data.rename(columns=lambda x: re.sub(' $','',x))
print(df.columns)


# In[9]:


df.index = pd.to_datetime(df_weather.iloc[:,0:4])  # use YYYY-MM-DD HH:MM index
df = df.loc[:,~df.columns.str.startswith('Unnamed:')]  # remove empty columns
df.to_csv(r'data/'+ samfile)


# In[24]:


# load the data from file into the captest object
sam = pvc.CapData('sim')
sam.load_data(fname=samfile, source='AlsoEnergy')  # the AlsoEnergy flag is needed to make this work.

sam.review_column_groups()
print(sam.regression_formula)
regression_formula0 = sam.regression_formula
regression_formula_tmod = 'power ~ poa + I(poa * poa)+ I(poa * t_amb) - 1'


# ## Captest subroutines

# In[11]:



def setupSAM(sam0, date):
    sam = deepcopy(sam0)

    # loop through, and save a DF `rc_out` with sam.rc for each timestamp
    sam.reset_filter()
    sam.filter_outliers()

    sam.fit_regression(filter=True, summary=False)

    sam.filter_time(test_date=date.strftime('%Y-%m-%d'), days=7)  # was 14
    sam.filter_irr(200, 930)
    rcs = sam.rep_cond(inplace=False)
    sam.rc = rcs  #suppress printing of rc's
    sam.rc.index=[date]#.strftime('%Y-%m-%d')
    

    # filter irradiance around RC's
    sam.filter_irr(0.5, 1.5, ref_val=sam.rc['poa'][0])

    #filter_report_sam = sam.get_summary()
    sam.fit_regression(summary=False)
    #sam.scatter_hv()
    return sam


def setupDAS(das0, date, poa):
    das = deepcopy(das0)
    das.reset_filter()
    das.filter_time(test_date=date, days=7)  # was 10

    das.filter_outliers()

    das.filter_irr(0.5, 1.5, ref_val=poa)  # filter around +/- 50% of POA RC's.  sam.rc['poa'][0]
    das.fit_regression(filter=True, summary=False)
    #filter_report_das = das.get_summary()
    das.fit_regression(summary=False)
    #das.scatter_hv(timeseries=True)
    return das

def saveFilter(df, samfile, rownum, print_results=False):
    # df: output dataframe with compiled SAM and DAS columns
    # save filtering details for each run
    filter_out = pd.DataFrame()
    for (index,row) in df.iterrows():
        temp = pvc.get_summary(row.DAS, row.SAM)
        #print(temp.columns)
        #print(temp.index)
        #print(temp)
        #newindex = pd.MultiIndex.from_tuples(date,temp.index)
        temp['date'] = row.date.strftime('%Y-%m-%d')
        temp.set_index('date', append=True, inplace=True)
        filter_out = pd.concat([filter_out, temp])
    filter_out.to_csv(os.path.join('results',f'filter_out_{samfile}_row{rownum}'))
    if print_results:
        print(filter_out.to_markdown())


# In[12]:


def runCaptest(sam, das, samfile, rownum):

    # Divide year into n=12 increments for sequential cap test
    #rc_out = pd.DataFrame(columns=['poa','t_amb','w_vel'])
    sam_list = pd.DataFrame()
    l = das.data.index.__len__()
    n=24
    index = np.linspace(l/(2*n),l*(2*n-1)/(2*n), n).round()
    datelist = [das.data.index[int(i)] for i in index]

    sam_df = pd.DataFrame([[setupSAM(sam,k)] for k in datelist], index=[k for k in datelist], columns = ['SAM'])
    
    rc_out = pd.concat([a.rc for a in sam_df.SAM])
    #print(rc_out)
    
    das_df = pd.DataFrame([[setupDAS(das,index,row.poa)] for (index,row) in rc_out.iterrows()], 
                      index=[index for (index,row) in rc_out.iterrows()], columns = ['DAS'])

    df = pd.concat([sam_df, das_df, rc_out], axis=1)
    df['date'] = df.index
    #print(df)
    
    saveFilter(df, samfile, rownum)
    
    # Save regression comparison for each timepoint
    results_SAM = pd.DataFrame(pd.concat([row.SAM.regression_results.predict(row.SAM.rc) for (index,row) in df.iterrows()]),
                              columns=['SAM_test'])
    results_DAS = pd.DataFrame(pd.concat([row.DAS.regression_results.predict(row.SAM.rc) for (index,row) in df.iterrows()]),
                              columns=['DAS_test'])

    results_out = pd.concat([results_SAM,results_DAS], axis=1)
    results_out['ratio'] = results_out.DAS_test / results_out.SAM_test
    results_out.to_csv(os.path.join('results',f'captest_out_{samfile}_row{rownum}'))
    
    return results_out, df


# In[13]:


def plotAlbedo(results_out, df, rownum, title_text=''):
    # plot comparison vs albedo. Average albedo for each interval
    #print(das.data.columns)
    albedo = das.data.albedo_down / das.data.albedo_up
    albedo = albedo.fillna(0.99).clip(lower=0.01,upper=0.99)[das.data.albedo_up > 20]
    #plt.plot(albedo)
    index = results_out.index
    grouper = index[index.searchsorted(albedo.index)-1]
    alb2 = albedo.groupby(grouper).mean()

    fig, ax1 = plt.subplots()
    ax1.plot(results_out.ratio)
    ax2 = ax1.twinx()
    ax2.plot(alb2,'r')
    ax1.set_ylabel('Cap test ratio', color='b')
    ax2.set_ylabel('Albedo', color='r')
    fig.autofmt_xdate()
    plt.title(f'Row{rownum} {title_text}')
    plt.savefig(os.path.join('images',f'Row{rownum}{title_text}_Captest.png'))
    
def savePowervPOA(df, rownum, text=''):
    for (index, row) in df.iterrows():
        plot1 = row.DAS.scatter_hv().relabel('DAS')
        plot1_test = hv.Points([[ row.poa, results_out.loc[index].DAS_test ]]).opts(color='blue', marker='triangle', size=20)


        plot2 = row.SAM.scatter_hv().relabel('SAM')
        plot2_test = hv.Points([[  row.poa, results_out.loc[index].SAM_test ] ]).opts(color='red', marker='square', size=15)

        plot = plot1 * plot2 * plot1_test * plot2_test
        plot.label=row.date.strftime('%Y-%m-%d')
        hv.save(plot, os.path.join('images',f'Row{rownum}{text}_PvsPOA_{plot.label}.png'), fmt='png')
        #plot


# ## Set up regression details for the run of Row 8

# In[25]:


rownum = 8

sam.set_regression_cols(power=f'power_dc_inv{rownum}', poa=f'poa{rownum}', t_amb='temp-amb-', w_vel='wind--')
sam.regression_formula = regression_formula0
# Load 15-minute field data, 6/1/21 - 5/31/22
das = pvc.CapData('das')
das.load_data(fname='Rows2-9_2021-2022_15T.csv', source='AlsoEnergy')  # the AlsoEnergy flag is needed to make this work.

das.data = das.data[(das.data['Gfront_poa'].notna())&(das.data[f'power_dc_inv{rownum}'].notna())&(das.data['row2wind_speed'].notna())] 
das.regression_formula = regression_formula0
das.set_regression_cols(power=f'power_dc_inv{rownum}', poa='Gfront_poa', t_amb='temp-amb-', w_vel='wind--')

#das.review_column_groups()

(results_out, df) = runCaptest(sam, das, samfile, rownum)

plotAlbedo(results_out, df, rownum, 'monofacial')
savePowervPOA(df, rownum)


# In[28]:


## look at row 8 but with back-of-module temperature.  update regression formula to remove windspeed. Hardly any difference
rownum = 8

sam.regression_formula = regression_formula_tmod
sam.set_regression_cols(power=f'power_dc_inv{rownum}', poa=f'poa{rownum}', t_amb='tmod8', w_vel='wind--')
# Load 15-minute field data, 6/1/21 - 5/31/22
das = pvc.CapData('das')
das.load_data(fname='Rows2-9_2021-2022_15T.csv', source='AlsoEnergy')  # the AlsoEnergy flag is needed to make this work.

das.data = das.data[(das.data['Gfront_poa'].notna())&(das.data[f'power_dc_inv{rownum}'].notna())&(das.data['row2wind_speed'].notna())] 

das.regression_formula = regression_formula_tmod
das.set_regression_cols(power=f'power_dc_inv{rownum}', poa='Gfront_poa', t_amb='row8tmod_2', w_vel='wind--')

#das.review_column_groups()

(results_out, df) = runCaptest(sam, das, samfile, rownum)

plotAlbedo(results_out, df, rownum, 'Tmod')
savePowervPOA(df, rownum, 'Tmod')

# revert regression formula back to include wspd for remaining runs
sam.regression_formula = regression_formula0
das.regression_formula = regression_formula0


# ## Set up regression details for the run of Row 9 - POA front

# In[29]:


rownum = 9

sam.set_regression_cols(power=f'power_dc_inv{rownum}', poa=f'poa{rownum}', t_amb='temp-amb-', w_vel='wind--')

# Load 15-minute field data, 6/1/21 - 5/31/22
das = pvc.CapData('das')
das.load_data(fname='Rows2-9_2021-2022_15T.csv', source='AlsoEnergy')  # the AlsoEnergy flag is needed to make this work.

das.data = das.data[(das.data['Gfront_poa'].notna())&(das.data[f'power_dc_inv{rownum}'].notna())&(das.data['row2wind_speed'].notna())] 

das.set_regression_cols(power=f'power_dc_inv{rownum}', poa='Gfront_poa', t_amb='temp-amb-', w_vel='wind--')

#das.review_column_groups()

(results_out, df) = runCaptest(sam, das, samfile, rownum)

plotAlbedo(results_out, df, rownum, 'Front POA only')
savePowervPOA(df, rownum, 'FrontPOA')


# ## Set up regression details for the run of Row 9 - Gtotal
# 
# 
# 
# 

# In[17]:


das.data.columns


# In[18]:


rownum = 9

sam.data['Gtotal'] = sam.data[f'poa{rownum}']+sam.data[f'rear_irr{rownum}']*0.85

sam.set_regression_cols(power=f'power_dc_inv{rownum}', poa='Gtotal', t_amb='temp-amb-', w_vel='wind--')
# Load 15-minute field data, 6/1/21 - 5/31/22
das = pvc.CapData('das')
das.load_data(fname='Rows2-9_2021-2022_15T.csv', source='AlsoEnergy')  # the AlsoEnergy flag is needed to make this work.

das.data = das.data[(das.data['Gfront_poa'].notna())&(das.data[f'power_dc_inv{rownum}'].notna())&(das.data['row2wind_speed'].notna())] 

das.data['Gtotal'] = das.data['Gfront_poa']+das.data['Grear']*0.85

das.set_regression_cols(power=f'power_dc_inv{rownum}', poa='Gtotal', t_amb='temp-amb-', w_vel='wind--')

#das.review_column_groups()

(results_out, df) = runCaptest(sam, das, samfile, rownum)

plotAlbedo(results_out, df, rownum, 'Gtotal')
savePowervPOA(df, rownum, 'Gtotal')


# ## Look at Row2 - both POA only and Gtotal
# 

# In[19]:


rownum = 2

sam.set_regression_cols(power=f'power_dc_inv{rownum}', poa=f'poa{rownum}', t_amb='temp-amb-', w_vel='wind--')
# Load 15-minute field data, 6/1/21 - 5/31/22
das = pvc.CapData('das')
das.load_data(fname='Rows2-9_2021-2022_15T.csv', source='AlsoEnergy')  # the AlsoEnergy flag is needed to make this work.

das.data = das.data[(das.data['Gfront_poa'].notna())&(das.data[f'power_dc_inv{rownum}'].notna())&(das.data['row2wind_speed'].notna())] 

das.set_regression_cols(power=f'power_dc_inv{rownum}', poa='Gfront_poa', t_amb='temp-amb-', w_vel='wind--')

#das.review_column_groups()

(results_out, df) = runCaptest(sam, das, samfile, rownum)

plotAlbedo(results_out, df, rownum, 'Front POA only')
savePowervPOA(df, rownum, 'FrontPOA')


# In[20]:


rownum = 2

sam.data['Gtotal'] = sam.data[f'poa{rownum}']+sam.data[f'rear_irr{rownum}']*0.69
sam.set_regression_cols(power=f'power_dc_inv{rownum}', poa='Gtotal', t_amb='temp-amb-', w_vel='wind--')
# Load 15-minute field data, 6/1/21 - 5/31/22
das = pvc.CapData('das')
das.load_data(fname='Rows2-9_2021-2022_15T.csv', source='AlsoEnergy')  # the AlsoEnergy flag is needed to make this work.

das.data = das.data[(das.data['Gfront_poa'].notna())&(das.data[f'power_dc_inv{rownum}'].notna())&(das.data['row2wind_speed'].notna())] 

das.data['Gtotal'] = das.data['Gfront_poa']+das.data['Grear']*0.85

das.set_regression_cols(power=f'power_dc_inv{rownum}', poa='Gtotal', t_amb='temp-amb-', w_vel='wind--')

#das.review_column_groups()

(results_out, df) = runCaptest(sam, das, samfile, rownum)

plotAlbedo(results_out, df, rownum, 'Gtotal')
savePowervPOA(df, rownum, 'Gtotal')

    
    


# ## Look at Row 4 both POA only and Gtotal

# In[21]:


rownum = 4

sam.set_regression_cols(power=f'power_dc_inv{rownum}', poa=f'poa{rownum}', t_amb='temp-amb-', w_vel='wind--')
# Load 15-minute field data, 6/1/21 - 5/31/22
das = pvc.CapData('das')
das.load_data(fname='Rows2-9_2021-2022_15T.csv', source='AlsoEnergy')  # the AlsoEnergy flag is needed to make this work.

das.data = das.data[(das.data['Gfront_poa'].notna())&(das.data[f'power_dc_inv{rownum}'].notna())&(das.data['row2wind_speed'].notna())] 

das.set_regression_cols(power=f'power_dc_inv{rownum}', poa='Gfront_poa', t_amb='temp-amb-', w_vel='wind--')

#das.review_column_groups()

(results_out, df) = runCaptest(sam, das, samfile, rownum)

plotAlbedo(results_out, df, rownum, 'Front POA only')
savePowervPOA(df, rownum, 'FrontPOA')


# In[22]:


rownum = 4

sam.data['Gtotal'] = sam.data[f'poa{rownum}']+sam.data[f'rear_irr{rownum}']*0.69
sam.set_regression_cols(power=f'power_dc_inv{rownum}', poa='Gtotal', t_amb='temp-amb-', w_vel='wind--')
# Load 15-minute field data, 6/1/21 - 5/31/22
das = pvc.CapData('das')
das.load_data(fname='Rows2-9_2021-2022_15T.csv', source='AlsoEnergy')  # the AlsoEnergy flag is needed to make this work.

das.data = das.data[(das.data['Gfront_poa'].notna())&(das.data[f'power_dc_inv{rownum}'].notna())&(das.data['row2wind_speed'].notna())] 

das.data['Gtotal'] = das.data['Gfront_poa']+das.data['Grear']*0.85

das.set_regression_cols(power=f'power_dc_inv{rownum}', poa='Gtotal', t_amb='temp-amb-', w_vel='wind--')

#das.review_column_groups()

(results_out, df) = runCaptest(sam, das, samfile, rownum)

plotAlbedo(results_out, df, rownum, 'Gtotal')
savePowervPOA(df, rownum, 'Gtotal')


# In[ ]:




