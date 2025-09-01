import os
import json
import matplotlib.pyplot as plt
import numpy as np
from pydae import plot_tools
colores = plot_tools.set_style(plt)

# Configuración
modes = ['sinMT', 'conMT', 'sinMT_conPSM']
bands = list(range(8))
x_labels = ['80-85%', '85-90%', '90-95%', '95-100%', '100-105%', '105-110%', '110-115%', '115-120%']
power_factor = '090pos'  # Puedes cambiarlo si lo deseas
horas = ['08', '10', '13']
magnitudes = ['P', 'Q', 'U', 'I']
colors = {'sinMT': colores[0], 'conMT': colores[1], 'sinMT_conPSM': colores[2]}

# Crear figura
fig, axes = plt.subplots(4, 3, figsize=(12, 8), sharex=True, sharey=True)

bar_width = 0.25
x = np.arange(len(bands))

# Recorremos cada combinación magnitud × hora
for i, mag in enumerate(magnitudes):
    for j, hora in enumerate(horas):
        ax = axes[i, j]

        # Inicializar datos: una lista por modo
        values_by_mode = {mode: [] for mode in modes}

        for band in bands:
            for mode in modes:
                fname = f'results/detection_{mode}_{band}.json'
                if os.path.exists(fname):
                    with open(fname, 'r') as f:
                        try:
                            data = json.load(f)
                            detections = data[power_factor][hora][mag]['Detection']
                            porcentaje = 100 * sum(detections) / len(detections) if detections else 0
                        except KeyError:
                            porcentaje = np.nan
                else:
                    porcentaje = np.nan

                values_by_mode[mode].append(porcentaje)

        # Dibujar las barras
        for k, mode in enumerate(modes):
            bar_pos = x + (k - 1) * bar_width
            ax.bar(bar_pos, values_by_mode[mode], width=bar_width, label=mode if i == 0 and j == 0 else "", color=colors[mode])
            if hora == '13':
                print(mag)
                print(mode)
                print(values_by_mode[mode])
        if i == 0:
            ax.set_title(f'{hora} h')
        if j == 0:
            ax.set_ylabel(f'{mag}')
        ax.set_xticks(x)
        ax.set_xticklabels(x_labels, rotation=45, ha='right')

        # ax.set_ylim(0, 105)
        ax.grid(True)

# Leyenda única
labels = ['Detection (%) w/o MV meas.', 'Detection (%) with MV meas.', 'Detection (%) with MV psm.']
axes[0,0].legend(labels)

plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.savefig(f'figs/detection_{power_factor}.pdf')
plt.show()
