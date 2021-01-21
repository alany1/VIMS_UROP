#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 21 14:27:36 2020

@author: alanyu
"""

from IPython.core.display import HTML
import numpy as np
import matplotlib
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from pylab import *
import pysis
import os
import scipy.optimize as sco
import time


def gaussian(x,mean,sigma,A):
    
    return A*np.exp( -((x-mean)**2.) / (2.*sigma**2.) )

def powerlaw(x,a, k, c):
    
    return a*x**k + c

def analyze_cube(cube,nav,l,w):
    """
    Given cube data (cube) and navigation information (nav) with dimensions x and y, returns:
    
    1) max/min 2 micron amplitude
    2) max/min sigma
    3) max/min mean 
    4) max/min incidence
    5) max/min emission
    6) max/min phase
    7) max/min lat
    8) max/min lon
    """
    
    count=0
    band_channels = [29,30,31,32,47,48,49,50,51,52,53,54,55,84,85,86,87,88,89,90] + [i for i in range(160,181)] 
    
    info = np.full((40,l,w),None)
    #0: key (0 = good, 1 = off disk, 2 = low resolution, 3 = bad powerlaw, 4 = dark, 5 = bad incidence/emission), 6 = completely failed 
    #1-6: best fit (1-3: gaussian mean,sigma,amp; 4-6: plaw amp,exp,const)
    #7-32: raw data channel 60:85
    #32-40: phase,emission,incidence, lat, lon, resolution,spacecraft azimuth, solar azimuth
    

    info[7:32]=cube[60:85]
    info[32:35] = nav[1:4]
    info[35:38] = nav[6:9]
    info[38:] = nav[16:18]

    for i in range(l):
        for j in range(w):
            
            if nav[6,i,j] < -90:  
                count+=1
                info[0,i,j] = 1
                continue
            elif nav[8,i,j]>100000:
                info[0,i,j] = 2
            elif cube[69,i,j]<=0.02:
                info[0,i,j] = 4
            elif nav[2,i,j]>70 or nav[3,i,j]>70:
                info[0,i,j] = 5
            
            
            

            try:
                #Fit power law
                p_fit, p_cov = sco.curve_fit(powerlaw, vims_wave[band_channels], cube[band_channels, i,j], p0 = (.005,-2,0), maxfev = 10000)
                p = powerlaw(vims_wave, *p_fit)

                #Subtract power law
                new_data = cube[:,i,j] - p

                #Fit gaussian
                fit,cov = sco.curve_fit(gaussian, vims_wave[64:85],new_data[64:85], \
                                    p0=(2.08,.125,.1), maxfev=100000)

                info[1,i,j] = fit[0]
                info[2,i,j] = fit[1]
                info[3,i,j] = fit[2]
                info[4,i,j] = p_fit[0]
                info[5,i,j] = p_fit[1]
                info[6,i,j] = p_fit[2]
                info[0,i,j] = 0


            except:
                #If powerlaw fit fails, directly fit gaussian
                info[0,i,j] = 3
                try:
                    fit,cov = sco.curve_fit(gaussian, vims_wave[64:85],cube[64:85,i,j], p0=(2.08,.125,.1), maxfev=1000000)
                    info[1,i,j] = fit[0]
                    info[2,i,j] = fit[1]
                    info[3,i,j] = fit[2]
                except:
                    info[0,i,j]=6
                    break


    return info

def create_cube_parser(cube_list,destination='cube_info'):
    '''
    Parameters:
    
    master_directory (str): Path to folder with all viewing geometries.
    
    Creates text file with information about each cube (assuming max resolution < 100km): 
    
    1) folder 
    2) name 
    3) max/min 2 micron amplitude
    4) max/min sigma
    5) max/min mean
    6) dimensions
    7) max/min incidence
    8) max/min emission
    9) max/min phase
    10) max/min lat
    11) max/min lon
    
    '''
 

    skipped=set()
    file = open(cube_list,'r')
    
    while True:
        
        
        cube_path = file.readline().strip()
        
        if not cube_path:
            break
            
        nav = pysis.CubeFile(f'{cube_path[:-4]}_nav.cub').data


        print(f'Working on: {cube_path}')
            
            
        
        name = cube_path.split('/')[-1]
        
        data = pysis.CubeFile(cube_path).data

        lbl = pysis.CubeFile(cube_path).label
        length=lbl['IsisCube']['Instrument']['SwathLength']
        width=lbl['IsisCube']['Instrument']['SwathWidth']

        info = analyze_cube(data,nav,length,width)

        length = f'0{length}' if length < 10 else length
        width = f'0{width}' if width < 10 else width
        np.save(os.path.join(destination, f'{name}-{length}x{width}.npy'),info)
          
    file.close()  

    return skipped

if __name__ == '__main__':
    
    PATH_TO_VIMS_WAVE = '/home/alanyu/Dropbox (MIT)/VIMS_UROP/vims_wave.txt' #change path
    vims_wave = np.loadtxt(PATH_TO_VIMS_WAVE)  
    
    CUBE_LIST_PATH = '/home/alanyu/Dropbox (MIT)/VIMS_UROP/cube_list.txt' #change this path
    OUTPUT_PATH = 'cube_info' #name of directory to write to, need to mkdir first 
    
    create_cube_parser(CUBE_LIST_PATH, OUTPUT_PATH)
    
    