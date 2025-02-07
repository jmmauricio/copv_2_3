from lib_timeseries import system_topology, system_measurements, system_constraints
import lib
import numpy as np
import pandas as pd

# Se extrae el conjunto de nodos, líneas y medidas de la red así como las restricciones
extended_path = ['../data/pv_2_3_180_14_45_pf_090neg/', '../data_Cati/pv_2_3_180_14_45_pf_090neg/']
Nodes, Lines = system_topology('../data/pv_2_3.json')
Meas, mjson, stdjson = system_measurements(extended_path, 
                                           'measurements.json', 
                                           'std_2.json', 
                                           Nodes, 
                                           Lines, 
                                           add_noise = True)
Meas_noiseless, mjson, stdjson = system_measurements(extended_path, 
                                           'measurements.json', 
                                           'std_2.json', 
                                           Nodes, 
                                           Lines, 
                                           add_noise = False)
Cons = system_constraints(Nodes)

# Nombres de las medidas en orden
names = [m['type'] + '_' + Nodes[m['node']]['name'] if m['line'] == None else m['type'] + '_' + Lines[np.abs(m['line'])]['From'] + '_' + Lines[np.abs(m['line'])]['To'] for m in Meas]
for item in zip(Meas, names):
    item[0]['name'] = item[1]
    
# Resolvemos el problema sin ruido
net_noiseless = lib.grid(Nodes, Lines, Meas_noiseless, Cons)
Results_noiseless = net_noiseless.state_estimation(tol = 1e-4, 
                                                   niter = 50, 
                                                   Huber = False, 
                                                   lmb = None, 
                                                   rn = True) 


# Se decide a qué medida atacar
######################################################################
######################################################################

ataque = ['P_LV0103']
for at in ataque:
    print(names.index(at))
    
num = names.index(ataque[0])
Meas[num]['value'] = 1.2*Meas[num]['value']


######################################################################
######################################################################


# Se construye la red y se lanza el estimador de estado (WLS con residuos normalizados)
net = lib.grid(Nodes, Lines, Meas, Cons)
Results_WLS = net.state_estimation(tol = 1e-4, 
                               niter = 50, 
                               Huber = False, 
                               lmb = None, 
                               rn = True)  
# print(net.res_norm)
# A = list(np.array(net.res)*np.array([np.sqrt(item) for item in np.diag(net.W)]))
# B = list(net.res)
# C = np.array([list(np.array(A).T), list(np.array(B).T), list(np.array(net.res_norm).T)]).T

# Máximo residuo normalizado antes de descartar ninguna medida  -> ajustamos lambda
lmb_value = Results_WLS['max_res']*0.5

# Restauramos todas las medidas y resolvemos Huber
net = lib.grid(Nodes, Lines, Meas, Cons)
Results_Huber = net.state_estimation(tol = 1e-4, 
                                    niter = 50, 
                                    Huber = True, 
                                    lmb = lmb_value, 
                                    rn = False)

# Guardamos los resultados
df_sol = pd.DataFrame(list(np.array([
                        Results_noiseless['solution'][-1],
                        Results_WLS['solution'][-1],
                        Results_Huber['solution'][-1]                    
                      ]).T), 
                      index=['ang_' + item['name'] for item in Nodes] + ['U_' + item['name'] for item in Nodes[1:]], 
                      columns=['Sin ruido', 'WLS', 'Huber'])

Results_WLS['std_sol'] = list(Results_WLS['std_sol'])
for item in Results_WLS['rm_meas']:
    Results_WLS['std_sol'].insert(item, None)
Results_WLS['std_sol'] = np.array(Results_WLS['std_sol'])

df_std = pd.DataFrame(list(np.array([
                        Results_WLS['std_sol'],
                        Results_Huber['std_sol']                   
                      ]).T), 
                      index=names,
                      columns=['WLS', 'Huber'])

ataque_WLS = ['ataque' if item == None else None for item in Results_WLS['std_sol']]
ataque_Huber = list(Results_Huber['Q'][-1])
df_ataque = pd.DataFrame(list(np.array([
                        ataque_WLS,
                        ataque_Huber                   
                      ]).T), 
                      index=names,
                      columns=['WLS', 'Huber'])


df_evol_Q = pd.DataFrame(list(np.array([
                        list(Results_Huber['Q'][index])
                        for index in range(len(Results_Huber['Q']))  
                      ]).T), 
                      index=names)


# Representación grafica
df_evol_Q = df_evol_Q.iloc[:, 3:]
import matplotlib.pyplot as plt
from pydae import plot_tools

col = plot_tools.set_style(plt)


# Configuración de los subplots
num_rows = len(df_evol_Q)  # Total de filas del DataFrame
num_subplots = 4  # Número de subplots (4 filas, 1 columna)
rows_per_subplot = (num_rows + num_subplots - 1) // num_subplots  # Filas por subplot

fig, axes = plt.subplots(num_subplots, 1, figsize=(12, 16))  # Crear los subplots
axes = axes.flatten()  # Asegurarse de que axes sea iterable

# Iterar por los subplots
for subplot_idx in range(num_subplots):
    ax = axes[subplot_idx]
    start_idx = subplot_idx * rows_per_subplot  # Índice de inicio para este subplot
    end_idx = min(start_idx + rows_per_subplot, num_rows)  # Índice de fin para este subplot
    
    # Extraer las filas correspondientes a este subplot
    subset = df_evol_Q.iloc[start_idx:end_idx]
    
    # Configurar eje X
    x_positions = np.arange(len(subset))  # Posiciones de las barras en el eje X
    width = 0.15  # Ancho de cada barra
    offsets = np.linspace(-width*2, width*2, len(col))  # Espaciado para las columnas
    
    # Dibujar las barras
    for i, column in enumerate(df_evol_Q.columns):
        values = subset[column].values  # Valores de la columna
        ax.bar(x_positions + offsets[i], values, width, label=column, color=col[i])
    
    # Configuración de etiquetas
    ax.set_xticks(x_positions)
    ax.set_xticklabels(subset.index)  
    

# Ajustar espaciado entre subplots
plt.tight_layout()
plt.show()














