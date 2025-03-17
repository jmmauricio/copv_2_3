from lib_timeseries import system_topology, system_measurements, system_constraints
import lib
import numpy as np
import json 


lambda_value = 2.5

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
        
        n_simus = 1000
        range_n_att = list(range(3,19))
        # bandas = {
        #     'P': ([0.8, 0.85], [1.15, 1.2]),
        #     'Q': ([0.8, 0.85], [1.15, 1.2]),
        #     'U': ([0.98, 0.985], [1.015, 1.02]),
        #     }
        bandas = {
            'P': ([0.85, 0.9], [1.10, 1.15]),
            'Q': ([0.85, 0.9], [1.10, 1.15]),
            'U': ([0.985, 0.99], [1.010, 1.015]),
            }
        count = lib.n_attacks(lambda_value = lambda_value, n_simus = n_simus, names = names, net_base = net, range_n_att=range_n_att, bandas = bandas)
        
        for n_attacks in range_n_att:               
            count[str(lambda_value)][str(n_attacks)]['Precision'] = count[str(lambda_value)][str(n_attacks)]['Precision']/n_simus
            count[str(lambda_value)][str(n_attacks)]['Accuracy'] = count[str(lambda_value)][str(n_attacks)]['Accuracy']/n_simus
            count[str(lambda_value)][str(n_attacks)]['Recall'] = count[str(lambda_value)][str(n_attacks)]['Recall']/n_simus
        resultados[c][hour] = count


with open('data_n_attacks_KPI_10_15.json', 'w') as json_file:
    json.dump(resultados, json_file, indent=4)