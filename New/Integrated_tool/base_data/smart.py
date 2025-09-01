import json
import lib
import numpy as np

# inicio
año = 2024
mes = 8
dia = 10
hora = 5
minuto = 48

# año = 2024
# mes = 8
# dia = 10
# hora = 14
# minuto = 18


# Ataque inteligente
line = 13
nmeas = 31
amplitude = 0.8
tipo = 'P'
        
# node = 5
# nmeas = 6
# amplitude = 0.98
# tipo = 'U'

contador = 0
while contador < 288:

    with open(f'scenarios/{año}_{mes}_{dia}_{hora}_{minuto}.json', 'r') as fp:
        meas = json.load(fp)
        
        
    net_clean = lib.grid(path_topology='pv_2_3.json', 
               path_measurements=f'scenarios/{año}_{mes}_{dia}_{hora}_{minuto}.json')   
    net = lib.grid(path_topology='pv_2_3.json', 
               path_measurements=f'scenarios/{año}_{mes}_{dia}_{hora}_{minuto}.json')     
    sol_clean = net_clean.state_estimation(tol = 1e-4, 
                                niter = 50, 
                                Huber = True, 
                                lmb = 2.5, 
                                rn = False)  
    meas_at, constraints = net.data
    
    n = len(meas_at)
    meas_attacked = [5, 10, 15, 20]
    keys = [item for item in meas.keys()]
    keys_attacked = [keys[idx] for idx in meas_attacked]
    meas_safe = [i for i in list(range(n)) if i not in meas_attacked]
    
    
    for meas_index in meas_safe:
        net.meas[meas_index].std = 1e-5
        
        
    std_pqui = {'P': 0.020000, 'Q': 0.002000, 'U': 0.002500, 'I': 0.010000 }
    for meas_index in meas_attacked:
        net.meas[meas_index].std = std_pqui[meas_at[meas_index]['type']] 

           
    id_ref = net.constrained_meas[-1].ref + 1
    actual_state = net_clean.lines[line].Pji
    net.constrained_meas.append(lib.measurement(id_ref, None, line, tipo, -amplitude*actual_state, 0, net.nodes, net.lines, net.n))        
    net.meas[nmeas].value = amplitude*actual_state
    
    
    # Obtaining the "smart" attack
    solution = net.state_estimation(tol = 1e-4, 
                                    niter = 50, 
                                    Huber = False, 
                                    lmb = 2.5, 
                                    rn = False)
    
    for item in zip(keys_attacked, meas_attacked):
        meas[item[0]] = solution['z_output'][item[1]]        
    meas[keys[nmeas]] = solution['z_output'][nmeas]
    
    
    
    with open(f'smart/{año}_{mes}_{dia}_{hora}_{minuto}.json', 'w', encoding='utf-8') as f:
        json.dump(meas, f, ensure_ascii=False, indent=2)    
    
    minuto += 5
    if minuto >= 60:
        minuto -= 60
        hora += 1
        if hora >= 24:
            hora = 0
            dia += 1
    
    contador += 1