import lib
import numpy as np
import json

ano = 2024
mes = 8
dia = 10
hora = 5
minuto = 48

folder = 'scenarios'
P = []     

index = 0
while index < 288:   
    
    net = lib.grid(path_topology='pv_2_3.json', 
                   path_measurements='../' + folder + '/' + str(ano) + '_' + str(mes) + '_' + str(dia) + '_' + str(hora) + '_' + str(minuto) + '.json')
         
    P.append(net.meas[31].value)  
    
    minuto += 5
    if minuto >= 60:
        minuto -= 60
        hora += 1
        if hora >= 24:
            hora = 0
            dia += 1
    
    index += 1
    
with open('results/P_poi_integrated_' + folder + '.json', 'w') as json_file:
     json.dump(P, json_file, indent=4)