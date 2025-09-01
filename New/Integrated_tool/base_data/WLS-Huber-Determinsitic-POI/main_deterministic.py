import lib
import numpy as np
import json

ano = 2024
mes = 8
dia = 10
hora = 5
minuto = 48

folder = 'smart'
deterministic_detection = []     

# Voltages
U_index = [2, 6, 10, 14, 18, 22, 26, 33]

# P, Q, U, I at inverters
inv1 = [0, 1, 2, 3]
inv2 = [4, 5, 6, 7]
inv3 = [8, 9, 10, 11]
inv4 = [12, 13, 14, 15]
inv5 = [16, 17, 18, 19]
inv6 = [20, 21, 22, 23]

# I at inverters = feeder
mv1 = [3, 7, 11, 27]
mv2 = [15, 19, 23, 30]

# I at feeders = poi
poi = [27, 30, 34]

# without MV
mv =  [3, 7, 11, 15, 19, 23, 34]
s_lim = [0.33, 0.22, 0.33, 0.22, 0.22, 0.22]

index = 0
while index < 288:   
    
    net = lib.grid(path_topology='pv_2_3.json', 
                   path_measurements='../' + folder + '/' + str(ano) + '_' + str(mes) + '_' + str(dia) + '_' + str(hora) + '_' + str(minuto) + '.json')
    
    detect = False
    # Checking voltages
    for idx in U_index:
        if net.meas[idx].value > 1.1 or net.meas[idx].value < 0.9:
            detect = True
    # Checking inverters
    for inverter, slim in zip([inv1, inv2, inv3, inv4, inv5, inv6], s_lim):
        if net.meas[inverter[0]].value >= slim: # P > Sn
            detect = True
        if net.meas[inverter[1]].value >= np.sqrt(slim**2 - net.meas[inverter[0]].value**2): # Q > sqrt(Sn**2 - Pm**2)
            detect = True
        if np.sqrt(net.meas[inverter[3]].value) >= slim/net.meas[inverter[2]].value: # I > Sn/Un
            detect = True
        if np.abs( np.sqrt(net.meas[inverter[0]].value**2 + net.meas[inverter[1]].value**2) - net.meas[inverter[2]].value*np.sqrt(net.meas[inverter[3]].value) ) > 0.1: # sqrt(Pm**2 + Qm**2) == Um*Im
            detect = True
    # Checking currents
    # for m in [mv1, mv2, poi]:
    for m in [mv]:
        if np.abs( np.sum([np.sqrt(net.meas[item].value) for item in m[:-1]]) - np.sqrt(net.meas[m[-1]].value) ) > 0.1: # sum(i_inv) == i_mv
            detect = True
    # Adding to list
    deterministic_detection.append(detect)
     
    
    minuto += 5
    if minuto >= 60:
        minuto -= 60
        hora += 1
        if hora >= 24:
            hora = 0
            dia += 1
    
    index += 1
    
with open('results/deterministic_integrated_' + folder + '.json', 'w') as json_file:
     json.dump(deterministic_detection, json_file, indent=4)