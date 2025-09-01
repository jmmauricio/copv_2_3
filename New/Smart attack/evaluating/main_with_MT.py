import lib
import numpy as np
import random
import json
import copy

random.seed(0)

            
res_ind = {'Precision': [],
           'Recall': [],
           'Accuracy': [],
           'F1': [],
           'z': [],
           'norm2': [],
           'norminf': []}            
Res = {
       '5' : {'0': copy.deepcopy(res_ind), '1': copy.deepcopy(res_ind), '2': copy.deepcopy(res_ind), '3': copy.deepcopy(res_ind), '4': copy.deepcopy(res_ind), 
              '5': copy.deepcopy(res_ind), '6': copy.deepcopy(res_ind), '7': copy.deepcopy(res_ind), '8': copy.deepcopy(res_ind), '9': copy.deepcopy(res_ind)},
       '10': {'0': copy.deepcopy(res_ind), '1': copy.deepcopy(res_ind), '2': copy.deepcopy(res_ind), '3': copy.deepcopy(res_ind), '4': copy.deepcopy(res_ind), 
              '5': copy.deepcopy(res_ind), '6': copy.deepcopy(res_ind), '7': copy.deepcopy(res_ind), '8': copy.deepcopy(res_ind), '9': copy.deepcopy(res_ind)},
       '20': {'0': copy.deepcopy(res_ind), '1': copy.deepcopy(res_ind), '2': copy.deepcopy(res_ind), '3': copy.deepcopy(res_ind), '4': copy.deepcopy(res_ind), 
              '5': copy.deepcopy(res_ind), '6': copy.deepcopy(res_ind), '7': copy.deepcopy(res_ind), '8': copy.deepcopy(res_ind), '9': copy.deepcopy(res_ind)},
       '40': {'0': copy.deepcopy(res_ind), '1': copy.deepcopy(res_ind), '2': copy.deepcopy(res_ind), '3': copy.deepcopy(res_ind), '4': copy.deepcopy(res_ind), 
              '5': copy.deepcopy(res_ind), '6': copy.deepcopy(res_ind), '7': copy.deepcopy(res_ind), '8': copy.deepcopy(res_ind), '9': copy.deepcopy(res_ind)},
      }           
    

