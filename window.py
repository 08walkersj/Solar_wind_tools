#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 16 09:56:54 2021

@author: simon
"""
import pandas as pd
import numpy as np
from progressbar import progressbar

#engine_kwargs= {'nopython':True, 'nogil':False, 'parallel': True}
def circular_variance(file_path, save_path, window=30):
    window+=1
    def sin(theta):
        return np.nanmean(np.sin(theta))**2
    def cos(theta):
        return np.nanmean(np.cos(theta))**2
    def Variance(X):
        X=X[np.isfinite(X)]
        if len(X)<=1:
            return np.nan
        else:
            return np.nansum((X-np.nanmean(X))**2)/(len(X)-1)
    omni= pd.read_hdf(file_path)
    columns= ['IMF','BX_GSE', 'BY_GSM', 'BZ_GSM']
    for column in progressbar(columns, max_value= len(columns)):
        omni[column+'_Var']= omni[column].rolling(window=window,min_periods=0).apply(Variance, engine='numba', raw=True)
        omni[column+'_Mean']= omni[column].rolling(window=window,min_periods=0).apply(np.nanmean, engine='numba', raw=True)
    omni['Clock_GSM']= np.arctan2(omni.BY_GSM, omni.BZ_GSM)
    omni['Clock_GSM_Mean']= omni.Clock_GSM.rolling(window=window, min_periods=0).apply(np.nanmean, engine='numba', raw=True)
    tmp= pd.DataFrame({'Theta': np.arctan2(omni['BY_GSM'], omni['BZ_GSM'])}).rolling(window=window,min_periods=0)
    omni['Circular_Variance_GSM']= 1- np.sqrt(tmp.apply(sin, engine='numba', raw=True) + tmp.apply(cos, engine='numba', raw=True))
    omni.to_hdf(save_path, key='main')
def coupling(file_path, save_path, window=30):
    window+=1
    data= pd.read_hdf(file_path)
    from Coupling_Functions import newell_coupling_function
    data['Newell_Episilon']= newell_coupling_function(data.Vx, data.BY_GSM, data.BZ_GSM)
    data['Newell_Episilon_Mean']= data.Newell_Episilon.rolling(window=window, min_periods=0).apply(np.nanmean, engine='numba', raw=True)
    data.to_hdf(save_path, key='main')
def dipole(file_path, save_path, window=30):
    import dipole
    data= pd.read_hdf(file_path)
    years= data.index.year
    data['Dipole_Tilt']=np.concatenate([dipole.dipole_tilt(data.index.values[years==year], year) for year in np.unique(years)])
    data.to_hdf(save_path, key='main')
def time_shift(file_path, save_path, start=20, end=10):
    data= pd.read_hdf(file_path)
    for col in data.columns:
        if col.endswith('_Mean') or col.endswith('_Var'):
            data[col]= data[col].shift(-end)
    data.to_hdf(save_path, key='main')

