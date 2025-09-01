import pandas as pd
import json
import lib
import copy


# max_values = [2933000, 1952000, 2905000, 1972000, 1977000, 1995000]

# Testing
for index in range(1):
    
    df_original = pd.read_excel('Datos_ARN.xlsx')
    
    # Modifiying the date format
    columna_fecha = df_original.columns[0]
    df_original[columna_fecha] = pd.to_datetime(df_original[columna_fecha].str.split('+').str[0], errors='coerce')
    df_original['año'] = df_original[columna_fecha].dt.year
    df_original['mes'] = df_original[columna_fecha].dt.month
    df_original['día'] = df_original[columna_fecha].dt.day
    df_original['hora'] = df_original[columna_fecha].dt.hour
    df_original['minuto'] = df_original[columna_fecha].dt.minute
    
    # Generating a new dataframe with all the information in the correct format
    columnas_restantes = df_original.columns.difference([columna_fecha, 'año', 'mes', 'día', 'hora', 'minuto'])
    df_nuevo = df_original[['año', 'mes', 'día', 'hora', 'minuto'] + list(columnas_restantes)]
    df_nuevo = df_nuevo.rename(columns={
        'ppc,inverter,0,measurement,p' : 'p0', 
        'ppc,inverter,0,measurement,q' : 'q0', 
        'ppc,inverter,1,measurement,p' : 'p1',   
        'ppc,inverter,1,measurement,q' : 'q1', 
        'ppc,inverter,2,measurement,p' : 'p2',  
        'ppc,inverter,2,measurement,q' : 'q2', 
        'ppc,inverter,3,measurement,p' : 'p3',   
        'ppc,inverter,3,measurement,q' : 'q3', 
        'ppc,inverter,4,measurement,p' : 'p4',   
        'ppc,inverter,4,measurement,q' : 'q4', 
        'ppc,inverter,5,measurement,p' : 'p5',   
        'ppc,inverter,5,measurement,q' : 'q5'
    })
    
    
    # Opening an example of the structure for the measurements
    with open('measurements.json', 'r') as fp:
        meas = json.load(fp)
    
        
    relation = {'p0': 'P_LV0101', 'q0': 'Q_LV0101',
                'p1': 'P_LV0102', 'q1': 'Q_LV0102',
                'p2': 'P_LV0103', 'q2': 'Q_LV0103',
                'p3': 'P_LV0201', 'q3': 'Q_LV0201',
                'p4': 'P_LV0202', 'q4': 'Q_LV0202',
                'p5': 'P_LV0203', 'q5': 'Q_LV0203'}

    max_valu = {'p0': 2933000, 'q0': 2933000,
                'p1': 2933000, 'q1': 2933000,
                'p2': 2933000, 'q2': 2933000,
                'p3': 2933000, 'q3': 2933000,
                'p4': 2933000, 'q4': 2933000,
                'p5': 2933000, 'q5': 2933000}
    
    
    row = df_nuevo.loc[index]
    año = row.año
    mes = row.mes
    dia = row.día
    hora = row.hora
    minuto = row.minuto
    
    meas['U_POI'] = 1
    for item in relation:
        # meas[relation[item]] = row[item]/2933000
        meas[relation[item]] = (row[item]/max_valu[item])*(3/10)
    meas_original = copy.deepcopy(meas)
    # Removing data not available
    delete = [k for k in meas if (k.startswith('U_') or k.startswith('I_') or k.startswith('P_P') or k.startswith('Q_P')) and k != 'U_POI']
    for key in delete:
        del meas[key]
        
    with open('meas.json', 'w', encoding='utf-8') as f:
        json.dump(meas, f, ensure_ascii=False, indent=2)
    
    net = lib.grid(path_topology='pv_2_3.json', 
                   path_measurements='meas.json')   
    
    
    solution = net.state_estimation(tol = 1e-4, 
                                    niter = 50, 
                                    Huber = False, 
                                    lmb = 2.5, 
                                    rn = False) 
    
    for m in net.meas:
        print(f'{m.tipo}-{m.node_name}')
    
    for m in meas_original:
        if m.startswith('U_'):
            node_name = m.split('_')[1]
            index_node = [node.name for node in net.nodes].index(node_name)
            meas_original[m] = net.nodes[index_node].V    
        if m.startswith('I_L'):
            node_name = m.split('_')[1]
            index_node = [node.name for node in net.nodes].index(node_name)
            meas_original[m] = net.nodes[index_node].I
            
    meas_original['P_POIMV_MV0101'] = net.lines[2].Pji     
    meas_original['Q_POIMV_MV0101'] = net.lines[2].Qji     
    meas_original['I_POIMV_MV0101'] = net.lines[2].I
    meas_original['P_POIMV_MV0201'] = net.lines[8].Pji     
    meas_original['Q_POIMV_MV0201'] = net.lines[8].Qji     
    meas_original['I_POIMV_MV0201'] = net.lines[8].I
    meas_original['P_POI_POIMV'] = net.lines[13].Pji     
    meas_original['Q_POI_POIMV'] = net.lines[13].Qji     
    meas_original['I_POI_POIMV'] = net.lines[13].I       
       
    with open(f'scenarios/{año}_{mes}_{dia}_{hora}_{minuto}.json', 'w', encoding='utf-8') as f:
        json.dump(meas_original, f, ensure_ascii=False, indent=2)     
    
    
    # Checking
    net = lib.grid(path_topology='pv_2_3.json', 
                   path_measurements=f'scenarios/{año}_{mes}_{dia}_{hora}_{minuto}.json')   
    
    # for m in net.meas:
    #     print(f'{m.tipo}-{m.node_name}-{m.std}')
        # print(m.std)
    
    solution = net.state_estimation(tol = 1e-4, 
                                    niter = 50, 
                                    Huber = False, 
                                    lmb = 2.5, 
                                    rn = False) 
    net.report()
    
    
    
















