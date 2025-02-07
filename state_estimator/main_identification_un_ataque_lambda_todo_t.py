from lib_timeseries import system_topology, system_measurements, system_constraints
import lib
import numpy as np
import pandas as pd
import copy
import random

resultados = dict()

path = ['../data/pv_2_3_180_', '../data_Cati/pv_2_3_180_']
case = ['090neg', '090pos', '100pos']
for c in case:
    resultados[c] = dict()
    for hour in ['08', '09', '10', '11', '12', '13', '14']:
        resultados[c][hour] = dict()
        for minute in ['00', '15', '30', '45']:
            
            
            sheet_name = hour + '_' + minute + '_pf_' + c
            extended_path = [path[0] + hour + '_' + minute + '_pf_' + c + '/',
                             path[1] + hour + '_' + minute + '_pf_' + c + '/']

            Nodes, Lines = system_topology('../data/pv_2_3.json')
            Meas, mjson, stdjson = system_measurements(extended_path, 
                                                       'measurements.json', 
                                                       'std_2.json', 
                                                       Nodes, 
                                                       Lines, 
                                                       add_noise = True)
            Cons = system_constraints(Nodes)
            Meas_seguridad = copy.deepcopy(Meas)
            
            # Nombres de las medidas en orden
            names = [m['type'] + '_' + Nodes[m['node']]['name'] if m['line'] == None else m['type'] + '_' + Lines[np.abs(m['line'])]['From'] + '_' + Lines[np.abs(m['line'])]['To'] for m in Meas]
            for item in zip(Meas, names):
                item[0]['name'] = item[1]
                
            net = lib.grid(Nodes, Lines, Meas, Cons)

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
                        lmb_value = 2#Results_WLS['max_res']*0.5
                        
                        # Restauramos todas las medidas y resolvemos Huber
                        net = lib.grid(Nodes, Lines, Meas, Cons)
                        Results_Huber = net.state_estimation(tol = 1e-4, 
                                                            niter = 50, 
                                                            Huber = True, 
                                                            lmb = lmb_value, 
                                                            rn = False)
                        
                        # Guardamos los resultados
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
                        
            resultados[c][hour][minute] = Res__ide

