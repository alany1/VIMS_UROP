#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 21 14:13:46 2020

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


def write_cubes(master_directory,file_name):
    viewing_geometries = os.listdir(master_directory)
    file = open(file_name,'w')
    for folder in viewing_geometries:
        print(f'Working on folder {folder}')
        for cube in os.listdir(f'{master_directory}/{folder}'):
            if cube[0:2] != 'CM' or 'nav' in cube or 'BKGD' in cube:
                continue
            file.write(f'{master_directory}/{folder}/{cube}\n')
    return file_name

 
if __name__ == '__main__':
    
    PATH_TO_VIMS_WAVE = '/home/alanyu/Dropbox (MIT)/VIMS_UROP/vims_wave.txt' #change path
    vims_wave = np.loadtxt(PATH_TO_VIMS_WAVE)  
    
    MASTER_DIRECTORY = '/home/alanyu/Dropbox (MIT)/VIMS_UROP/data' #change path, directory containing viewing geometry folders
    FILE_NAME = 'cube_list.txt'
    
    write_cubes(MASTER_DIRECTORY,FILE_NAME)