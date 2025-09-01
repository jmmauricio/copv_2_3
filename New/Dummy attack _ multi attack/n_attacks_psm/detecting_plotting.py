import os
import json
import matplotlib.pyplot as plt
import numpy as np
from pydae import plot_tools
colores = plot_tools.set_style(plt)

a = False

# Configuración
factor_potencia = '090pos'
modes = ['sinMT', 'conMT', 'sinMT_conPSM']
bands = list(range(8))  # banda0 a banda7
x_labels = ['80-85%', '85-90%', '90-95%', '95-100%', '100-105%', '105-110%', '110-115%', '115-120%']
colors = {'sinMT': colores[0], 'conMT': colores[1], 'sinMT_conPSM': colores[2]}
time_instants = ['08', '10', '13']
if a:
    n_attacked = list(range(2, 6))  # 2 a 6
else:
    n_attacked = list(range(6, 11))  # 2 a 10

# Crear figura
if a:
    fig, axes = plt.subplots(3, len(n_attacked), figsize=(12, 8), sharex=True, sharey=True)
else:
    fig, axes = plt.subplots(3, len(n_attacked), figsize=(15, 8), sharex=True, sharey=True)

bar_width = 0.25
x = np.arange(len(bands))

for i, time in enumerate(time_instants):
    for j, n_att in enumerate(n_attacked):
        ax = axes[i, j]

        values_by_mode = {mode: [] for mode in modes}

        for band in bands:
            for mode in modes:
                fname = f'results/detection_{mode}_banda{band}.json'
                if os.path.exists(fname):
                    with open(fname, 'r') as f:
                        try:
                            data = json.load(f)
                            detections = data[factor_potencia][time][str(n_att)]['Detection']
                            porcentaje = 100 * sum(detections) / len(detections) if detections else 0
                        except KeyError:
                            porcentaje = np.nan
                else:
                    porcentaje = np.nan
                values_by_mode[mode].append(porcentaje)

        # Dibujar barras
        for k, mode in enumerate(modes):
            bar_pos = x + (k - 1) * bar_width
            ax.bar(bar_pos, values_by_mode[mode], width=bar_width,
                   label=mode if i == 0 and j == 0 else "", color=colors[mode])

        if i == 2:
            ax.set_xticks(x)
            ax.set_xticklabels(x_labels, rotation=45, ha='right')
        else:
            ax.set_xticks([])

        if j == 0:
            ax.set_ylabel(f'{time} h')
        if i == 0:
            ax.set_title(f'{n_att} attacked')

        ax.set_ylim(0, 105)
        ax.grid()

# Leyenda única
labels = ['Detection (%) w/o MV meas.', 'Detection (%) with MV meas.', 'Detection (%) with MV psm.']
axes[0,0].legend(labels)

plt.tight_layout(rect=[0, 0, 1, 0.94])
if a:
    plt.savefig(f'figs/detecction_{factor_potencia}_a.pdf')
else:
    plt.savefig(f'figs/detecction_{factor_potencia}_b.pdf')
plt.show()
