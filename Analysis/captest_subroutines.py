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
# NOTE: code is designed for captest v 0.10.0.   It won't work with latest 0.11.2

#import captest as pvc
from captest import capdata as pvc
from bokeh.io import output_notebook, show

# uncomment below two lines to use cptest.scatter_hv in notebook
import holoviews as hv
hv.extension('bokeh')



# ## Captest subroutines

# In[10]:



def setupSAM(sam0, date, rcs=None):
    """
    
    

    Parameters
    ----------
    sam0 : PVCaptest object
        DESCRIPTION.
    date : datetime
        DESCRIPTION.
    rcs : pd.DataFrame, keys 'poa', 't_amb', 'w_vel', optional
        DESCRIPTION. The default is None.

    Returns
    -------
    sam : TYPE
        DESCRIPTION.

    """

    
    sam = deepcopy(sam0)

    # loop through, and save a DF `rc_out` with sam.rc for each timestamp
    sam.reset_filter()
    
    
    sam.filter_time(test_date=date, days=8)  # was 14 #.strftime('%Y-%m-%d')
    sam.filter_outliers()
    sam.fit_regression(filter=True, summary=False)

    
    sam.filter_irr(20, 2000)
    
    if rcs is None:
        rcs = sam.rep_cond(inplace=False)
    # constant rcs. CDELINE: remove this line for variable RC's
    #rcs = pd.DataFrame({'poa':657, 't_amb':16, 'w_vel':2.2}, index=[0])
    sam.rc = rcs  #suppress printing of rc's
    sam.rc.index=[date]#.strftime('%Y-%m-%d')
    

    # filter irradiance around RC's. This can throw away too many points if RC's are small and data is sparse
    sam_old = deepcopy(sam)
    sam.filter_irr(0.5, 1.5, ref_val=sam.rc['poa'].iloc[0])
    data_points_old = sam.data_filtered.__len__() 
    if data_points_old <= 5:  # expand RC irradiance filter
        sam = sam_old
        sam.filter_irr(0.2, 2, ref_val=sam.rc['poa'].iloc[0])
        print(f'Irradiance filter window expanded b/c its too narrow. Old # points: {data_points_old}.  ' +
              f'New # points: {sam.data_filtered.__len__()}')
    
    
    #filter_report_sam = sam.get_summary()
    sam.fit_regression(summary=False)
    #regress_formula_new =  _checkPvals(sam.regression_results, sam.regression_formula)  # only use model params with pval < 0.05
    #if regress_formula_new != sam.regression_formula:
    #    print(f'Date: {date}. Regression: {regress_formula_new}')
    #    sam.regression_formula = regress_formula_new
    #    sam.fit_regression(summary=False)
    #sam.scatter_hv()
    return sam


def setupDAS(das0, date, poa):
    das = deepcopy(das0)
    das.reset_filter()
    
    # the integrated time filtering module just isn't working. have to DIY
    das.filter_time(test_date=date, days=8)  # was 7

    das.filter_outliers()
    das.fit_regression(filter=True, summary=False)
    
    das.filter_irr(0.5, 1.5, ref_val=poa)  # filter around +/- 50% of POA RC's.  sam.rc['poa'][0]
    
    #filter_report_das = das.get_summary()
    das.fit_regression(summary=False)
    #regress_formula_new =  _checkPvals(das.regression_results, das.regression_formula)  # only use model params with pval < 0.05
    #if regress_formula_new != das.regression_formula:
    #    print(f'Date: {date}. Regression: {regress_formula_new}')
    #    das.regression_formula = regress_formula_new
    #    das.fit_regression(summary=False)
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
def _checkPvals(regression_results, regression_formula):
    # remove regression_formula params if pval > 0.05
    for i in range(regression_results.params.__len__()):
        if regression_results.pvalues[i] > 0.05:
            #print(f'{regression_results.params.index[i]} = 0')
            regression_formula = regression_formula.replace(f'+ {regression_results.params.index[i]}', '')   
    return regression_formula

def RMSE(ratios): # RMSE around average ratio
    return np.sqrt(np.mean((ratios-np.mean(ratios))**2))

def MBE(ratios):
    return np.mean(ratios-1)

def MAE(ratios):
    return np.mean(abs(ratios-1))


def runCaptest(sam, das, run, rownum, rcs=None):

    # Divide year into n=12 increments for sequential cap test
    if rcs is None:
        monthlyRCS = get_monthlyRC(sam)
    
    def _getrcs(rcs,k):
        if rcs is None:
            return pd.DataFrame(monthlyRCS.loc[k.month]).T
        else:
            return pd.DataFrame(rcs.loc[k]).T
        
    
    #sam_list = pd.DataFrame()
    l = das.data.index.__len__()
    n=52
    index = np.linspace(l/n,l*(n-1)/(n), n-1).round()
    datelist = [das.data.index[int(i)] for i in index]
    

    sam_df = pd.DataFrame([[setupSAM(sam,k, _getrcs(rcs,k))] for k in datelist], index=[k for k in datelist], columns = ['SAM'])
    
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

    results_sigmaMC = pd.DataFrame([_monteCarlo(row.SAM.regression_results, row.SAM.rc) for (index,row) in df.iterrows()],
                              columns=['SAM_model_1sigma_pct'], index=results_SAM.index)
    results_out = pd.concat([results_SAM,results_DAS,results_sigmaMC], axis=1)
    results_out['ratio'] = results_out.DAS_test / results_out.SAM_test
    results_out = results_out.join(rc_out)
    results_out.to_csv(os.path.join('results',f'captest_out_{run}_row{rownum}.csv'))
    
    return results_out, df


