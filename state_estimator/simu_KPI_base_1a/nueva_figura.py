import numpy as np
import json
import matplotlib.pyplot as plt
from pydae import plot_tools
from lib_timeseries import system_topology, system_measurements
import matplotlib.gridspec as gridspec

# Ajustes generales de estilo
colors = plot_tools.set_style(plt)
plt.rcParams.update({
    'font.size': 11,
    'axes.labelsize': 11,
    'axes.titlesize': 11,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'legend.fontsize': 10,
    'figure.titlesize': 12
})

file_name = 'data_simus_ts_1ataque_KPI.json'
fp_list = ['090pos']

# Cargar datos JSON
with open(file_name, 'r') as file:
    data = json.load(file)

P_gen = []
minute = '00'
path = ['../../data_Cati2/pv_2_3_180_', '../../data_Cati2/pv_2_3_180_']

for c in ['090neg']:
    for hour in ['01','02','03','04','05','06','07','08','09','10','11','12','13','14','15','16','17','18','19','20','21','22','23']:
        extended_path = [path[0] + hour + '_' + minute + '_pf_' + c + '/',
                         path[1] + hour + '_' + minute + '_pf_' + c + '/']

        Nodes, Lines = system_topology('../../data/pv_2_3.json')
        Meas, mjson, stdjson = system_measurements(extended_path,
                                                   'measurements.json',
                                                   'std_2.json',
                                                   Nodes,
                                                   Lines,
                                                   add_noise=False)
        P_gen.append(Meas[0]['value'])

# Valores de lambda
num_lmb = 20
lmb_range = np.linspace(0.01, 10, num_lmb)

# Función para añadir subplots
def add_kpi_subplots(fig, gs, start_row, tipo, data, hours, labels_time, colors, c, show_xticks=False):
    axs = np.empty((2, 3), dtype=object)
    index = 0
    for i in range(2):
        for j in range(3):
            axs[i, j] = fig.add_subplot(gs[start_row + i, j])

    for hour, label in zip(hours, labels_time):
        row, col = divmod(index, 3)
        x_values = [str(item) for item in np.linspace(0.01, 10, num_lmb)]

        counts = []
        kpis = []
        for x in x_values:
            values = list(np.array([data[c][hour][x][tipo][k] for k in ['0','1','2','3'] if k in data[c][hour][x][tipo]]) / 10)
            counts.append(values)
            values = list(np.array([data[c][hour][x][tipo][k] for k in ['Precision','Accuracy','Recall']]))
            kpis.append(values)

        counts = np.array(counts).T
        axs[row, col].stackplot(lmb_range, counts, colors=colors, alpha=0.7)
        axs[row + 1, col].plot(lmb_range, [item[0]*100 for item in kpis], 'b')
        axs[row + 1, col].plot(lmb_range, [item[1]*100 for item in kpis], 'r')
        axs[row + 1, col].plot(lmb_range, [item[2]*100 for item in kpis], 'k')
        axs[row + 1, col].plot(lmb_range, [200*item[0]*item[2]/(item[0]+item[2]) for item in kpis], 'g')

        axs[row, col].set_title(label)
        axs[row, col].set_xlim([0, 5])
        axs[row + 1, col].set_xlim([0, 5])
        axs[row, col].set_ylim([0, 100])
        axs[row + 1, col].set_ylim([0, 100])
        axs[row, col].grid(True)
        axs[row + 1, col].grid(True)

        if not show_xticks:
            axs[row, col].set_xticklabels([])
            axs[row + 1, col].set_xticklabels([])
        else:
            axs[row, col].set_xticklabels([])
            axs[row + 1, col].set_xlabel(r'$\lambda$')
            axs[row + 1, col].set_xticks([0,1,2,3,4,5])

        if col > 0:
            axs[row, col].set_yticklabels([])
            axs[row + 1, col].set_yticklabels([])
        if col == 0:
            axs[row, col].set_yticklabels([0, 50, 100])
            axs[row + 1, col].set_yticklabels([0, 50, 100])

        index += 1

    return axs  # 🔍 devolvemos referencias para leyenda

# Configuración de etiquetas
hours = ['08', '10', '13']
labels_P = ['P - 8h', 'P - 10h', 'P - 13h']
labels_Q = ['Q - 8h', 'Q - 10h', 'Q - 13h']
labels_U = ['U - 8h', 'U - 10h', 'U - 13h']

for c in fp_list:
    fig = plt.figure(figsize=(7, 8))
    gs = gridspec.GridSpec(7, 3, height_ratios=[1.5, 1, 1, 1, 1, 1, 1])
    gs.update(wspace=0.1, hspace=0.4) 

    # Gráfico principal
    ax = fig.add_subplot(gs[0, :])
    ax.stackplot(list(range(1, 24)), P_gen, alpha=0.7)
    ax.grid(True)
    for it in [8, 10, 13]:
        ax.plot([it, it], [0, 0.35], 'k-.', alpha=0.5)
    ax.set_ylim([0.0, 0.4])
    ax.set_xlim([0.0, 23])
    ax.set_xticklabels([])

    # Añadir subplots y capturar handles para la leyenda
    axs_P = add_kpi_subplots(fig, gs, start_row=1, tipo='P', data=data, hours=hours, labels_time=labels_P, colors=colors, c=c)
    axs_Q = add_kpi_subplots(fig, gs, start_row=3, tipo='Q', data=data, hours=hours, labels_time=labels_Q, colors=colors, c=c)
    axs_U = add_kpi_subplots(fig, gs, start_row=5, tipo='U', data=data, hours=hours, labels_time=labels_U, colors=colors, c=c, show_xticks=True)

    # 🔍 Extraer handles para la leyenda global
    # Leyenda del stackplot (primera columna de la segunda fila)
    stack_labels = ['Identificacion', 'Identificacion and others', 'Incorrect Identificacion', 'No Identificacion']
    stack_handles = axs_P[0,0].collections[:4]

    # Leyenda de métricas (primera columna de la tercera fila)
    metric_labels = ['Precision', 'Accuracy', 'Recall', 'F1']
    metric_handles = axs_P[1,0].lines[:4]

    all_handles = stack_handles + metric_handles
    all_labels = stack_labels + metric_labels

    # Leyenda global arriba del todo
    fig.legend(all_handles, all_labels, loc='upper center', bbox_to_anchor=(0.5, 0.95), ncol=4, frameon=False)

    # Guardar figura
    
    # plt.tight_layout(rect=[0, 0, 1, 0.92])
    plt.savefig('figs/nueva_con_leyenda_global.pdf', bbox_inches='tight')
    plt.show()
