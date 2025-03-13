from lib_timeseries import system_topology, system_measurements, system_constraints
import lib
import numpy as np
import json 

bandas_array = [{'P': [0.80, 0.05], 'Q': [0.80, 0.05], 'U': [0.980, 0.005]},
                {'P': [0.85, 0.05], 'Q': [0.85, 0.05], 'U': [0.985, 0.005]},
                {'P': [0.90, 0.05], 'Q': [0.90, 0.05], 'U': [0.990, 0.005]},
                {'P': [0.95, 0.05], 'Q': [0.95, 0.05], 'U': [0.995, 0.005]},
                {'P': [1.00, 0.05], 'Q': [1.00, 0.05], 'U': [1.000, 0.005]},
                {'P': [1.05, 0.05], 'Q': [1.05, 0.05], 'U': [1.005, 0.005]},
                {'P': [1.10, 0.05], 'Q': [1.10, 0.05], 'U': [1.010, 0.005]},
                {'P': [1.15, 0.05], 'Q': [1.15, 0.05], 'U': [1.015, 0.005]}]

lambda_value = 2.5

for index_banda_1, banda_1 in enumerate(bandas_array): 
    for index_banda_2, banda_2 in enumerate(bandas_array):    
    
        resultados = dict()
        
        minute = '00'
        path = ['../../data/pv_2_3_180_', '../../data_Cati/pv_2_3_180_']
        
        for c in ['090neg', '090pos', '100pos']:    
            resultados[c] = dict()
            
            for hour in ['10']:                          
                    
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
                count = lib.identification_2attacks_combinacion(lambda_value = lambda_value, n_simus = n_simus, names = names, net_base = net, banda1 = banda_1, banda2 = banda_2)
                
                for medida_atacada in ['PQ', 'PU', 'QU']:               
                    count[str(lambda_value)][medida_atacada]['Precision'] = count[str(lambda_value)][medida_atacada]['Precision']/n_simus
                    count[str(lambda_value)][medida_atacada]['Accuracy'] = count[str(lambda_value)][medida_atacada]['Accuracy']/n_simus
                    count[str(lambda_value)][medida_atacada]['Recall'] = count[str(lambda_value)][medida_atacada]['Recall']/n_simus
                resultados[c][hour] = count
        
        
        with open('data_simus_ts_bandas_' + str(index_banda_1) + '_' + str(index_banda_2) + '_2ataques_combinacion_KPI.json', 'w') as json_file:
            json.dump(resultados, json_file, indent=4)