import lib
import numpy as np
import random
import json



for percent_attacked in [5, 10, 25, 50]:
    for scenario in range(10):
        n_simu = 0
        while n_simu < 20:

            # hyper-parameters
            # percent_attacked = 50
            # scenario = 0
            
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
                case 4:        
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
                    
                    
                    
            
            
            # Constucting the network object
            path = ['../../../data/pv_2_3_180_', '../../../data_Cati/pv_2_3_180_']
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
                    print(f'{m.ref}: {m.tipo} at node {m.node_name}')       
                else:
                    print(f'{m.ref}: {m.tipo} at line {m.line_name}')  
            print('')     
            
            
            # Selecting the measurements that the attack can modify
            n = len(meas_at)
            n_attacked = int(np.round(n*percent_attacked/100))
            meas_attacked = list(random.sample(list(range(n)), n_attacked))
            meas_safe = [i for i in list(range(n)) if i not in meas_attacked]
            
            
            # Assigning a large std to the measurements that CANNOT be modified by the attack
            # They are not considered in the objective function of the proposed optimization
            for meas_index in meas_safe:
                net.meas[meas_index].std = 1e-5
                
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
            
            # If the estimator has converged
            if len(solution['solution']) != 0:
                n_simu += 1
               
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
                 
                # Saving the attack
                print(n_simu)
                with open(f'with MT/case_{scenario}_percent_{percent_attacked}_index_{int(optimal_index)}_{int((optimal_index-int(optimal_index))*1000000)}.json', 'w') as json_file:
                        json.dump(meas_at, json_file, indent=4)
    
    
    
    
