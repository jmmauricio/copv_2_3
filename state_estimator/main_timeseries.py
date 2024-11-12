from lib_timeseries import system_topology, system_measurements, system_constraints
import lib

# Obtenemos la topología del parque
Nodes, Lines = system_topology('../data/pv_2_3.json')

# Para cada instante de tiempo
path = '../data/pv_2_3_180_'
for hour in ['08', '09', '10', '11', '12', '13', '14']:
    for minute in ['00', '15', '30', '45']:
        extended_path = path + hour + '_' + minute + '_pf_090neg/'
        print('Evaluando ' + hour + '_' + minute + '_pf_090neg')
        
        
        # Tomamos los valores de las medidas
        Meas = system_measurements(extended_path, 
                                   'measurements.json', 
                                   'std_1.json', 
                                   Nodes, 
                                   Lines, 
                                   add_noise = False)
        # Construimos las restricciones
        Cons = system_constraints(Nodes)

        # Generamos la red y resolvemos el problema de estiamción de estado
        net = lib.grid(Nodes, Lines, Meas, Cons)
        res, sol, H = net.state_estimation(niter = 15, 
                                           Huber = False, 
                                           lmb = 0.0001)
        net.report()
        
