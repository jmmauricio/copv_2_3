import numpy as np
import json
import matplotlib.pyplot as plt
from pydae import plot_tools
from lib_timeseries import system_topology, system_measurements
import matplotlib.gridspec as gridspec
import os

fp = '090neg'
hour = '10'
tipo = 'QU' #PQ, PU, QU
num_indices = 8 
num_subplots = 6  
fp_list = ['090neg', '090pos', '100pos']


for fp in fp_list:
    data_matrices = [np.zeros((num_indices, num_indices)) for _ in range(num_subplots)]
    
    for i in range(num_indices):
        for j in range(num_indices):
            file_name = f'data_simus_ts_bandas_{i}_{j}_2ataques_combinacion_KPI.json'
            if os.path.exists(file_name):
                with open(file_name, 'r') as file:
                    data = json.load(file)
                    for k in range(num_subplots):
                        try:
                            value = data[fp][hour]['2.5'][tipo][str(k)]
                            data_matrices[k][i, j] = value
                        except KeyError:
                            data_matrices[k][i, j] = np.nan  
            else:
                for k in range(num_subplots):
                    data_matrices[k][i, j] = np.nan
    
    fig, axes = plt.subplots(2, 3, figsize=(18, 9), gridspec_kw={'wspace': -0.2})
    cmap = plt.cm.magma  
    norm = plt.Normalize(vmin=0, vmax=100)
    labels = ['80-85%', '85-90%', '90-95%', '95-100%', '100-105%', '105-110%', '110-115%', '115-120%']
    if tipo[1] == 'U':
        labels2 = ['98-98.5%', '98.5-99%', '99-99.5%', '99.5-100%', '100-100.5%', '100.5-101%', '101-101.5%', '101.5-102%']
    else:
        labels2 = ['80-85%', '85-90%', '90-95%', '95-100%', '100-105%', '105-110%', '110-115%', '115-120%']
    
    titulos = ['Detection', 'Detection and others', 'Partial detection', 'Partial detection and others', 'No detection', 'Incorrect detection']
    for k, ax in enumerate(axes.flat):
        grid = ax.imshow(data_matrices[k], cmap=cmap, norm=norm)
        
        for i in range(num_indices):
            for j in range(num_indices):
                value = data_matrices[k][i, j]
                if not np.isnan(value):
                    ax.text(j, i, f'{value:.0f}%', ha='center', va='center', color='white' if value < 50 else 'black')
        
        ax.set_xticks(np.arange(num_indices))
        ax.set_yticks(np.arange(num_indices))
        ax.set_xticklabels(labels, rotation=45, ha="right")
        ax.set_yticklabels(labels2)
        ax.set_title(titulos[k])    
    
    axes[0,0].set_xticks([])
    axes[0,1].set_xticks([])
    axes[0,2].set_xticks([])
    axes[0,1].set_yticks([])
    axes[0,2].set_yticks([])
    axes[1,1].set_yticks([])
    axes[1,2].set_yticks([])
    
    axes[0,0].set_ylabel(tipo[1])
    axes[1,0].set_ylabel(tipo[1])
    axes[1,0].set_xlabel(tipo[0])
    axes[1,1].set_xlabel(tipo[0])
    axes[1,2].set_xlabel(tipo[0])
    
    
    fig.colorbar(grid, ax=axes.ravel().tolist())
    
    
    plt.savefig('figs/2_ataques_bandas_combinacion_' + tipo + '_' + fp + '.pdf')
    plt.savefig('figs/2_ataques_bandas_combinacion_' + tipo + '_' + fp + '.png')
    plt.close()














