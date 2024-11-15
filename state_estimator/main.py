import lib
from lib_timeseries import system_topology, system_measurements, system_constraints
import pandas as pd

extended_path = ['../data/pv_2_3_180_14_45_pf_090neg/', '../data_Cati/pv_2_3_180_14_45_pf_090neg/']
Nodes, Lines = system_topology('../data/pv_2_3.json')
Meas, mjson, stdjson = system_measurements(extended_path, 
                                           'measurements.json', 
                                           'std_1.json', 
                                           Nodes, 
                                           Lines, 
                                           add_noise = True)
Cons = system_constraints(Nodes)

net = lib.grid(Nodes, Lines, Meas, Cons)
res, sol, H, std_sol = net.state_estimation(niter = 15, 
                                            Huber = False, 
                                            lmb = 0.0001)
net.norm_res()
net.report()


# Excel: Key de medidas, medidas sin ruido, std, medidas con ruido, estimacion, residuos, std solucion
df = pd.DataFrame()
df['Nombre'] = list(mjson.keys())
df['Medidas'] = [mjson[item] if item[0] != 'I' else mjson[item]**2 for item in mjson]
df['Std medidas'] = [item.std for item in net.meas]
df['Medidas ruidosas'] = [item.value for item in net.meas]
df['Estimación'] = [item.h() for item in net.meas]
df['Residuos'] = [item.value - item.h() for item in net.meas]
df['Std solucion'] = list(std_sol)
df['Residuos normalizados'] = net.res_norm
df.to_excel("Results_WLS_std1.xlsx", sheet_name='pv_2_3_180_14_45_pf_090neg')
