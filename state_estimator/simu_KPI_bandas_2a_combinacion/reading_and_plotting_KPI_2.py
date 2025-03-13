import numpy as np
import json
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import os

# Configuración inicial
fp = '090neg'
hour = '10'
tipo = 'PQ' #PQ, PU, QU
num_indices = 8 
metrics = ['Precision', 'Accuracy', 'Recall', 'F1']  # Métricas a representar
num_subplots = len(metrics)
fp_list = ['090neg', '090pos', '100pos']

for fp in fp_list:
    data_matrices = [np.zeros((num_indices, num_indices)) for _ in range(num_subplots)]
    
    for i in range(num_indices):
        for j in range(num_indices):
            file_name = f'data_simus_ts_bandas_{i}_{j}_2ataques_combinacion_KPI.json'
            if os.path.exists(file_name):
                with open(file_name, 'r') as file:
                    data = json.load(file)
                    for k, metric in enumerate(metrics):
                        try:
                            if metric != 'F1':
                                value = data[fp][hour]['2.5'][tipo][metric] 
                            else:
                                precision = data[fp][hour]['2.5'][tipo]['Precision']
                                recall = data[fp][hour]['2.5'][tipo]['Recall']
                                if precision + recall == 0:
                                    value = 0
                                else:
                                    value = 2*precision*recall/(precision + recall)
                            data_matrices[k][i, j] = value*100
                        except KeyError:
                            data_matrices[k][i, j] = np.nan  
            else:
                for k in range(num_subplots):
                    data_matrices[k][i, j] = np.nan
    
    # Crear figura y rejilla con espacio para la barra de color
    fig = plt.figure(figsize=(24, 6))
    gs = GridSpec(1, 5, width_ratios=[1, 1, 1, 1, 0.05], wspace=0.2)  # 4 subplots + espacio para colorbar
    
    axes = [fig.add_subplot(gs[0]), fig.add_subplot(gs[1]), fig.add_subplot(gs[2]), fig.add_subplot(gs[3])]
    cax = fig.add_subplot(gs[4])  
    
    cmap = plt.cm.magma  
    norm = plt.Normalize(vmin=0, vmax=100)
    labels = ['80-85%', '85-90%', '90-95%', '95-100%', '100-105%', '105-110%', '110-115%', '115-120%']
    if tipo[1] == 'U':
        labels2 = ['98-98.5%', '98.5-99%', '99-99.5%', '99.5-100%', '100-100.5%', '100.5-101%', '101-101.5%', '101.5-102%']
    else:
        labels2 = ['80-85%', '85-90%', '90-95%', '95-100%', '100-105%', '105-110%', '110-115%', '115-120%']
    
    
    for k, ax in enumerate(axes):
        grid = ax.imshow(data_matrices[k], cmap=cmap, norm=norm)
        
        for i in range(num_indices):
            for j in range(num_indices):
                value = data_matrices[k][i, j]
                if not np.isnan(value):
                    ax.text(j, i, f'{value:.0f}%', ha='center', va='center', color='white' if value < 50 else 'black')
        
        ax.set_xticks(np.arange(num_indices))
        ax.set_yticks(np.arange(num_indices))
        ax.set_xticklabels(labels, rotation=45, ha="right")
        ax.set_yticklabels(labels2 if k == 0 else [])
        ax.set_title(metrics[k])
        
        
    axes[0].set_ylabel(tipo[1])
    axes[0].set_xlabel(tipo[0])
    axes[1].set_xlabel(tipo[0])
    axes[2].set_xlabel(tipo[0])
    axes[3].set_xlabel(tipo[0])
    
    # Agregar la barra de color en el espacio reservado
    cbar = fig.colorbar(grid, cax=cax)
    
    plt.savefig('figs/2_ataques_bandas_combinacion_' + tipo + '_' + fp + '_kpi.pdf')
    plt.savefig('figs/2_ataques_bandas_combinacion_' + tipo + '_' + fp + '_kpi.png')
    plt.close()
