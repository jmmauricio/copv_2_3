import json
import numpy as np
from lib_timeseries import system_topology

# Reading network topology
Nodes, Lines = system_topology('../../data/pv_2_3.json')

# Reading the json with the measurements
with open('../../data/pv_2_3_180_13_00_pf_090pos/measurements.json', 'r') as f:
    data = json.load(f)

# Sorting the measurements
Meas_nodes = {item['name']: {'P': [], 'Q': [], 'U': [], 'I': []} for item in Nodes}
Meas_lines = {item['From'] + '_' + item['To']: {'P': [], 'Q': [], 'I': []} for item in Lines}
Meas_lines.update({item['To'] + '_' + item['From']: {'P': [], 'Q': [], 'I': []} for item in Lines})
for key in data:
    item = key.split('_')
    if len(item) == 2:
        Meas_nodes[item[1]][item[0]].append(data[key])        
    elif len(item) == 3:
        Meas_lines[item[1] + '_' + item[2]][item[0]].append(data[key])   
      
# Generating stds
# rt = {'LV_MV':      [3000/(np.sqrt(3)*800), 5],
#       'POI_MV':     3*3000/(np.sqrt(3)*800),
#       'POIMV_POI':  6*3000/(np.sqrt(3)*800)}
rt = 3000/(np.sqrt(3)*800)
I_base = 10e6/(20e3*np.sqrt(3))
data_std = {key: None for key in data}   
    if key.startswith('U'):
        data_std[key] = [0.0025*data[key], 20*np.pi/(60*180)]
    elif key.startswith('I'):
        # rango_i = data[key]*100/(rt/I_base)
        # (valorI/(rt/Ibase_aqui))*100        
        data_std[key] = [0.0025*data[key], 20*np.pi/(60*180)]

for key in data_std:     
    elif key.startswith('P'):
        key_split = key.split['_']
        if len(key_split) == 2:
            U_std = data_std['U_' + key_split[1]]
            I_std = data_std['I_' + key_split[1]]
        
        
    elif key.startswith('Q'):
        5