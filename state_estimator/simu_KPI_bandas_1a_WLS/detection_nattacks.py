from lib_timeseries import system_topology, system_measurements, system_constraints
import lib
import numpy as np
import time
import json 

bandas_array = [{'P': [0.6, 0.8], 'Q': [0.6, 0.8], 'U': [0.96, 0.08]}]



for index_bandas, bandas in enumerate(bandas_array):    
    
    resultados = dict()
    
    t0 = time.time()
    minute = '00'
    path = ['../../data/pv_2_3_180_', '../../data_Cati/pv_2_3_180_']
    
    for c in ['090pos']:    
        resultados[c] = dict()
        
        for hour in ['13']:
            resultados[c][hour] = dict()
            
            for n_at in range(2,19):
                print(hour)
                print(time.time() - t0)
                t0 = time.time()
                          
                    
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
                
                n_simus = 100
                count = lib.detection_n(lmb_min = 0.01, lmb_max = 10, lmb_num = 20, n_simus = n_simus, names = names, net_base = net, bandas = bandas, num_attacks=n_at)
                
                resultados[c][hour][n_at] = count
    
    
    with open('detection_n_' + str(index_bandas) + '.json', 'w') as json_file:
        json.dump(resultados, json_file, indent=4)