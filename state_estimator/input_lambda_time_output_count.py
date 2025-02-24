from lib_timeseries import system_topology, system_measurements, system_constraints
import lib
import numpy as np


# Se extrae el conjunto de nodos, líneas y medidas de la red así como las restricciones
extended_path = ['../data/pv_2_3_180_14_45_pf_090neg/', '../data_Cati/pv_2_3_180_14_45_pf_090neg/']
Nodes, Lines = system_topology('../data/pv_2_3.json')
Meas, mjson, stdjson = system_measurements(extended_path, 
                                           'measurements.json', 
                                           'std_2.json', 
                                           Nodes, 
                                           Lines, 
                                           add_noise = True)
Cons = system_constraints(Nodes)

names = [m['type'] + '_' + Nodes[m['node']]['name'] if m['line'] == None else m['type'] + '_' + Lines[np.abs(m['line'])]['From'] + '_' + Lines[np.abs(m['line'])]['To'] for m in Meas]
for item in zip(Meas, names):
    item[0]['name'] = item[1]

names_P = [names[index] for index in range(len(names)) if names[index].startswith('P_LV')]
names_Q = [names[index] for index in range(len(names)) if names[index].startswith('Q_LV')]
names_U = [names[index] for index in range(len(names)) if names[index].startswith('U_LV')]

net = lib.grid(Nodes, Lines, Meas, Cons)

count = lib.identification_fun(lmb_min = 0.01, lmb_max = 50, lmb_num = 100, n_simus = 1000, names = names, net_base = net, num_attacks = 2)



import matplotlib.pyplot as plt
from pydae import plot_tools

lmb_range = np.linspace(0.01, 50, 100)
keys_lmb = [str(x) for x in lmb_range]

# Set style and colors
colors = plot_tools.set_style(plt)
colors.pop(3)

# Initialize the figure and axes
fig, axs = plt.subplots(3, 1, figsize=(8, 8), sharex=True)

# Labels for the different numbers
labels = ['Detection', 'Detection and others', 'Incorrect detection', 'No detection']

def preparar_datos(clave):
    vals_0 = [count[str(k)][clave]["0"] for k in lmb_range]
    vals_1 = [count[str(k)][clave]["1"] for k in lmb_range]
    vals_2 = [count[str(k)][clave]["2"] for k in lmb_range]
    vals_3 = [count[str(k)][clave]["3"] for k in lmb_range]
    return vals_0, vals_1, vals_2, vals_3

p_0, p_1, p_2, p_3 = preparar_datos("P")
q_0, q_1, q_2, q_3 = preparar_datos("Q")
u_0, u_1, u_2, u_3 = preparar_datos("U")

# Subplot P
axs[0].stackplot(lmb_range, p_0, p_1, p_2, p_3, labels=labels, colors=colors, alpha=0.6)

# Subplot Q
axs[1].stackplot(lmb_range, q_0, q_1, q_2, q_3, labels=labels, colors=colors, alpha=0.6)

# Subplot U
axs[2].stackplot(lmb_range, u_0, u_1, u_2, u_3, labels=labels, colors=colors, alpha=0.6)

# Etiquetas y formato
plt.xlabel('lmb_range')
plt.xticks(rotation=90)
plt.tight_layout()
plt.show()


# Set the shared x-axis label
axs[0].set_ylabel('$P$')
axs[1].set_ylabel('$Q$')
axs[2].set_ylabel('$U$')

axs[-1].set_xlabel('$\lambda$')
axs[-1].legend()


