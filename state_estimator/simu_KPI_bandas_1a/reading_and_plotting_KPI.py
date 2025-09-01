import numpy as np
import json
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from pydae import plot_tools
from lib_timeseries import system_topology, system_measurements
import matplotlib.gridspec as gridspec

# Ajustes generales de estilo
colores = plot_tools.set_style(plt)
plt.rcParams.update({
    'font.size': 11,
    'axes.labelsize': 11,
    'axes.titlesize': 11,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'legend.fontsize': 10,
    'figure.titlesize': 12
})

# Colores extra
colores.append("#007bff")
colores.append("#d63384")
colores.append("#28a745")
colores.append("#dc3545")

bandas_array = [
    {'P': [0.80, 0.05], 'Q': [0.80, 0.05], 'U': [0.980, 0.005]},
    {'P': [0.85, 0.05], 'Q': [0.85, 0.05], 'U': [0.985, 0.005]},
    {'P': [0.90, 0.05], 'Q': [0.90, 0.05], 'U': [0.990, 0.005]},
    {'P': [0.95, 0.05], 'Q': [0.95, 0.05], 'U': [0.995, 0.005]},
    {'P': [1.00, 0.05], 'Q': [1.00, 0.05], 'U': [1.000, 0.005]},
    {'P': [1.05, 0.05], 'Q': [1.05, 0.05], 'U': [1.005, 0.005]},
    {'P': [1.10, 0.05], 'Q': [1.10, 0.05], 'U': [1.010, 0.005]},
    {'P': [1.15, 0.05], 'Q': [1.15, 0.05], 'U': [1.015, 0.005]}
]

P_gen = []
minute = '00'
path = ['../../data_Cati2/pv_2_3_180_', '../../data_Cati2/pv_2_3_180_']
c = '090pos'

for hour in ['01','02','03','04','05','06','07','08','09','10','11','12','13','14','15','16','17','18','19','20','21','22','23']:
    extended_path = [path[0] + hour + '_' + minute + '_pf_' + c + '/',
                     path[1] + hour + '_' + minute + '_pf_' + c + '/']
    Nodes, Lines = system_topology('../../data/pv_2_3.json')
    Meas, mjson, stdjson = system_measurements(extended_path, 
                                               'measurements.json', 
                                               'std_2.json', 
                                               Nodes, 
                                               Lines, 
                                               add_noise = False)
    P_gen.append(Meas[0]['value'])

# Figura y GridSpec
fig = plt.figure(figsize=(7, 7))
gs = gridspec.GridSpec(4, 3, height_ratios=[1.2, 1, 1, 1])
plt.subplots_adjust(wspace=0.1, hspace=0.4)

# Primer subplot (stackplot)
ax = fig.add_subplot(gs[0, :])
ax_pos = ax.get_position()
ax.set_position([ax_pos.x0, ax_pos.y0 + 0.08, ax_pos.width, ax_pos.height * (1 / 1.5)])
ax.stackplot(range(1, 24), P_gen, alpha=0.7)
ax.grid(True)
for it in [8, 10, 13]:
    ax.plot([it, it], [0, 0.35], 'k-.', alpha=0.5)
ax.set_ylim([0.0, 0.4])
ax.set_xlim([0.0, 23])
ax.set_xticks([])  # Quitar xticks
ax.set_xlabel("")  # Quitar xlabel

# Subplots para P, Q, U
axes = np.empty((3, 3), dtype=object)
for i in range(3):
    for j in range(3):
        axes[i, j] = fig.add_subplot(gs[i+1, j])

horas = ['08', '10', '13']
tipos = ['P', 'Q', 'U']

for idx_tipo, tipo in enumerate(tipos):
    for index_hour, hour in enumerate(horas):
        for index_bandas, bandas in enumerate(bandas_array):
            file_name = f'data_simus_ts_banda_{index_bandas}_1ataque_KPI.json'
            with open(file_name, 'r') as file:
                data = json.load(file)

            num_lmb = 20
            lmb_range = np.linspace(0.01, 10, num_lmb)
            x_values = [str(item) for item in lmb_range]

            # KPIs
            kpis = []
            for x in x_values:
                values = list(np.array([data[c][hour][x][tipo][k] for k in ['Precision', 'Accuracy', 'Recall']]))
                kpis.append(values)

            precision = [item[0]*100 for item in kpis]
            recall = [item[2]*100 for item in kpis]
            F1 = [2*p*r/(p+r) if (p+r)>0 else 0 for p,r in zip(precision, recall)]

            axes[idx_tipo, index_hour].plot(lmb_range, F1, color=colores[index_bandas])

# Ajustes de ejes y grid
xticks = [0,2,4,6,8,10]
yticks = [0,25,50,75,100]

for i in range(3):
    for j in range(3):
        axes[i, j].set_xlim([0,10])
        axes[i, j].set_xticks(xticks)
        axes[i, j].set_yticks(yticks)
        axes[i, j].grid(True, linestyle='--', alpha=0.6)  # Grid uniforme
        if i < 2:
            axes[i, j].set_xticklabels([])
        if j > 0:
            axes[i, j].set_yticklabels([])

# Etiquetas solo en última fila
axes[2,0].set_xlabel(r'$\lambda$')
axes[2,1].set_xlabel(r'$\lambda$')
axes[2,2].set_xlabel(r'$\lambda$')

# Títulos encima de cada subplot
for i, tipo in enumerate(tipos):
    for j, hora in enumerate(horas):
        fig.text(0.21 + j * 0.31, 0.646 - i * 0.195, f"{tipo}-{hora} h", fontsize=11, ha='center')

# Leyenda global con colores correctos
legend_labels = ['98-98.5%', '98.5-99%', '99-99.5%', '99.5-100%', '100-100.5%', '100.5-101%', '101-101.5%', '101.5-102%']
handles = [Line2D([0], [0], color=colores[i], lw=2) for i in range(len(legend_labels))]
fig.legend(handles, legend_labels, loc='upper center', ncol=4, bbox_to_anchor=(0.5, 0.97))

plt.tight_layout(rect=[0, 0, 1, 0.92])
plt.savefig('figs/new_fig.pdf', bbox_inches='tight')
plt.show()