for percent_attacked in [5, 10, 20, 40]:
    
    for scenario in range(10):
        
        n_simu = 0
        while n_simu < 20:
            
            match scenario:
                case 0:        
                    # Disparo inversor -> Ataque inversor -> U_atacada < U_medida -> LV0102: 0.98 por su valor
                    node = 5
                    nmeas = 6
                    amplitude = 0.98
                    minute = '00'
                    c = '090pos'
                    hour = '13'
                    tipo = 'U'
                case 1:        
                    # Disparo inversor -> Ataque POI -> Q_atacada < Q_medida -> 0.98 por su valor
                    line = 13
                    nmeas = 32
                    amplitude = 0.8
                    minute = '00'
                    c = '090pos'
                    hour = '13'
                    tipo = 'Q'
                case 2:        
                    # Disparo inversor -> Ataque POI -> U_atacada < U_medida -> 0.98 por su valor
                    node = 1
                    nmeas = 33
                    amplitude = 0.98
                    minute = '00'
                    c = '090pos'
                    hour = '13'
                    tipo = 'U'
                case 3:        
                    # Disparo inversor -> Ataque POI -> U_atacada > U_medida -> 1.02 por su valor
                    node = 1
                    nmeas = 33
                    amplitude = 1.02
                    minute = '00'
                    c = '090neg'
                    hour = '13'
                    tipo = 'U'
                case 4:        # IGUAL QUE 1
                    # Afectación POI -> Ataque POI -> Q_atacada < Q_medida -> 0.98 por su valor
                    line = 13
                    nmeas = 32
                    amplitude = 0.8
                    minute = '00'
                    c = '090pos'
                    hour = '13'
                    tipo = 'Q'
                case 5:        
                    # Afectación POI -> Ataque POI -> Q_atacada > Q_medida -> 1.02 por su valor
                    line = 13
                    nmeas = 32
                    amplitude = 1.2
                    minute = '00'
                    c = '090pos'
                    hour = '13'
                    tipo = 'Q'
                case 6:        
                    # Afectación POI -> Ataque POI -> P_atacada < P_medida -> 0.98 por su valor
                    line = 13
                    nmeas = 31
                    amplitude = 0.8
                    minute = '00'
                    c = '090pos'
                    hour = '13'
                    tipo = 'P'
                case 7:        
                    # Afectación POI -> Ataque POI -> P_atacada > P_medida -> 1.02 por su valor
                    line = 13
                    nmeas = 31
                    amplitude = 1.2
                    minute = '00'
                    c = '090pos'
                    hour = '13'
                    tipo = 'P'
                case 8:        
                    # Afectación POI -> Ataque POI -> U_atacada < U_medida -> 0.98 por su valor
                    node = 1
                    nmeas = 33
                    amplitude = 0.98
                    minute = '00'
                    c = '090pos'
                    hour = '13'
                    tipo = 'U'
                case 9:        
                    # Afectación POI -> Ataque POI -> U_atacada > U_medida -> 1.02 por su valor
                    node = 1
                    nmeas = 33
                    amplitude = 1.02
                    minute = '00'
                    c = '090pos'
                    hour = '13'
                    tipo = 'U'
                                                 
                        
            # Constucting the network object and computing the real state of the network
            path = ['../../../data/pv_2_3_180_', 
                    '../../../data_Cati/pv_2_3_180_']
            net = lib.grid(path_topology='../../../data/pv_2_3.json', 
                           path_measurements='../../../data/pv_2_3_180_' + hour + '_00_pf_' + c + '/measurements.json',
                           MT=True)   
            net_clean = lib.grid(path_topology='../../../data/pv_2_3.json', 
                                 path_measurements='../../../data/pv_2_3_180_' + hour + '_00_pf_' + c + '/measurements.json',
                                 MT=True)   
            sol_clean = net_clean.state_estimation(tol = 1e-4, 
                                            niter = 50, 
                                            Huber = False, 
                                            lmb = 2.5, 
                                            rn = False)  
            meas_at, constraints = net.data
            
            # Printing all the measurements      
            print('Measurements gathered...')
            for m in net.meas:
                if hasattr(m, 'node'):
                    print(f'{m.ref}: {m.tipo} at node {m.node_name}: {m.value}')       
                else:
                    print(f'{m.ref}: {m.tipo} at line {m.line_name}: {m.value}')  
            print('')     
            
            
            # Selecting the measurements that the attack can modify
            n = len(meas_at)
            n_attacked = int(np.round(n*percent_attacked/100))
            meas_attacked = list(random.sample(list(range(n)), n_attacked))
            meas_safe = [i for i in list(range(n)) if i not in meas_attacked]
            
            
            # The measurements that CANNOT be modified by the attack
            # std_pqui = {'P': 0.020000, 'Q': 0.002000, 'U': 0.002500, 'I': 0.010000 }
            for meas_index in meas_safe:
                net.meas[meas_index].std = 1e-5
                # net.meas[meas_index].std = std_pqui[meas_at[meas_index]['type']]
                
            # Assigning regular std to the measurements that CAN be modified by the attack
            # NOT in the meas files since the operator does not know about the attack
            std_pqui = {'P': 0.020000, 'Q': 0.002000, 'U': 0.002500, 'I': 0.010000 }
            for meas_index in meas_attacked:
                net.meas[meas_index].std = std_pqui[meas_at[meas_index]['type']]
            
                    
            # Imposing the main constraint of the attack
            id_ref = net.constrained_meas[-1].ref + 1
            match tipo:
                case 'P':
                    actual_state = net_clean.lines[line].Pji
                case 'Q':
                    actual_state = net_clean.lines[line].Qji
                case 'U':
                    actual_state = net_clean.nodes[node].V
                    
            if tipo == 'U':
                net.constrained_meas.append(lib.measurement(id_ref, node, None, tipo, amplitude*actual_state, 0, net.nodes, net.lines, net.n))
            else:
                net.constrained_meas.append(lib.measurement(id_ref, None, line, tipo, amplitude*actual_state, 0, net.nodes, net.lines, net.n))
            net.meas[nmeas].value = amplitude*actual_state
            
            # Printing all the constraints      
            print('Constraints imposed...')    
            for m in net.constrained_meas:
                if hasattr(m, 'node'):
                    print(f'{m.ref}: {m.tipo} with value {m.value} at node {m.node_name}')       
                else:
                    print(f'{m.ref}: {m.tipo} with value {m.value} at line {m.line_name}')       
            print('')    
            
            # Obtaining the "smart" attack
            solution = net.state_estimation(tol = 1e-4, 
                                            niter = 50, 
                                            Huber = False, 
                                            lmb = 2.5, 
                                            rn = False)
            
            try:
                # Printing the state of the system and the modified output
                # Computing a performace index
                print('Smart attack output...') 
                optimal_index = 0
                for item in zip(meas_at, solution['z_output']):
                    if item[0]['node'] != None:
                        if item[0]['id'] in meas_attacked:
                            print(f"**{item[0]['type']}({net.nodes[item[0]['node']].name}): \t\t\t {item[0]['value']:.3f} --> {item[1]:.3f}")
                        else:
                            print(f"{item[0]['type']}({net.nodes[item[0]['node']].name}): \t\t\t {item[0]['value']:.3f} --> {item[1]:.3f}")
                    else:
                        if item[0]['id'] in meas_attacked:
                            print(f"**{item[0]['type']}({net.lines[abs(item[0]['line'])].nodes[0].name}-{net.lines[abs(item[0]['line'])].nodes[1].name}): \t {item[0]['value']:.3f} --> {item[1]:.3f}")
                        else:
                            print(f"{item[0]['type']}({net.lines[abs(item[0]['line'])].nodes[0].name}-{net.lines[abs(item[0]['line'])].nodes[1].name}): \t {item[0]['value']:.3f} --> {item[1]:.3f}")
                    optimal_index += (item[0]['value'] - item[1])**2
                    
                    
                # Assigning the new values to meas
                for meas_index in meas_attacked:
                    meas_at[meas_index]['value'] = solution['z_output'][meas_index]
                
                print(optimal_index)
                 
                # Taking the information about the network
                path_topology = '../../../data/pv_2_3.json'
                nodes, lines = lib.system_topology(path_topology)
                constraints = lib.system_constraints(nodes)
                # Renumbering the constraints references
                for index, m in enumerate(constraints):
                    constraints[index]['id'] = index
                
                # Networks with the data modified by the attack
                net_withMT = lib.grid(nodes = nodes, 
                                      lines = lines, 
                                      meas = meas_at, 
                                      constraints = constraints) 
                
                
                
                res_withMT = net_withMT.state_estimation(tol = 1e-4, 
                                                         niter = 50, 
                                                         Huber = True, 
                                                         lmb = 2.5, 
                                                         rn = False)
            
            
                # Identifying the wrong measurements
                ident_withMT = net_withMT.identification(res_withMT)
                meas_attacked.sort()
                
                print("Measurement attacked: " )
                [print(item) for item in meas_attacked]
                print("Identified as attacked: "  )
                [print(item) for item in ident_withMT]
                
                Q = np.array([list(res_withMT['Q'][index]) for index in range(len(res_withMT['Q']))]).T 
                Obs = Q[meas_attacked,:]
                
                        
                # Evaluating identification performance
                TP, TN, FP, FN = 0, 0, 0, 0
                for i in range(len(net.meas)):
                   is_attacked = i in meas_attacked # Attacked?               
                   is_identified = i in ident_withMT # Well-identified?
                              
                   # Classify the measurement and append to the appropriate list
                   if is_attacked and is_identified:
                       TP += 1
                   elif not is_attacked and not is_identified:
                       TN += 1
                   elif not is_attacked and is_identified:
                       FP += 1
                   elif is_attacked and not is_identified:
                       FN += 1
                
                z_estimada = [net_withMT.meas[idx].h() for idx in meas_attacked]
                z_exacta = [net_clean.meas[idx].h() for idx in meas_attacked]       
                Precision = TP/(TP+FP) if TP + FP !=0 else 0
                Recall = TP/(TP+FN) if TP + FN !=0 else 0
                Accuracy = (TP+TN)/(TP+TN+FP+FN)
                F1 = 2*Precision*Recall/(Precision + Recall) if Precision + Recall !=0 else 0
                z = np.linalg.norm(np.array(z_estimada) - np.array(z_exacta), 2)/len(z_estimada)
                x_clean = sol_clean['solution'][-1]
                x_Huber = res_withMT['solution'][-1]
                norm2 = np.linalg.norm(x_clean - x_Huber, 2)/len(x_clean)
                norminf = np.linalg.norm(x_clean - x_Huber, np.inf)
                
                print('')
                print(f'Precision: {Precision*100:.2f} %')
                print(f'Recall: {Recall*100:.2f} %')
                print(f'Accuracy: {Accuracy*100:.2f} %')
                print(f'F1: {F1*100:.2f} %')
                print(f'z: {z*100:.2f} %')
                print(f'norm2: {norm2*100:.2f} %')
                print(f'norminf: {norminf*100:.2f} %')
                
                Res[str(percent_attacked)][str(scenario)]['Precision'].append(Precision*100)
                Res[str(percent_attacked)][str(scenario)]['Recall'].append(Recall*100)
                Res[str(percent_attacked)][str(scenario)]['Accuracy'].append(Accuracy*100)
                Res[str(percent_attacked)][str(scenario)]['F1'].append(F1*100)
                Res[str(percent_attacked)][str(scenario)]['z'].append(z*100)
                Res[str(percent_attacked)][str(scenario)]['norm2'].append(norm2*100)
                Res[str(percent_attacked)][str(scenario)]['norminf'].append(norminf*100)
                
                n_simu += 1
                
            except:
                
                continue
                    
with open('results/with_MT.json', 'w') as json_file:
    json.dump(Res, json_file, indent=4)









