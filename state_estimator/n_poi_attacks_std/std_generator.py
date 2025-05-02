import json
import numpy as np
from lib_timeseries import system_topology
import re


# Reading network topology
Nodes, Lines = system_topology('../../data/pv_2_3.json')

# Reading the json with the measurements
with open('../../data/pv_2_3_180_13_00_pf_090pos/measurements.json', 'r') as f:
    data = json.load(f)

     
# Generating stds
rt = {'LV':     3e6/(np.sqrt(3)*800),
      'POIMV':  3*3e6/(np.sqrt(3)*20e3),
      'POI':    6*3e6/(np.sqrt(3)*132e3)}

I_base = {'LV':     3e6/(np.sqrt(3)*800),
          'POIMV':  3e6/(np.sqrt(3)*20e3),
          'POI':    3e6/(np.sqrt(3)*132e3)}

Iclass = [[5, 20, 100, 120], [1.5, 0.75, 0.5, 0.5], [90, 45, 30, 30]]

data_std = {key: None for key in data} 
  
for key in data_std:
    if key.startswith('U'):
        data_std[key] = [0.0025*data[key], 20*np.pi/(60*180)]
    elif key.startswith('I'):
        value = (data[key]*I_base[re.sub(r'\d', '', key.split('_')[1])]/rt[re.sub(r'\d', '', key.split('_')[1])])*100
        epsilon_i_mag = np.interp(value, Iclass[0], Iclass[1])
        epsilon_i_ang = np.interp(value, Iclass[0], Iclass[2])
        data_std[key] = [epsilon_i_mag*data[key]/200, epsilon_i_ang*np.pi/(60*180)]

for key in data_std:
    if key.startswith('P'):
        I_pointer = [key_aux for key_aux in data_std if key_aux.startswith('I_' + key.split('_')[1])][0]
        U_pointer = 'U_' + key.split('_')[1]
        Q_pointer = 'Q_' + key[2:]
        P_pointer = key
        data_std[key] = np.sqrt((data[Q_pointer]**2)*(data_std[U_pointer][1]**2 + data_std[I_pointer][1]**2) + (data[P_pointer]**2)*((data_std[I_pointer][0]/data[I_pointer])**2 + (data_std[U_pointer][0]/data[U_pointer])**2))   
    elif key.startswith('Q'):
        I_pointer = [key_aux for key_aux in data_std if key_aux.startswith('I_' + key.split('_')[1])][0]
        U_pointer = 'U_' + key.split('_')[1]
        P_pointer = 'P_' + key[2:]
        Q_pointer = key
        data_std[key] = np.sqrt((data[P_pointer]**2)*(data_std[U_pointer][1]**2 + data_std[I_pointer][1]**2) + (data[Q_pointer]**2)*((data_std[I_pointer][0]/data[I_pointer])**2 + (data_std[U_pointer][0]/data[U_pointer])**2))
        
