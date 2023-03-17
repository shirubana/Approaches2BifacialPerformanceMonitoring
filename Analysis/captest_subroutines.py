#!/usr/bin/env python
# coding: utf-8

# captest subroutines to leverage in jupyter analysis notebooks

# In[2]:


import pandas as pd
import matplotlib.pyplot as plt
import pvlib
import numpy as np
import os
import re
from pathlib import Path
from datetime import datetime
from copy import deepcopy
import time
starttime = time.time()

# pip install pvcaptest and holoviews if you don't have it installed already.
# following example from https://pvcaptest.readthedocs.io/en/latest/examples/complete_capacity_test.html

#import captest as pvc
from captest import capdata as pvc
from bokeh.io import output_notebook, show

# uncomment below two lines to use cptest.scatter_hv in notebook
import holoviews as hv
hv.extension('bokeh')



# ## Captest subroutines

# In[10]:



def setupSAM(sam0, date):
    sam = deepcopy(sam0)

    # loop through, and save a DF `rc_out` with sam.rc for each timestamp
    sam.reset_filter()
    sam.filter_outliers()

    sam.fit_regression(filter=True, summary=False)

    sam.filter_time(test_date=date, days=7)  # was 14 #.strftime('%Y-%m-%d')
    sam.filter_irr(200, 930)
    rcs = sam.rep_cond(inplace=False)
    # constant rcs. CDELINE: remove this line for variable RC's
    #rcs = pd.DataFrame({'poa':657, 't_amb':16, 'w_vel':2.2}, index=[0])
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
    
    # the integrated time filtering module just isn't working. have to DIY
    das.filter_time(test_date=date, days=7)  # was 10

    das.filter_outliers()

    das.filter_irr(0.5, 1.5, ref_val=poa)  # filter around +/- 50% of POA RC's.  sam.rc['poa'][0]
    das.fit_regression(filter=True, summary=False)
    #filter_report_das = das.get_summary()
    das.fit_regression(summary=False)
    #das.scatter_hv(timeseries=True)
    return das

def saveFilter(df, run, rownum, print_results=False):
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
    filter_out.to_csv(os.path.join('results','filter',f'filter_out_{run}_row{rownum}.csv'))
    if print_results:
        print(filter_out.to_markdown())


# In[11]:


def RMSE(ratios): # RMSE around average ratio
    return np.sqrt(np.mean((ratios-np.mean(ratios))**2))

def MBE(ratios):
    return np.mean(ratios-1)

def MAE(ratios):
    return np.mean(abs(ratios-1))

def runCaptest(sam, das, run, rownum):

    # Divide year into n=12 increments for sequential cap test
    #rc_out = pd.DataFrame(columns=['poa','t_amb','w_vel'])
    sam_list = pd.DataFrame()
    l = das.data.index.__len__()
    n=52
    index = np.linspace(l/n,l*(n-1)/(n), n-1).round()
    datelist = [das.data.index[int(i)] for i in index]

    sam_df = pd.DataFrame([[setupSAM(sam,k)] for k in datelist], index=[k for k in datelist], columns = ['SAM'])
    
    rc_out = pd.concat([a.rc for a in sam_df.SAM])
    #print(rc_out)
    
    das_df = pd.DataFrame([[setupDAS(das,index,row.poa)] for (index,row) in rc_out.iterrows()], 
                      index=[index for (index,row) in rc_out.iterrows()], columns = ['DAS'])

    df = pd.concat([sam_df, das_df, rc_out], axis=1)
    df['date'] = df.index
    #print(df)
    
    saveFilter(df, run, rownum)
    
    # Save regression comparison for each timepoint
    results_SAM = pd.DataFrame(pd.concat([row.SAM.regression_results.predict(row.SAM.rc) for (index,row) in df.iterrows()]),
                              columns=['SAM_test'])
    results_DAS = pd.DataFrame(pd.concat([row.DAS.regression_results.predict(row.SAM.rc) for (index,row) in df.iterrows()]),
                              columns=['DAS_test'])

    results_out = pd.concat([results_SAM,results_DAS], axis=1)
    results_out['ratio'] = results_out.DAS_test / results_out.SAM_test
    
    results_out.to_csv(os.path.join('results',f'captest_out_{run}_row{rownum}.csv'))
    
    return results_out, df


# In[12]:


