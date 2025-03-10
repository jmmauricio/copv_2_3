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
    index = 0
    for item in data['buses']:
        if item['name'] != 'BESS':
            Nodes.append({'name': item['name'], 
                          'id': index, 
                          'B': 0} )
            index += 1
        
    # Construimos la lista de líneas
    Lines = list()
    index = 0
    for item in data['lines']:        
        if item['bus_j'] != 'BESS' and item['bus_k'] != 'BESS':
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
            index += 1
            
    # Construimos la lista de trasnformadores    
    index_lines = index 
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


def system_measurements(path, meas_file, std_file, Nodes, Lines, add_noise = False, corrientes = True):
    
    # Leemos los datos de los ficheros
    with open(path[0] + meas_file, 'r') as f:
        data = json.load(f)
    with open(path[1] + std_file, 'r') as f:
        std_data = json.load(f)
    std_data = {key.replace("POI_MV", "POIMV"): value for key, value in std_data.items()}
    
    
    # Construimos la lista de medidas
    Meas = list()
    index_meas_id = 0
    for index_meas, item in enumerate(data.keys()):
        modified_item = item.split('_')
        # Si se trata de una medida en un nodo
        if len(modified_item) == 2:
            N = [d.get('id') if d.get('name') == modified_item[1] else -1 for d in Nodes]
            N.sort()
            N = N[-1]
            Meas.append({
                'id': index_meas_id,
                'node': N,
                'line': None,
                'type': modified_item[0],
                'value': data[item] if add_noise == False else data[item] + random.gauss(0, std_data[item]),
                'std': std_data[item]
                })     
            index_meas_id += 1
        # Si se trata de una medida en una línea
        if len(modified_item) == 3:
            for l in Lines:
                if l['From'] == modified_item[1] and l['To'] == modified_item[2]:
                    id_l = l['id']
                    break
                if l['From'] == modified_item[2] and l['To'] == modified_item[1]:
                    id_l = -l['id']
                    break     
            value = data[item]**2 if modified_item[0] == 'I' else data[item]
            if add_noise and modified_item[0] != 'I':
                value += random.gauss(0, std_data[item])            
            if add_noise and modified_item[0] == 'I':
                value += random.gauss(0, 2*std_data[item]*data[item])
            if corrientes == True or (corrientes == False and modified_item[1].startswith('LV') == True):
                Meas.append({
                    'id': index_meas_id,
                    'node': None,
                    'line': id_l,
                    'type': modified_item[0],
                    'value': value,
                    'std': 2*std_data[item]*data[item] if modified_item[0] == 'I' else std_data[item],
                    })
                index_meas_id += 1
            
        
    return Meas, data, std_data
    

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



