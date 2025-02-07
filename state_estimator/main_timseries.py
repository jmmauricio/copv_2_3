import lib
from lib_timeseries import system_topology, system_measurements, system_constraints

path = ['../data/pv_2_3_180_', '../data_Cati/pv_2_3_180_']
case = ['090neg', '090pos', '100pos']
for c in case:
    for hour in ['08', '09', '10', '11', '12', '13', '14']:
        for minute in ['00', '15', '30', '45']:
            
            sheet_name = hour + '_' + minute + '_pf_' + c
            extended_path = [path[0] + hour + '_' + minute + '_pf_' + c + '/',
                             path[1] + hour + '_' + minute + '_pf_' + c + '/']
            print('Evaluando ' + hour + '_' + minute + '_pf_090neg')

            Nodes, Lines = system_topology('../data/pv_2_3.json')
            Meas, mjson, stdjson = system_measurements(extended_path, 
                                                       'measurements.json', 
                                                       'std_1.json', 
                                                       Nodes, 
                                                       Lines, 
                                                       add_noise = False)
            Cons = system_constraints(Nodes)
            
            net = lib.grid(Nodes, Lines, Meas, Cons)
            Resultados_WLS = net.state_estimation(tol = 1e-6, 
                                                  niter = 30, 
                                                  Huber = False, 
                                                  lmb = None, 
                                                  rn = True)
