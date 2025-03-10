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
                                           add_noise = True,
                                           corrientes = True)
Meas_noiseless, mjson, stdjson = system_measurements(extended_path, 
                                           'measurements.json', 
                                           'std_2.json', 
                                           Nodes, 
                                           Lines, 
                                           add_noise = False,
                                           corrientes = True)
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

ataque = ['P_LV0101']
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
lmb_value = 5#Results_WLS['max_res']*0.5

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

from openpyxl import load_workbook
name_xlsx = 'Results_basico.xlsx'

try:
    book = load_workbook(name_xlsx) 
except FileNotFoundError:
    book = None
    
if book:
    with pd.ExcelWriter(name_xlsx, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        df_sol.to_excel(writer, sheet_name='soluciones', index=True)
        df_std.to_excel(writer, sheet_name='desviaciones', index=True)
        df_ataque.to_excel(writer, sheet_name='ataque', index=True)
        df_evol_Q.to_excel(writer, sheet_name='Q', index=True)
else:
    with pd.ExcelWriter(name_xlsx, engine='openpyxl', mode='w') as writer:
        df_sol.to_excel(writer, sheet_name='soluciones', index=True)
        df_std.to_excel(writer, sheet_name='desviaciones', index=True)
        df_ataque.to_excel(writer, sheet_name='ataque', index=True)
        df_evol_Q.to_excel(writer, sheet_name='Q', index=True)



# Generador de medidas
dict_medidas = {}
for node in net_noiseless.nodes:
    if node.name != 'GRID':
        dict_medidas['U_' + node.name] = node.V
        dict_medidas['P_' + node.name] = node.P
        dict_medidas['Q_' + node.name] = node.Q
    
for line in net_noiseless.lines:
    if line.nodes[0].name != 'GRID' and line.nodes[1].name != 'GRID':
        dict_medidas['P_' + line.nodes[0].name + '_' + line.nodes[1].name] = line.Pij
        dict_medidas['Q_' + line.nodes[0].name + '_' + line.nodes[1].name] = line.Qij
        dict_medidas['P_' + line.nodes[1].name + '_' + line.nodes[0].name] = line.Pji
        dict_medidas['Q_' + line.nodes[1].name + '_' + line.nodes[0].name] = line.Qji

import json
with open('medidas_nuevas.json', 'w') as file:
    json.dump(dict_medidas, file, 
        indent=4,  
        separators=(',', ': ')
        )




