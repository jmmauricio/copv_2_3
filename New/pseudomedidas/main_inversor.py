import lib
import numpy as np
import json

bandas_array = [{'P': [0.80, 0.05], 'Q': [0.80, 0.05], 'U': [0.980, 0.005], 'I': [0.80, 0.05]},
                {'P': [0.85, 0.05], 'Q': [0.85, 0.05], 'U': [0.985, 0.005], 'I': [0.85, 0.05]},
                {'P': [0.90, 0.05], 'Q': [0.90, 0.05], 'U': [0.990, 0.005], 'I': [0.90, 0.05]},
                {'P': [0.95, 0.05], 'Q': [0.95, 0.05], 'U': [0.995, 0.005], 'I': [0.95, 0.05]},
                {'P': [1.00, 0.05], 'Q': [1.00, 0.05], 'U': [1.000, 0.005], 'I': [1.00, 0.05]},
                {'P': [1.05, 0.05], 'Q': [1.05, 0.05], 'U': [1.005, 0.005], 'I': [1.05, 0.05]},
                {'P': [1.10, 0.05], 'Q': [1.10, 0.05], 'U': [1.010, 0.005], 'I': [1.10, 0.05]},
                {'P': [1.15, 0.05], 'Q': [1.15, 0.05], 'U': [1.015, 0.005], 'I': [1.15, 0.05]}]

minute = '00'
path = ['../../data/pv_2_3_180_', '../../data_Cati/pv_2_3_180_']

# Iteration over the time and power factors
for index_bandas, bandas in enumerate(bandas_array): 
    resultados_sinMT = dict()
    resultados_conMT = dict()
    resultados_sinMT_conPSM = dict()
    for c in ['090neg', '090pos']:  
        resultados_sinMT[c] = dict()
        resultados_conMT[c] = dict()
        resultados_sinMT_conPSM[c] = dict()
        for hour in ['08', '10', '13']: 
            
            # Network objects
            net_sinMT = lib.grid(path_topology='pv_2_3.json', 
                                 path_measurements='../../data/pv_2_3_180_' + hour + '_00_pf_' + c + '/measurements.json',
                                 MT=False)            
            net_conMT = lib.grid(path_topology='pv_2_3.json', 
                                 path_measurements='../../data/pv_2_3_180_' + hour + '_00_pf_' + c + '/measurements.json',
                                 MT=True)      
            net_sinMT_conPSM = lib.grid(path_topology='pv_2_3.json', 
                                        path_measurements='../../data/pv_2_3_180_' + hour + '_00_pf_' + c + '/measurements.json',
                                        MT=False, PSM=True)
            
            # Testing the identification performance
            n_simus = 100            
            names = [m.tipo + '_' + m.node.name if hasattr(m, 'node') else m.tipo + '_' + m.line.nodes[0].name + '_' + m.line.nodes[1].name for m in net_sinMT.meas]  
            
            count_sinMT = lib.identification_fun(n_simus = n_simus, names = names, net_base = net_sinMT, bandas = bandas)
            count_conMT = lib.identification_fun(n_simus = n_simus, names = names, net_base = net_conMT, bandas = bandas)
            count_sinMT_conPSM = lib.identification_fun(n_simus = n_simus, names = names, net_base = net_sinMT_conPSM, bandas = bandas)
            
            resultados_sinMT[c][hour] = count_sinMT
            resultados_conMT[c][hour] = count_conMT
            resultados_sinMT_conPSM[c][hour] = count_sinMT_conPSM
            
    # Saving results
    with open('results/inversor_1ataque_sinMT_' + str(index_bandas) + '.json', 'w') as json_file:
        json.dump(resultados_sinMT, json_file, indent=4)
    with open('results/inversor_1ataque_conMT_' + str(index_bandas) + '.json', 'w') as json_file:
        json.dump(resultados_conMT, json_file, indent=4)
    with open('results/inversor_1ataque_sinMT_conPSM_' + str(index_bandas) + '.json', 'w') as json_file:
        json.dump(resultados_sinMT_conPSM, json_file, indent=4)
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        