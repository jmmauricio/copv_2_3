import lib
from lib_timeseries import system_topology, system_measurements, system_constraints


extended_path = ['../data/pv_2_3_180_14_45_pf_090neg/', '../data_Cati/pv_2_3_180_14_45_pf_090neg/']
Nodes, Lines = system_topology('../data/pv_2_3.json')
Meas = system_measurements(extended_path, 
                           'measurements.json', 
                           'std_1.json', 
                           Nodes, 
                           Lines, 
                           add_noise = False)
Cons = system_constraints(Nodes)

net = lib.grid(Nodes, Lines, Meas, Cons)
res, sol, H = net.state_estimation(niter = 15, 
                                   Huber = False, 
                                   lmb = 0.0001)
net.report()

