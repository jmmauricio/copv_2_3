from lib_timeseries import system_topology, system_measurements, system_constraints
import lib
import pandas as pd
from openpyxl import Workbook

case = ['090neg', '090pos', '100pos']
workbook = Workbook()
workbook.save("Results_WLS_std1.xlsx")



# Obtenemos la topología del parque
Nodes, Lines = system_topology('../data/pv_2_3.json')

# Para cada instante de tiempo
path = ['../data/pv_2_3_180_', '../data_Cati/pv_2_3_180_']
for c in case:
    for hour in ['08', '09', '10', '11', '12', '13', '14']:
        for minute in ['00', '15', '30', '45']:
            sheet_name = hour + '_' + minute + '_pf_' + c
            extended_path = [path[0] + hour + '_' + minute + '_pf_' + c + '/',
                             path[1] + hour + '_' + minute + '_pf_' + c + '/']
            print('Evaluando ' + hour + '_' + minute + '_pf_090neg')
            
            
            # Tomamos los valores de las medidas
            Meas, mjson, stdjson = system_measurements(extended_path, 
                                                       'measurements.json', 
                                                       'std_1.json', 
                                                       Nodes, 
                                                       Lines, 
                                                       add_noise = True)
            # Construimos las restricciones
            Cons = system_constraints(Nodes)
    
            # Generamos la red y resolvemos el problema de estiamción de estado
            net = lib.grid(Nodes, Lines, Meas, Cons)
            res, sol, H, std_sol = net.state_estimation(niter = 15, 
                                                        Huber = False, 
                                                        lmb = 0.0001)
            net.norm_res()
            net.report()
            
            # Escribimos los resultados
            df = pd.DataFrame()
            df['Nombre'] = list(mjson.keys())
            df['Medidas'] = [mjson[item] if item[0] != 'I' else mjson[item]**2 for item in mjson]
            df['Std medidas'] = [item.std for item in net.meas]
            df['Medidas ruidosas'] = [item.value for item in net.meas]
            df['Estimación'] = [item.h() for item in net.meas]
            df['Residuos'] = [item.value - item.h() for item in net.meas]
            df['Std solucion'] = list(std_sol)
            df['Residuos normalizados'] = net.res_norm
            
            with pd.ExcelWriter("Results_WLS_std1.xlsx", engine="openpyxl", mode="a") as writer:
                df.to_excel(writer, sheet_name=sheet_name, index=False)
        
# Excel: Key de medidas, medidas sin ruido, std, medidas con ruido, estimacion, residuos, std solucion