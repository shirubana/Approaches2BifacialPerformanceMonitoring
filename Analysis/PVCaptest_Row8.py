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


# In[10]:


# load the data from file into the captest object
sam = pvc.CapData('sim')
sam.load_data(fname=samfile, source='AlsoEnergy')  # the AlsoEnergy flag is needed to make this work.

sam.review_column_groups()


# ## Set up regression details for the run

# In[11]:


rownum = 8

sam.set_regression_cols(power=f'power_dc_inv{rownum}', poa=f'poa{rownum}', t_amb='temp-amb-', w_vel='wind--')
# Load 15-minute field data, 6/1/21 - 5/31/22
das = pvc.CapData('das')
das.load_data(fname='Rows2-9_2021-2022_15T.csv', source='AlsoEnergy')  # the AlsoEnergy flag is needed to make this work.

das.data = das.data[(das.data['Gfront_poa'].notna())&(das.data[f'power_dc_inv{rownum}'].notna())&(das.data['row2wind_speed'].notna())] 

das.set_regression_cols(power=f'power_dc_inv{rownum}', poa='Gfront_poa', t_amb='temp-amb-', w_vel='wind--')

#das.review_column_groups()


# In[ ]:





# In[12]:



def setupSAM(sam0, date):
    sam = deepcopy(sam0)

    # loop through, and save a DF `rc_out` with sam.rc for each timestamp
    sam.reset_filter()
    sam.filter_outliers()

    sam.fit_regression(filter=True, summary=False)

    sam.filter_time(test_date=date.strftime('%Y-%m-%d'), days=15)  #'03/11/2020'
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
    das.filter_time(test_date=date, days=10)  #'03/11/2020'

    das.filter_outliers()

    das.filter_irr(0.5, 1.5, ref_val=poa)  # filter around +/- 50% of POA RC's.  sam.rc['poa'][0]
    das.fit_regression(filter=True, summary=False)
    #filter_report_das = das.get_summary()
    das.fit_regression(summary=False)
    #das.scatter_hv(timeseries=True)
    return das


# In[13]:


# Divide year into n=12 increments for sequential cap test
#rc_out = pd.DataFrame(columns=['poa','t_amb','w_vel'])
sam_list = pd.DataFrame()
l = das.data.index.__len__()
n=12
index = np.linspace(l/(2*n),l*(2*n-1)/(2*n), n).round()
datelist = [das.data.index[int(i)] for i in index]

sam_df = pd.DataFrame([[setupSAM(sam,k)] for k in datelist], index=[k for k in datelist], columns = ['SAM'])


# In[14]:



#print([a for a in A.SAM])
rc_out = pd.concat([a.rc for a in sam_df.SAM])
print(rc_out)


# In[15]:





# In[16]:


das_df = pd.DataFrame([[setupDAS(das,index,row.poa)] for (index,row) in rc_out.iterrows()], 
                      index=[index for (index,row) in rc_out.iterrows()], columns = ['DAS'])


# In[17]:


df = pd.concat([sam_df, das_df, rc_out], axis=1)
df['date'] = df.index
print(df)


# In[18]:


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
print(filter_out.to_markdown())


# In[19]:


# pvcaptest has a comparison, but it doesn't save the data.  Need to calculate manually...
ratio = pvc.captest_results(row.SAM, row.DAS, 6,  '+/- 7')


# In[20]:


# Save regression comparison for each timepoint

results_SAM = pd.DataFrame(pd.concat([row.SAM.regression_results.predict(row.SAM.rc) for (index,row) in df.iterrows()]),
                          columns=['SAM_test'])
results_DAS = pd.DataFrame(pd.concat([row.DAS.regression_results.predict(row.SAM.rc) for (index,row) in df.iterrows()]),
                          columns=['DAS_test'])

results_out = pd.concat([results_SAM,results_DAS], axis=1)
results_out['ratio'] = results_out.DAS_test / results_out.SAM_test
results_out.to_csv(os.path.join('results',f'captest_out_{samfile}_row{rownum}'))



# In[ ]:





# In[21]:


# plot comparison vs albedo. Average albedo for each interval
print(das.data.columns)
albedo = das.data.albedo_down / das.data.albedo_up
albedo = albedo.fillna(0.99).clip(lower=0.01,upper=0.99)[das.data.albedo_up > 20]
plt.plot(albedo)
index = results_out.index
grouper = index[index.searchsorted(albedo.index)-1]
alb2 = albedo.groupby(grouper).mean()


# In[26]:


fig, ax1 = plt.subplots()
ax1.plot(results_out.ratio)
ax2 = ax1.twinx()
ax2.plot(alb2,'r')
ax1.set_ylabel('Cap test ratio', color='b')
ax2.set_ylabel('Albedo', color='r')
fig.autofmt_xdate()
plt.title(f'Row{rownum}')


# In[23]:


# save Power vs POA plots for each time interval.  To suppress warnings, do pip install holoviews==1.14.9  (warnings show up in 1.15)

for (index, row) in df.iterrows():
    plot1 = row.DAS.scatter_hv().relabel('DAS')
    plot1_test = hv.Points([[ row.poa, results_out.loc[index].DAS_test ]]).opts(color='blue', marker='triangle', size=20)
                           

    plot2 = row.SAM.scatter_hv().relabel('SAM')
    plot2_test = hv.Points([[  row.poa, results_out.loc[index].SAM_test ] ]).opts(color='red', marker='square', size=15)

    plot = plot1 * plot2 * plot1_test * plot2_test
    plot.label=row.date.strftime('%Y-%m-%d')
    hv.save(plot, os.path.join('images',f'Row{rownum}_PvsPOA_{plot.label}.png'), fmt='png')
    #plot
    
    


# In[24]:


plot


# In[25]:


print(row)
results_out.loc[index].SAM_test


# In[ ]:





# In[ ]:




