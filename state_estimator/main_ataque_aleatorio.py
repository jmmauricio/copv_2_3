from lib_timeseries import system_topology, system_measurements, system_constraints
import lib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pydae import plot_tools
import copy

col = plot_tools.set_style(plt)
f, ax = plt.subplots(2, 3, figsize=(18, 8))

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


n_ataques  = 10
names_ataque = [names_P*n_ataques, names_Q*n_ataques, names_U*n_ataques]

for index_PQU in range(3):
    
    minimos_U = []
    minimos_ang = []
    Meas = copy.deepcopy(Meas_seguridad)
    for ataque in names_ataque[index_PQU]:
        if ataque.startswith('P'):
            num = names.index(ataque)
            magnitud = 0.8 + np.random.rand()*0.4
            Meas[num]['value'] = magnitud*Meas[num]['value']    
            color_plot = col[0]
            color_marker = col[1]
        if ataque.startswith('Q'):
            num = names.index(ataque)
            magnitud = 0.8 + np.random.rand()*0.4
            Meas[num]['value'] = magnitud*Meas[num]['value']  
            color_plot = col[1]
            color_marker = col[0]
        if ataque.startswith('U'):
            num = names.index(ataque)
            magnitud = 0.98 + np.random.rand()*0.04
            Meas[num]['value'] = magnitud*Meas[num]['value']  
            color_plot = col[2]
            color_marker = 'k'
    
    
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
        lmb_range = np.linspace(0.01, 6, 100)
        for lmb_value in lmb_range:
        
            # Restauramos todas las medidas y resolvemos Huber
            net = lib.grid(Nodes, Lines, Meas, Cons)
            Results_Huber = net.state_estimation(tol = 1e-4, 
                                                niter = 50, 
                                                Huber = True, 
                                                lmb = lmb_value, 
                                                rn = False)
            Results_Huber_lmb.append(Results_Huber)
        
        
     
        
        
        U_noiseless = Results_noiseless['solution'][-1][14:]
        ang_noiseless = Results_noiseless['solution'][-1][:14]
        
        U_WLS = Results_WLS['solution'][-1][14:]
        ang_WLS = Results_WLS['solution'][-1][:14]
        
        error_U_WLS = np.linalg.norm(U_WLS - U_noiseless)
        error_ang_WLS = np.linalg.norm(ang_WLS - ang_noiseless)
            
        
        error_U_Huber = []
        error_ang_Huber = []
        for index in range(len(Results_Huber_lmb)):
            U_H = Results_Huber_lmb[index]['solution'][-1][14:]
            ang_H = Results_Huber_lmb[index]['solution'][-1][:14]
        
            error_U_H = np.linalg.norm(U_H - U_noiseless)
            error_ang_H = np.linalg.norm(ang_H - ang_noiseless)
            
            error_U_Huber.append(error_U_H)
            error_ang_Huber.append(error_ang_H)
        
        ax[0,index_PQU].plot(lmb_range, error_U_Huber, color=color_plot)
        ax[1,index_PQU].plot(lmb_range, error_ang_Huber, color=color_plot)
        
        min_value = np.min(error_U_Huber)
        min_index = list(error_U_Huber).index(min_value)
        minimos_U.append((lmb_range[min_index], error_U_Huber[min_index], color_plot))
        
        
        min_value = np.min(error_ang_Huber)
        min_index = list(error_ang_Huber).index(min_value)
        minimos_ang.append((lmb_range[min_index], error_ang_Huber[min_index], color_plot))
             
                
    for item in minimos_U:         
        ax[0,index_PQU].plot(item[0], item[1], color=color_marker, marker = "*")
    for item in minimos_ang:         
        ax[1,index_PQU].plot(item[0], item[1], color=color_marker, marker = "*")
        
        
    ax[1,index_PQU].set_xlabel(r'$\lambda$')
    ax[0,index_PQU].set_ylabel(r'$||U-\hat{U}||_2$')
    ax[1,index_PQU].set_ylabel(r'$||\theta-\hat{\theta}||_2$')
    
    ax[0,index_PQU].grid(True)
    ax[1,index_PQU].grid(True)
    
    leg_val = ['P','Q','U']
    
    ax[0,index_PQU].legend(leg_val[index_PQU])
    
    
    





















