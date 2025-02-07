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
Meas[num]['value'] = 0.8*Meas[num]['value']


######################################################################
######################################################################


# Se construye la red y se lanza el estimador de estado (WLS con residuos normalizados)
net = lib.grid(Nodes, Lines, Meas, Cons)
Results_WLS = net.state_estimation(tol = 1e-4, 
                               niter = 50, 
                               Huber = False, 
                               lmb = None, 
                               rn = True)  

# Barremos lambda:
Results_Huber_lmb = []
lmb_range = np.linspace(0.01, 3, 100)
for lmb_value in lmb_range:

    # Restauramos todas las medidas y resolvemos Huber
    net = lib.grid(Nodes, Lines, Meas, Cons)
    Results_Huber = net.state_estimation(tol = 1e-4, 
                                        niter = 50, 
                                        Huber = True, 
                                        lmb = lmb_value, 
                                        rn = False)
    Results_Huber_lmb.append(Results_Huber)


import matplotlib.pyplot as plt
from pydae import plot_tools

col = plot_tools.set_style(plt)
f, ax = plt.subplots(2, 1, figsize=(7, 5))


U_noiseless = Results_noiseless['solution'][-1][14:]
ang_noiseless = Results_noiseless['solution'][-1][:14]

U_WLS = Results_WLS['solution'][-1][14:]
ang_WLS = Results_WLS['solution'][-1][:14]

error_U_WLS = np.linalg.norm(U_WLS - U_noiseless)
error_ang_WLS = np.linalg.norm(ang_WLS - ang_noiseless)

# ax[0].plot(lmb_range, error_U_WLS*np.ones(len(lmb_range)), color=col[0])
# ax[1].plot(lmb_range, error_ang_WLS*np.ones(len(lmb_range)), color=col[0])


error_U_Huber = []
error_ang_Huber = []
for index in range(len(Results_Huber_lmb)):
    U_H = Results_Huber_lmb[index]['solution'][-1][14:]
    ang_H = Results_Huber_lmb[index]['solution'][-1][:14]

    error_U_H = np.linalg.norm(U_H - U_noiseless)
    error_ang_H = np.linalg.norm(ang_H - ang_noiseless)
    
    error_U_Huber.append(error_U_H)
    error_ang_Huber.append(error_ang_H)
    
ax[0].plot(lmb_range, error_U_Huber, color=col[1])
ax[1].plot(lmb_range, error_ang_Huber, color=col[1])
    
ax[1].set_xlabel(r'$\lambda$')
ax[0].set_ylabel(r'$||U-\hat{U}||_2$')
ax[1].set_ylabel(r'$||\theta-\hat{\theta}||_2$')

ax[0].grid(True)
ax[1].grid(True)

ax[0].legend({'WLS','Huber'})


