# In[12]:
def get_monthlyRC(SAM):
    
    def _filterRC(SAM,start, end):
        #start : str or pd.Timestamp or None, default None
        #end : str or pd.Timestamp or None, default None
        sam = deepcopy(SAM)
        sam.reset_filter()
        sam.filter_time(start=start, end=end)  
        sam.filter_outliers()
        sam.fit_regression(filter=True, summary=False)
        sam.filter_irr(20, 2000)
        rcs = sam.rep_cond(inplace=False)
        return rcs
    
    #rcs_out = pd.DataFrame(range(1,13))
    for n in range(1,13): 
        temp_dates = SAM.data.index[SAM.data.index.month==n]
        temp  = _filterRC(SAM,temp_dates.min(),temp_dates.max()) 
        temp.index=[n]
        if n==1:
            rcs_out = temp
        else:
            rcs_out = pd.concat([rcs_out, temp])
    
    return rcs_out

        

def _monteCarlo(results, rc):
    # bootstrap monte carlo on a statsmodels.regression.linear_model object
    # take advantage of results.conf_int() at the reference condition
    def p_regress(val, rc):
        REGRESSION_PARAMS = [rc.poa,rc.poa**2,rc.poa*rc.t_amb,rc.poa*rc.w_vel]
        p_out = sum([(v*REGRESSION_PARAMS[i]) for (i,v) in enumerate(val)])
        #p_out = val[0]*rc.poa + val[1]*(rc.poa**2) + val[2]*(rc.poa*rc.t_amb) + val[3]*(rc.poa*rc.w_vel)
        return p_out
    N = 500
    sigma = abs(results.conf_int(alpha = 0.05).iloc[:,1]-results.conf_int(alpha = 0.05).iloc[:,0])/4
    loc = results.params
    val_out = []
    for i in range(N):
        val= np.random.normal(loc=loc, scale=sigma)
        val_out.append(p_regress(val,rc))
    sigma_out = np.std(val_out)
    mean = np.mean(val_out)
    return(sigma_out/mean)
    
    


def plotAlbedo(results_out, das, rownum, run, title_text='', plotval='ratio'):
    # plot comparison vs albedo. Average albedo for each interval
    #print(das.data.columns)
    albedo = das.data.albedo_down / das.data.albedo_up
    albedo = albedo.fillna(0.99).clip(lower=0.01,upper=0.99)[das.data.albedo_up > 20]
    #albedo_sam = sam.data.Albedo[sam.data.poa2 > 20] #.tz_localize('Etc/GMT+7')
    index = results_out.index
    grouper = index[index.searchsorted(albedo.index)-1]
    alb2 = albedo.groupby(grouper).mean(numeric_only=True)
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
    if not os.path.exists(os.path.join('images',run)):
        os.makedirs(os.path.join('images',run))
    plt.savefig(os.path.join('images',run,f'Row{rownum}{title_text}_Captest.png'))
    
def savePowervPOA(df, results_out, rownum, run, text=''):
    for (index, row) in df.iterrows():
        plot1 = row.DAS.scatter_hv().relabel('DAS')
        plot1_test = hv.Points([[ row.poa, results_out.loc[index].DAS_test ]]).opts(color='blue', marker='triangle', size=20)


        plot2 = row.SAM.scatter_hv().relabel('SAM')
        plot2_test = hv.Points([[  row.poa, results_out.loc[index].SAM_test ] ]).opts(color='red', marker='square', size=15)

        plot = plot1 * plot2 * plot1_test * plot2_test
        plot.label=row.date.strftime('%Y-%m-%d')
        if not os.path.exists(os.path.join('images',run,f'Row{rownum}')):
            os.makedirs(os.path.join('images',run,f'Row{rownum}'))
        hv.save(plot, os.path.join('images',run,f'Row{rownum}',f'Row{rownum}{text}_PvsPOA_{plot.label}.png'), fmt='png')
        #plot


# In[13]:





def runIEC(df, rownum, run, text='', gtotal=False):
    
    def pcorr(power, poa, tmod, rcs=None, gamma=-0.0035):
        if rcs is None:
            rcs = [1000, 25]
        #return((power *(1-gamma*(tmod-rcs[1])) * rcs[0]/poa))
        return power  # bypass the power correction
    
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
        sam1 = sam0.data_filtered.resample('1h').mean(numeric_only=True)
        das1 = das0.data_filtered.resample('1h').mean(numeric_only=True)
        
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
        plt.legend()
        fig.autofmt_xdate()
        plt.savefig(os.path.join('images',run,f'Row{rownum}{text}_IEC_{label}.png'))
        plt.close(fig)
        IEClist.append(pcorr_mean)
    
    return IEClist
        