def plotAlbedo(results_out, das, rownum, run, title_text='', plotval='ratio'):
    # plot comparison vs albedo. Average albedo for each interval
    #print(das.data.columns)
    albedo = das.data.albedo_down / das.data.albedo_up
    albedo = albedo.fillna(0.99).clip(lower=0.01,upper=0.99)[das.data.albedo_up > 20]
    #albedo_sam = sam.data.Albedo[sam.data.poa2 > 20] #.tz_localize('Etc/GMT+7')
    index = results_out.index
    grouper = index[index.searchsorted(albedo.index)-1]
    alb2 = albedo.groupby(grouper).mean()
    #grouper_sam = index[index.searchsorted(albedo_sam.index)-1]
    #alb2_sam = albedo_sam.groupby(grouper_sam).mean()

    fig, ax1 = plt.subplots()
    ax1.plot(results_out[plotval])
    ax2 = ax1.twinx()
    ax2.plot(alb2,'r')
    #ax2.plot(alb2_sam,'r:')
    ax1.set_ylabel('Cap test ratio', color='b')
    ax2.set_ylabel('Albedo', color='r')
    fig.autofmt_xdate()
    plt.title(f'Row{rownum} {title_text}. MBE: {MBE(results_out[plotval])*100:0.2f}%. RMSE: {RMSE(results_out[plotval])*100:0.2f}%. ' )
    plt.savefig(os.path.join('images',run,f'Row{rownum}{title_text}_Captest.png'))
    
def savePowervPOA(df, results_out, rownum, run, text=''):
    for (index, row) in df.iterrows():
        plot1 = row.DAS.scatter_hv().relabel('DAS')
        plot1_test = hv.Points([[ row.poa, results_out.loc[index].DAS_test ]]).opts(color='blue', marker='triangle', size=20)


        plot2 = row.SAM.scatter_hv().relabel('SAM')
        plot2_test = hv.Points([[  row.poa, results_out.loc[index].SAM_test ] ]).opts(color='red', marker='square', size=15)

        plot = plot1 * plot2 * plot1_test * plot2_test
        plot.label=row.date.strftime('%Y-%m-%d')
        hv.save(plot, os.path.join('images',run,f'Row{rownum}',f'Row{rownum}{text}_PvsPOA_{plot.label}.png'), fmt='png')
        #plot


# In[13]:





def runIEC(df, rownum, run, text='', gtotal=False):
    
    def pcorr(power, poa, tmod, rcs=None, gamma=-0.0035):
        if rcs is None:
            rcs = [1000, 25]
        return((power *(1-gamma*(tmod-rcs[1])) * rcs[0]/poa))
        #return power  # bypass the power correction
    
    if type(rownum)==str:
        text = rownum[1:]
        rownum = int(rownum[0])
        
    if rownum ==2:
        gamma = -0.004
    elif rownum==4:
        gamma = -0.0035
    elif rownum==8:
        gamma = -0.0038
    elif rownum==9:
        gamma = -0.0025
        
    IEClist = []
    result = zip(df.DAS, df.SAM)
    for (das0, sam0) in result:
        sam1 = sam0.data_filtered.resample('1h').mean()
        das1 = das0.data_filtered.resample('1h').mean()
        
        rcs = [sam1[f'poa{rownum}'].mean(), sam1[f'tmod{rownum}'].mean()]
        if gtotal:
            sam1['pcorr'] = pcorr(sam1[f'power_dc_inv{rownum}'], sam1[f'poa{rownum}']+0.7*sam1[f'rear_irr{rownum}'], sam1[f'tmod{rownum}'], rcs, gamma)
            das1['pcorr'] = pcorr(das1[f'power_dc_inv{rownum}'], das1.Gfront_poa+0.7*das1[f'Grear'], das1[f'row{rownum}tmod_2'], rcs, gamma)            
        else:
            sam1['pcorr'] = pcorr(sam1[f'power_dc_inv{rownum}'], sam1[f'poa{rownum}'], sam1[f'tmod{rownum}'], rcs, gamma)
            das1['pcorr'] = pcorr(das1[f'power_dc_inv{rownum}'], das1.Gfront_poa, das1[f'row{rownum}tmod_2'], rcs, gamma)

        pcorr_ratio = sam1.join(das1['pcorr'], how='inner', rsuffix='_das')
        pcorr_ratio['ratio'] = pcorr_ratio.pcorr_das /pcorr_ratio.pcorr

        pcorr_mean = pcorr_ratio.ratio.mean()
        #print(f' pcorr_ratio mean: {pcorr_mean}')
        
        fig =plt.figure()
        plt.plot(pcorr_ratio['pcorr_das'],'.',label='das')
        plt.plot(pcorr_ratio['pcorr'],'.',label='sam')
        plt.plot(pcorr_ratio['ratio'],'.',label='ratio')
        label = sam1.index[0].strftime('%Y-%m-%d')
        plt.title(f'P_corr {label}. Mean: {pcorr_mean:.3f}')
        fig.autofmt_xdate()
        plt.savefig(os.path.join('images',run,f'Row{rownum}{text}_IEC_{label}.png'))
        plt.close(fig)
        IEClist.append(pcorr_mean)
    
    return IEClist
        



