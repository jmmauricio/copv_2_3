import lib
import numpy as np
import json

ano = 2024
mes = 8
dia = 10
hora = 5
minuto = 48

folder = 'smart'
detection_WLS = []     

index = 0
while index < 288:   
    
    net = lib.grid(path_topology='pv_2_3.json', 
                   path_measurements='../' + folder +'/' + str(ano) + '_' + str(mes) + '_' + str(dia) + '_' + str(hora) + '_' + str(minuto) + '.json')
         
    try:    
        Results = net.state_estimation(tol = 1e-4, 
                                       niter = 50, 
                                       Huber = False,
                                       lmb = 2.5,
                                       rn = True)  
        # net.report()
        if len(Results['pop']) == 0:
            detection_WLS.append(False)
        else:
            detection_WLS.append(True)
    except:
        detection_WLS.append(False)
            
    minuto += 5
    if minuto >= 60:
        minuto -= 60
        hora += 1
        if hora >= 24:
            hora = 0
            dia += 1
    
    index += 1
    
    
with open('results/WLS_integrated_' + folder + '.json', 'w') as json_file:
     json.dump(detection_WLS, json_file, indent=4)