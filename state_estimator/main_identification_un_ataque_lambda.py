from lib_timeseries import system_topology, system_measurements, system_constraints
import lib
import numpy as np
import pandas as pd
import copy
import random



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

Meas_seguridad = copy.deepcopy(Meas)

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

# Se decide a qué medida atacar: Primero P luego Q y luego U
######################################################################
######################################################################

names_P = [names[index] for index in range(len(names)) if names[index].startswith('P_LV')]
names_Q = [names[index] for index in range(len(names)) if names[index].startswith('Q_LV')]
names_U = [names[index] for index in range(len(names)) if names[index].startswith('U_LV')]

lmb_range = np.linspace(0.01, 50, 100)
Res__ide = []

for lmb_value in lmb_range:
    Res_ide = []
    for names_ataque in [names_P, names_Q, names_U]:
    
        Res_ide.append([])
        
        n_simus = 1000
        for _ in range(n_simus):
            
            
            Meas = copy.deepcopy(Meas_seguridad)    
            
            random_entries = random.sample(names_ataque, 2)
        
            for ataque in random_entries:
                if ataque.startswith('P'):
                    num = names.index(ataque)
                    magnitud = 0.8 + np.random.rand()*0.4
                if ataque.startswith('Q'):
                    num = names.index(ataque)
                    magnitud = 0.8 + np.random.rand()*0.4
                if ataque.startswith('U'):
                    num = names.index(ataque)
                    magnitud = 0.98 + np.random.rand()*0.04
                Meas[num]['value'] = magnitud*Meas[num]['value'] 
            
            
            ######################################################################
            ######################################################################
        
            # Se construye la red y se lanza el estimador de estado (WLS con residuos normalizados)
            net = lib.grid(Nodes, Lines, Meas, Cons)
            Results_WLS = net.state_estimation(tol = 1e-4, 
                                           niter = 50, 
                                           Huber = False, 
                                           lmb = None, 
                                           rn = True)  
            
            # Máximo residuo normalizado antes de descartar ninguna medida  -> ajustamos lambda
            # lmb_value = 2#Results_WLS['max_res']*0.5
            
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
            df_evol_Q = df_evol_Q.iloc[:, 3:]
            
            # Tratamos de identificar el ciber ataque
            n_cols = 3
            if df_evol_Q.shape[1] < n_cols:
                result_rows = []  # Return an empty list if there are fewer than 4 columns
            else:
                # Step 1: Identify rows where the final value in the last column is less than 1
                final_value_condition = df_evol_Q.iloc[:, -1] < 1
            
                # Step 2: Check if the last 4 values in these rows are decreasing
                def is_decreasing(row):
                    last_four_values = row.iloc[-n_cols:]
                    return all(last_four_values.diff().dropna() < 0)
            
                def is_decreasing_first_cols(row):
                    first_values = row.iloc[:n_cols]  # Tomar las primeras n_cols columnas
                    return first_values.is_monotonic_decreasing
                
                decreasing_condition = df_evol_Q[final_value_condition].apply(is_decreasing, axis=1)
            
                # Step 3: Extract the names of the rows that satisfy both conditions
                result_rows = df_evol_Q[final_value_condition].index[decreasing_condition].tolist()
        
            print(f'Ataque sobre: {ataque}, identificación: {result_rows}\n')
            
            # 0 detecta
            # 1 detecta y detecta alguno más incorrecto
            # 2 detecta incorrecto
            # 3 no detecta nada
            if ataque in result_rows:
                if len(result_rows) == 1:
                    Res_ide[-1].append(0)
                else:
                    Res_ide[-1].append(1)
            else:
                if len(result_rows) == 0:            
                    Res_ide[-1].append(3)
                else:    
                    Res_ide[-1].append(2)
        Res__ide.append(Res_ide)
            

import matplotlib.pyplot as plt
from collections import Counter
from pydae import plot_tools
colors = plot_tools.set_style(plt)
colors.pop(3)

# Initialize the figure and axes
fig, axes = plt.subplots(3, 1, figsize=(8, 10), sharex=True)

# Colors for the different numbers
labels = ['Count of 0', 'Count of 1', 'Count of 2', 'Count of 3']

# Iterate through the three sublists
for i, ax in enumerate(axes):
    counts = {num: [] for num in range(4)}  # Dictionary to store counts for each number
    
    for idx in range(len(lmb_range)):
        sublist = Res__ide[idx][i]
        for num in range(4):
            counts[num].append(sublist.count(num))
    
    # Plot the counts
    for num in range(4):
        ax.plot(lmb_range, counts[num], marker='o', color=colors[num], label=labels[num])
    
    ax.legend()
    ax.grid(True)

# Set the shared x-axis label
axes[-1].set_xlabel('$\lambda$')
plt.show()




import matplotlib.pyplot as plt
from collections import Counter
from pydae import plot_tools

# Set style and colors
colors = plot_tools.set_style(plt)
colors.pop(3)

# Initialize the figure and axes
fig, axes = plt.subplots(3, 1, figsize=(8, 10), sharex=True)

# Labels for the different numbers
labels = ['Detection', 'Detection and others', 'Incorrect detection', 'No detection']

# Iterate through the three sublists
for i, ax in enumerate(axes):
    counts = {num: [] for num in range(4)}  # Dictionary to store counts for each number
    
    for idx in range(len(lmb_range)):
        sublist = Res__ide[idx][i]
        for num in range(4):
            counts[num].append(sublist.count(num))
    
    # Convert dictionary to list of lists for stackplot
    values = [counts[num] for num in range(4)]
    
    # Create the stacked area plot
    ax.stackplot(lmb_range, *values, labels=labels, colors=colors, alpha=0.6)    
    
    ax.grid(True)

# Set the shared x-axis label
axes[0].set_ylabel('$P$')
axes[1].set_ylabel('$Q$')
axes[2].set_ylabel('$U$')

axes[-1].set_xlabel('$\lambda$')
axes[-1].legend()
plt.show()

