from lib_timeseries import system_topology, system_measurements, system_constraints
import lib
import numpy as np
import math


# Funciones usadas
def evaluate_lambda_value(ataque, names, Nodes, Lines, Meas, Cons):      
    
    # Se identifica la medida atacada y se modifica su valor artificialmente
    num = names.index(ataque)
    if Meas[num]['type'] == 'Q':
        Meas[num]['value'] = 0.5
    else:        
        Meas[num]['value'] = 1.5*Meas[num]['value']
    
    # Se construye la red y se lanza el estimador de estado (WLS con residuos normalizados)
    net = lib.grid(Nodes, Lines, Meas, Cons)
    Results = net.state_estimation(tol = 1e-4, 
                                   niter = 50, 
                                   Huber = False, 
                                   lmb = None, 
                                   rn = True)    

    
    std_comparative = []
    Q_values = []
    lmb_values = []
    
    # Guardamos la desviación típica de las medidas estimadas
    std_comparative.append(Results['std_sol']) 
    # Calculamos los índices de las medidas descartadas por WLS
    index_pops = [item.ref for item in Results['rm_meas']] 
    index_std = list(set(range(0, len(Meas))) - set(index_pops))
    # Tomamos varios valores de lambda desde el máximo resiudo (antes de quitar ninguna medida) hasta cero (este último no incluido)
    upper_lmb = math.ceil(Results['max_res'] * 100) / 100
    lmb__ = np.linspace(upper_lmb, 0, 4)
    for lmb_value in list(lmb__[:3]):
        print(f'Lambda value: {lmb_value}')
        net.meas = net.add_meas(net.original_meas, net.nodes, net.lines, net.n)
        Results_Huber = net.state_estimation(tol = 1e-4, 
                                            niter = 50, 
                                            Huber = True, 
                                            lmb = lmb_value, 
                                            rn = False)
        # Guardamos la desviación típica de las medidas estimadas (no esta la descartada por WLS)
        std_comparative.append([Results_Huber['std_sol'][index] for index in index_std])
        # Guardamos la diagonal de la matriz Q
        Q_values.append({item[0]: item[1] for item in zip(names, Results_Huber['Q'][-1])})
        lmb_values.append(lmb_value)
    
    return {"std": std_comparative, "Q": Q_values, "lmb": lmb_values, "index": index_std, "pops": index_pops, "Meas": Meas}
    

def plotting_analysis(ataque, dict_res, names):
    
    import json
    import numpy as np
    import matplotlib.pyplot as plt
    from pydae import plot_tools
    
    data = dict_res
    std_solucion = data['std'] 
    Q = data['Q']
    l = data['lmb']
    labels = ['WLS']
    for index, item in enumerate(zip(l, Q)):
        labels.append('$\lambda$ = ' + str(np.round(item[0],2)))
     
    
    # Agrupar índices por prefijo
    groups = {
        'P_': [i for i, name in enumerate(names[:24]) if name.startswith('P_LV')],
        'Q_': [i for i, name in enumerate(names[:24]) if name.startswith('Q_LV')],
        'I_': [i for i, name in enumerate(names[:24]) if name.startswith('I_LV')],
        'U_': [i for i, name in enumerate(names[:24]) if name.startswith('U_LV')]
    }
    
    # Estilo
    col = plot_tools.set_style(plt)
    
    # Crear la figura con 4 subgráficos
    f, ax = plt.subplots(2, 2, figsize=(14, 8))
    bar_width = 0.8/len(std_solucion)
    
    for idx, (key, indices) in enumerate(groups.items()):
        # Se definen sombreados alternos para las columnas
        row = 0 if idx == 0 or idx == 1 else 1
        column = idx if idx < 2 else idx - 2 
        
        x = np.arange(len(indices))  
        x_positions = [x + i * bar_width - 0.3 for i in range(len(std_solucion))]  
    
        for i in range(len(x)):
            if i % 2 != 0:
                ax[row, column].axvspan(i - 0.5, i + 0.5, color='gray', alpha=0.1)
    
        # Se pintan las desviaciones típicas de las medidas estimadas
        max_value = 0
        min_value = 1
        for i, std_vals in enumerate(std_solucion):
            ax[row, column].bar(
                x_positions[i],                      
                [std_vals[item] for item in indices],                  
                width=bar_width,                    
                color=col[i % len(col)],            
                label=labels[i] if idx == 1 else "" 
            )
            if np.max([std_vals[item] for item in indices]) > max_value:
                max_value = np.max([std_vals[item] for item in indices])
            if np.min([std_vals[item] for item in indices]) < min_value:
                min_value = np.min([std_vals[item] for item in indices])
        
        # Etiquetas y formato
        delta = (max_value - min_value)/5
        ax[row, column].set_ylim([min_value - delta, max_value + delta])
        ax[row, column].set_xticks(x)
        ax[row, column].set_xticklabels(['I_' + names[i].split('_')[1] if names[i].startswith('I') else names[i] for i in indices], rotation=0, fontsize=8)
        ax[row, column].set_ylabel('$\sigma$')
    
    ax[0,1].legend(ncol=4)
    plt.tight_layout()
    plt.show()
    plt.close()
    f.savefig('figs/std2_comparative_fig' + ataque + '.pdf')
    






# Se define el conjunto de medidas a las que se va a atacar
ataques = {
    "P_LV0101": 0,
    "P_LV0102": 1,
    "P_LV0103": 2,
    "P_LV0201": 3,
    "P_LV0202": 4,
    "P_LV0203": 5,
    "Q_LV0101": 6,
    "Q_LV0102": 7,
    "Q_LV0103": 8,
    "Q_LV0201": 9,
    "Q_LV0202": 10,
    "Q_LV0203": 11,
    "I_LV0101_MV0101": 12,
    "I_LV0102_MV0102": 13,
    "I_LV0103_MV0103": 14,
    "I_LV0201_MV0201": 15,
    "I_LV0202_MV0202": 16,
    "I_LV0203_MV0203": 17,
}

# Se extrae el conjunto de nodos, líneas y medidas de la red así como las restricciones
extended_path = ['../data/pv_2_3_180_14_45_pf_090neg/', '../data_Cati/pv_2_3_180_14_45_pf_090neg/']
Nodes, Lines = system_topology('../data/pv_2_3.json')
Meas, mjson, stdjson = system_measurements(extended_path, 
                                           'measurements.json', 
                                           'std_2.json', 
                                           Nodes, 
                                           Lines, 
                                           add_noise = True)
Cons = system_constraints(Nodes)

# Nombres de las medidas en orden
names = [m['type'] + '_' + Nodes[m['node']]['name'] if m['line'] == None else m['type'] + '_' + Lines[m['line']]['From'] + '_' + Lines[m['line']]['To'] for m in Meas]

# Para cada ataque definido
for att in ataques:
    print(f'Ataque en {att}')
    dict_res = evaluate_lambda_value(att, names, Nodes, Lines, Meas, Cons)
    plotting_analysis(att, dict_res, names)

    medidas_eliminadas = [item for item in dict_res["Meas"] if item['id'] in dict_res["pops"]]




















