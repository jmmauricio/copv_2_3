from pylatex import Document, Section, Figure, NewPage
from pylatex.utils import NoEscape
from plotting_lmb_tunning import plotting_analysis
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
        std_comparative.append([Results_Huber['std_sol'][index] for index in index_std])
        Q_values.append(float(np.diag(net.Q)[num]))
        lmb_values.append(lmb_value)
    
    return {"std": list(std_comparative), "Q": Q_values, "lmb": lmb_values, "index": index_std, "pops": index_pops, "Meas": Meas}
    






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

# Creación del documento de Latex
geometry_options = {
    "margin": "1cm"  
}
doc = Document(geometry_options=geometry_options)
with doc.create(Section('Red')):
    doc.append('A continuación se presenta un esquemático de la red objeto de estudio. En este caso particular se consideran dos alimentadores. Cada uno de ellos cuenta con tres generadores.')    
    with doc.create(Figure(position="h!")) as figure:
        figure.add_image("figs/pv_m_n_bess.png", width=NoEscape(r"1\textwidth"))
        figure.add_caption("Esquemático de la red.")        
doc.append(NewPage())

# Para cada ataque definido
for att in ataques:
    print(att)
    dict_res = evaluate_lambda_value(att, names, Nodes, Lines, Meas, Cons)
    plotting_analysis(att, dict_res, names)

    with doc.create(Section('Ataque en ' + att)):
        medidas_eliminadas = [item for item in dict_res["Meas"] if item['id'] in dict_res["pops"]]
        if att.startswith('Q_'):
            doc.append('Se ataca el valor de ' + att + ' cambiandolo por un valor de 0.5. \n WLS descarta ' + str([names[item['id']] for item in medidas_eliminadas]))    
        else:
            doc.append('Se ataca el valor de ' + att + ' multiplicando su medida por 1.5. \n WLS descarta ' + str([names[item['id']] for item in medidas_eliminadas]))    
        
        with doc.create(Figure(position="h!")) as figure:
            figure.add_image('figs/std2_comparative_fig' + att + '.pdf', width=NoEscape(r"0.9\textwidth"))
            figure.add_caption("Comparativa entre las desviaciones típicas de las soluciones para WLS y Huber (con diferentes valores de lambda). Magnitudes medidas en baja tensión.")
            
        if att.startswith('I_') == False:
            with doc.create(Figure(position="h!")) as figure:
                figure.add_image('figs/std2_comparative_fig_MV' + att + '.pdf', width=NoEscape(r"0.9\textwidth"))
                figure.add_caption("Comparativa entre las desviaciones típicas de las soluciones para WLS y Huber (con diferentes valores de lambda). Magnitudes medidas en media tensión.")

    
        doc.append(NewPage())
        
doc.generate_pdf('resumen_estimador', compiler='pdflatex', clean_tex=True)



















