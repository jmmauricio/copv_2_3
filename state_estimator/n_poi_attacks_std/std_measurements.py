from lib_timeseries import system_topology, system_measurements, system_constraints
import lib
import numpy as np
import time
import json 

bandas = {'P': [0.80, 0.40], 'Q': [0.80, 0.40], 'U': [0.980, 0.040]}


minute = '00'
path = ['../../data/pv_2_3_180_', '../../data_Cati/pv_2_3_180_']

resultados = dict()
for c in ['090neg', '090pos']: 
# for c in ['090neg', '090pos', '100pos']:  
    resultados[c] = dict()
    for hour in ['08', '10', '13']:     
        
        sheet_name = hour + '_' + minute + '_pf_' + c
        extended_path = [path[0] + hour + '_' + minute + '_pf_' + c + '/',
                         path[1] + hour + '_' + minute + '_pf_' + c + '/']

        Nodes, Lines = system_topology('../../data/pv_2_3.json')
        Meas, mjson, stdjson = system_measurements(extended_path, 
                                                   'measurements.json', 
                                                   'std_2.json', 
                                                   Nodes, 
                                                   Lines, 
                                                   add_noise = True)
        Cons = system_constraints(Nodes)

        names = [m['type'] + '_' + Nodes[m['node']]['name'] if m['line'] == None else m['type'] + '_' + Lines[np.abs(m['line'])]['From'] + '_' + Lines[np.abs(m['line'])]['To'] for m in Meas]
        for item in zip(Meas, names):
            item[0]['name'] = item[1]

        names_P = [names[index] for index in range(len(names)) if names[index].startswith('P_LV')]
        names_Q = [names[index] for index in range(len(names)) if names[index].startswith('Q_LV')]
        names_U = [names[index] for index in range(len(names)) if names[index].startswith('U_LV')]
        
        net = lib.grid(Nodes, Lines, Meas, Cons)
        
        n_simus = 1000
        count = lib.identification_fun(n_simus = n_simus, names = names, net_base = net, bandas = bandas)
        resultados[c][hour] = count


with open('std_medidas_1ataque.json', 'w') as json_file:
    json.dump(resultados, json_file, indent=4)