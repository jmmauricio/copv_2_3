import lib
import numpy as np
import json

bandas = {'P': [0.80, 0.40], 'Q': [0.80, 0.40], 'U': [0.980, 0.040]}

minute = '00'
path = ['../../data/pv_2_3_180_', '../../data_Cati/pv_2_3_180_']

# Iteration over the time and power factors
resultados = dict()
for c in ['090neg', '090pos']:  
    resultados[c] = dict()
    for hour in ['08', '10', '13']: 
        
        # Network object
        net = lib.grid(path_topology='pv_2_3.json', 
                       path_measurements='../../data/pv_2_3_180_10_00_pf_090neg/measurements.json')
        
        # Testing the identification performance
        n_simus = 25
        count = lib.identification_fun(n_simus = n_simus, names = names, net_base = net, bandas = bandas)
        resultados[c][hour] = count

# Saving results
with open('std_medidas_1ataque.json', 'w') as json_file:
    json.dump(resultados, json_file, indent=4)