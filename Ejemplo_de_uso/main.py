import lib

# Definir de forma adecuada las magnitudes base
Sbase = 100e3
Ubase = 20e3
Zbase = (Ubase**2)/Sbase

# Nodos - Hay que darle id, nombre y decir si hay un elemento shunt
Nodes = [{'id': 1, 'name': 'Nodo 1', 'B': 0},
         {'id': 2, 'name': 'Nodo 2', 'B': 0},
         {'id': 3, 'name': 'Nodo 3', 'B': 0}]

# Lines -> B es la mitad de la susceptancia (la que hay en cada pata)
# La conexión con los nodos se indica por el "name" y no por el "id"
Lines = [{'id': 1,  'From': 'Nodo 1',  'To': 'Nodo 2',  'R': 0.01, 'X': 0.03, 'B': 0 , 'Transformer': False, 'rt': 1},  
         {'id': 2,  'From': 'Nodo 1',  'To': 'Nodo 3',  'R': 0.02, 'X': 0.05, 'B': 0 , 'Transformer': False, 'rt': 1},
         {'id': 3,  'From': 'Nodo 2',  'To': 'Nodo 3',  'R': 0.03, 'X': 0.08, 'B': 0 , 'Transformer': False, 'rt': 1}]

# Measurements
# Se indica el nodo o la línea por su "id"!
Meas = [{'id': 1, 'node': None, 'line': 1,    'type': 'P', 'value':  0.888,    'std': 0.008},
        {'id': 2, 'node': None, 'line': 2,    'type': 'P', 'value':  1.173,    'std': 0.008},
        {'id': 3, 'node': 2,    'line': None, 'type': 'P', 'value': -0.501,    'std': 0.010},
        {'id': 4, 'node': None, 'line': 1,    'type': 'Q', 'value':  0.568,    'std': 0.008},
        {'id': 5, 'node': None, 'line': 2,    'type': 'Q', 'value':  0.663,    'std': 0.008},
        {'id': 6, 'node': 2,    'line': None, 'type': 'Q', 'value': -0.286,    'std': 0.010},
        {'id': 7, 'node': 1,    'line': None, 'type': 'U', 'value':  1.006,    'std': 0.005},
        {'id': 8, 'node': 2,    'line': None, 'type': 'U', 'value':  0.968,    'std': 0.004}]

# Si se definen restricciones, al menos, hay que detallar: 'id', 'node', 'line', 'type', 'value' del mismo modo que se hizo ocn las medidas
Cons =[]

# Se contruye el objeto red
net = lib.grid(Nodes, Lines, Meas, Cons)

# Se resuelve la estimación de estado utilizando WLS
Results_WLS = net.state_estimation(tol = 1e-4, 
                                niter = 50, 
                                Huber = False, 
                                lmb = None, 
                                rn = True)  

# Se resuelve la estimación de estado utilizando Huber
Results_Huber = net.state_estimation(tol = 1e-4, 
                                    niter = 50, 
                                    Huber = True, 
                                    lmb = 3, 
                                    rn = False)

# Sacamnos resultados
tensiones = [node.V for node in net.nodes]
angulos = [node.theta for node in net.nodes]

print(tensiones)
print(angulos)




