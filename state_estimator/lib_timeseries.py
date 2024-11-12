import json
import random

random.seed(1)

def system_topology(file):
    
    # Leemos los datos del fichero
    with open(file, 'r') as f:
        data = json.load(f)
        
    # Definimos las magnitudes base
    S_base_syst = data['system']['S_base'] 
    U_base = 20e3
    Z_base = (U_base**2)/S_base_syst
    
    # Construimos la lista de nodos
    Nodes = list()
    index = 1
    for index, item in enumerate(data['buses']):
        Nodes.append({'name': item['name'], 
                      'id': index, 
                      'B': 0} )
        
    # Construimos la lista de líneas
    Lines = list()
    for index, item in enumerate(data['lines']):
        if 'R_pu' in item.keys():
            Lines.append({
                'id': index,
                'From': item['bus_j'],
                'To': item['bus_k'],
                'R': item['R_pu']*S_base_syst/(item['S_mva']*1e6),
                'X': item['X_pu']*S_base_syst/(item['S_mva']*1e6),
                'B': item['Bs_pu']*(item['S_mva']*1e6/S_base_syst)/2, 
                'Transformer': False,
                'rt': 1
                })
        else:
            Lines.append({
                'id': index,
                'From': item['bus_j'],
                'To': item['bus_k'],
                'R': item['R_km']*item['km']/Z_base,
                'X': item['X_km']*item['km']/Z_base,
                'B': item['Bs_km']*item['km']*Z_base/2, 
                'Transformer': False,
                'rt': 1
                })
            
    # Construimos la lista de trasnformadores    
    index_lines = index + 1
    for index, item in enumerate(data['transformers']):
        Lines.append({
            'id': index_lines + index,
            'From': item['bus_j'],
            'To': item['bus_k'],
            'R': item['R_pu']*S_base_syst/(item['S_mva']*1e6),
            'X': item['X_pu']*S_base_syst/(item['S_mva']*1e6),
            'B': [0, 0], 
            'Transformer': True,
            'rt': 1
            })

    return Nodes, Lines


def system_measurements(path, meas_file, std_file, Nodes, Lines, add_noise = False):
    
    # Leemos los datos de los ficheros
    with open(path + meas_file, 'r') as f:
        data = json.load(f)
    # with open(path + std_file, 'r') as f:
    #     contenido = f.read()
    # contenido = contenido.replace('{', '').replace('}', '')
    # lineas = contenido.split('\n')
    # lineas = [linea.strip() for linea in lineas if linea.strip()]
    # contenido_corregido = ',\n'.join(lineas)
    # contenido_corregido = '{' + contenido_corregido + '}'
    # std_data = json.loads(contenido_corregido)
    
    # Construimos la lista de medidas
    Meas = list()
    for index_meas, item in enumerate(data.keys()):
        modified_item = item.split('_')
        # Si se trata de una medida en un nodo
        if len(modified_item) == 2:
            N = [d.get('id') if d.get('name') == modified_item[1] else -1 for d in Nodes]
            N.sort()
            N = N[-1]
            Meas.append({
                'id': index_meas,
                'node': N,
                'line': None,
                'type': modified_item[0],
                'value': data[item],
                'std': 0.0000001#std_data[item]
                })           
        # Si se trata de una medida en una línea
        if len(modified_item) == 3:
            for l in Lines:
                if l['From'] == modified_item[1] and l['To'] == modified_item[2]:
                    id_l = l['id']
                    break
                if l['From'] == modified_item[2] and l['To'] == modified_item[1]:
                    id_l = -l['id']
                    break               
            Meas.append({
                'id': index_meas,
                'node': None,
                'line': id_l,
                'type': modified_item[0],
                'value': data[item]**2 if modified_item[0] == 'I' else data[item],
                'std': 0.01#std_data[item]
                })
        index_meas += 1
        
    return Meas
    

def system_constraints(Nodes):      
    nodenames = [node['name'] for node in Nodes]
    Cons = []
    index = 0
    for nn in nodenames:
        if "LV" in nn or "GRID" in nn:
            pass
        else:
            N = [d.get('id') if d.get('name') == nn else -1 for d in Nodes]
            N.sort()
            N = N[-1]
            Cons.append({
                'id': index,
                'node': N,
                'line': None,
                'type': 'P',
                'value': 0.0,
                })
            Cons.append({
                'id': index,
                'node': N,
                'line': None,
                'type': 'Q',
                'value': 0.0,
                })
            index += 2
    return Cons



