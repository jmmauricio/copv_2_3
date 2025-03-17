import numpy as np
import json
import matplotlib.pyplot as plt
from pydae import plot_tools
from lib_timeseries import system_topology, system_measurements
import matplotlib.gridspec as gridspec
import os

fp = '090neg'
hour = '10'
tipo = '3' # Número de ataques: 3, 4 ,5 6
num_indices = 8 
num_subplots = 6  
fp_list = ['090neg', '090pos', '100pos']

data_matrices = [np.zeros((num_indices, num_indices)) for _ in range(num_subplots)]


file_name = f'data_n_attacks_KPI_15_20.json'
if os.path.exists(file_name):
    with open(file_name, 'r') as file:
        data = json.load(file)
        for tip in [3, 4, 5, 6]:
            for fp in fp_list:
                tipo = str(tip)
                for k in ['Precision', 'Accuracy', 'Recall']:           
                    value = data[fp][hour]['2.5'][tipo][str(k)]
                    print('Number of attacks: ' + tipo + '\t' + 'Power factor: ' + fp + '\t Avg. ' + k + f': {value*100:.2f}', ) 
                print('')










