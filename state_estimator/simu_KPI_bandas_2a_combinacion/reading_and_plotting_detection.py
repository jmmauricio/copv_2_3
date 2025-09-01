import numpy as np
import json
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import os

# Configuración inicial
hour = '10'
lambda_fijo = '2.5'
tipo = 'QU'  # Magnitud atacada
num_indices = 8
fp_list = ['090neg', '090pos', '100pos']
metrics = ['Detected (%)', 'Not detected (%)']

for fp in fp_list:
    data_matrices = [np.full((num_indices, num_indices), np.nan) for _ in range(2)]  # Para % true y % false

    for i in range(num_indices):
        for j in range(num_indices):
            file_name = f'detection_{i}_{j}.json'
            if os.path.exists(file_name):
                with open(file_name, 'r') as file:
                    try:
                        data = json.load(file)
                        detections = data[fp][hour][lambda_fijo][tipo]['Detection']
                        total = len(detections)
                        if total > 0:
                            num_true = sum(detections)
                            num_false = total - num_true
                            data_matrices[0][i, j] = 100 * num_true / total
                            data_matrices[1][i, j] = 100 * num_false / total
                    except KeyError:
                        continue

    # Crear figura y rejilla con espacio para barra de color
    fig = plt.figure(figsize=(12, 6))
    gs = GridSpec(1, 3, width_ratios=[1, 1, 0.05], wspace=0.2)  # 2 subplots + colorbar

    axes = [fig.add_subplot(gs[0]), fig.add_subplot(gs[1])]
    cax = fig.add_subplot(gs[2])

    cmap = plt.cm.magma
    norm = plt.Normalize(vmin=0, vmax=100)

    # Etiquetas de los ejes
    tipo1 = tipo[0]
    tipo2 = tipo[1]
    if tipo1 == 'U':
        labels1 = ['98-98.5%', '98.5-99%', '99-99.5%', '99.5-100%', '100-100.5%', '100.5-101%', '101-101.5%', '101.5-102%']
    else:
        labels1 = ['80-85%', '85-90%', '90-95%', '95-100%', '100-105%', '105-110%', '110-115%', '115-120%']
    if tipo2 == 'U':
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
        ax.set_xticklabels(labels1, rotation=45, ha="right")
        ax.set_yticklabels(labels2 if k == 0 else [])
        ax.set_title(metrics[k])
        ax.set_xlabel(tipo1)
        if k == 0:
            ax.set_ylabel(tipo2)

    # Agregar la barra de color
    cbar = fig.colorbar(grid, cax=cax)

    # Guardar figura
    plt.savefig(f'figs/detection_bands_{tipo}_{fp}.pdf')
    plt.close()