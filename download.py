#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 27 12:29:06 2020

@author: aohma
"""

import cdflib # pip install cdflib
import pandas as pd
import numpy as np
import os
def validinput(inputstr, positive_answer, negative_answer):
    answer= input(inputstr+'\n').lower()
    if answer==positive_answer:
        return True
    elif answer== negative_answer:
        return False
    else:
        print('Invalid response should be either '+ str(positive_answer)+ ' or ' +str(negative_answer))
        return validinput(inputstr, positive_answer, negative_answer)
def download_omni_1min(fromYear,toYear,monthFirstYear=1,monthLastYear=12, path='./omni_1min.h5'):
    '''
    The function downloads omni 1min data and stores it in a hdf file. 
    
    Parameters
    ==========
    fromYear : int
        Download from and including fromYear
    toYear : int,
        Download to and including toYear
    monthFirstYear : int, default 1
        First month to include from the first year.
    monthLastYear : int, default 12
        Last month to include from the last year.
    '''
    
    if fromYear < 1981:
        raise ValueError('fromYear must be >=1981')
    if os.path.isfile(path):
        if not validinput('file already exists and more omni will be added which can lead to duplication of data continue? (y/n)', 'y', 'n'):
            raise ValueError('User Cancelled Download, Alter file name or path or remove or move the existing file and retry')
    years = np.arange(fromYear,toYear+1,1)
    months= []
    for i in np.arange(1,13,1): months.append('%02i' % i)
        
    for y in years:
        for m in months:
            if not ((y==years[0])& (int(m)<monthFirstYear)) | ((y==years[-1]) & (int(m)>monthLastYear)):
                command = 'wget https://cdaweb.gsfc.nasa.gov/sp_phys/data/omni/hro_1min/' + str(y) + \
                    '/omni_hro_1min_' + str(y) + str(m) + '01_v01.cdf'
                os.system(command)
                
                omni = pd.DataFrame()
                cdf_file = cdflib.CDF('omni_hro_1min_' + str(y) + str(m) + '01_v01.cdf')
                varlist = cdf_file.cdf_info()['zVariables']
                for v in varlist:
                    omni[v] = cdf_file.varget(v)
                    fillval = cdf_file.varattsget(v)['FILLVAL']
                    omni[v] = omni[v].replace(fillval,np.nan)
                omni.index = pd.to_datetime(cdflib.cdfepoch.unixtime(cdf_file.varget('Epoch')),unit='s')
                omni[['AE_INDEX','AL_INDEX','AU_INDEX', 'PC_N_INDEX']] = omni[['AE_INDEX','AL_INDEX','AU_INDEX', 'PC_N_INDEX']].astype('float64')
                omni.to_hdf(path,'omni',mode='a',append=True,format='t', data_columns=True)
                cdf_file.close()
                os.remove('omni_hro_1min_' + str(y) + str(m) + '01_v01.cdf')
    
