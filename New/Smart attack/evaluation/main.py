import lib
import numpy as np
import json
import os

case = 0
percent = 5

# Taking the information about the network
path_topology = '../../../data/pv_2_3.json'
nodes, lines = lib.system_topology(path_topology)
constraints = lib.system_constraints(nodes)
# Renumbering the constraints references
for index, m in enumerate(constraints):
    constraints[index]['id'] = index


# Taking the measurements clean  
if case == 3:
    path_measurements = '../../../data/pv_2_3_180_13_00_pf_090neg/measurements.json'
    meas_neg = lib.system_measurements(path_measurements, nodes, lines, add_noise = False)  
else:
    path_measurements = '../../../data/pv_2_3_180_13_00_pf_090pos/measurements.json'
    meas_pos = lib.system_measurements(path_measurements, nodes, lines, add_noise = False)

# Clean network
net_clean_neg = lib.grid(path_topology='../../../data/pv_2_3.json', 
                         path_measurements='../../../data/pv_2_3_180_13_00_pf_090neg/measurements.json',
                         MT=True) 
net_clean_pos = lib.grid(path_topology='../../../data/pv_2_3.json', 
                         path_measurements='../../../data/pv_2_3_180_13_00_pf_090pos/measurements.json',
                         MT=True) 

# Taking the measurements attacked (the first 10 with lower index)
prefix = f"case_{case}_percent_{percent}_"
path_measurements = '../scenarios/with MT/'
files_filtered_conMT = [
    file for file in os.listdir(path_measurements)
    if file.startswith(prefix)
][:10]
meas_conMT = []
for filename in files_filtered_conMT:
    with open(path_measurements + filename, 'r') as f:
        data = json.load(f)
        meas_conMT.append(data)

path_measurements = '../scenarios/wo MT/'
files_filtered_sinMT = [
    file for file in os.listdir(path_measurements)
    if file.startswith(prefix)
][:10]
meas_sinMT = []
for filename in files_filtered_sinMT:
    with open(path_measurements + filename, 'r') as f:
        data = json.load(f)
        meas_sinMT.append(data)

path_measurements = '../scenarios/with PSM/'
files_filtered_conPSM = [
    file for file in os.listdir(path_measurements)
    if file.startswith(prefix)
][:10]
meas_conPSM = []
for filename in files_filtered_conPSM:
    with open(path_measurements + filename, 'r') as f:
        data = json.load(f)
        meas_conPSM.append(data)



# Networks with the data modified by the attack
net_conMT = [lib.grid(nodes = nodes, 
                      lines = lines, 
                      meas = m, 
                      constraints = constraints) for m in meas_conMT]  
net_sinMT = [lib.grid(nodes = nodes, 
                      lines = lines, 
                      meas = m, 
                      constraints = constraints) for m in meas_sinMT]     
net_conPSM = [lib.grid(nodes = nodes, 
                       lines = lines, 
                       meas = m, 
                       constraints = constraints) for m in meas_conPSM]     
                
# Solving the state estimation for each network
res_clen_neg = net_clean_neg.state_estimation(tol = 1e-4, 
                                              niter = 50, 
                                              Huber = True, 
                                              lmb = 2.5, 
                                              rn = False)
res_clen_pos = net_clean_pos.state_estimation(tol = 1e-4, 
                                              niter = 50, 
                                              Huber = True, 
                                              lmb = 2.5, 
                                              rn = False)
res_conMT, res_sinMT, res_conPSM = list(), list(), list()
for n in net_conMT:
    res_conMT = n.state_estimation(tol = 1e-4, 
                                   niter = 50, 
                                   Huber = True, 
                                   lmb = 2.5, 
                                   rn = False)
for n in net_sinMT:
    res_sinMT = n.state_estimation(tol = 1e-4, 
                                   niter = 50, 
                                   Huber = True, 
                                   lmb = 2.5, 
                                   rn = False)
for n in net_conPSM:
    res_conPSM = n.state_estimation(tol = 1e-4, 
                                    niter = 50, 
                                    Huber = True, 
                                    lmb = 2.5, 
                                    rn = False)

# Identifying the wrong measurements
ident_clean_neg = net_clean_neg.identification(res_clen_neg)
ident_clean_pos = net_clean_pos.identification(res_clen_pos)
ident_conMT, ident_sinMT, ident_conPSM = list(), list(), list()
for item in zip(net_conMT, res_conMT):
    ident_conMT.append(item[0].identification(item[1]))
for item in zip(net_sinMT, res_sinMT):
    ident_sinMT.append(item[0].identification(item[1]))
for item in zip(net_conPSM, res_conPSM):
    ident_conPSM.append(item[0].identification(item[1]))
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        