import numpy as np
import json
import matplotlib.pyplot as plt
from pydae import plot_tools
from lib_timeseries import system_topology, system_measurements



tipo = 'U'
file_name = 'data_simus_ts_2ataques.json'

# Leemos el json de resultados
with open(file_name,'r') as file:
    data = json.load(file)     
    


P_gen = list() 

minute = '00'
path = ['../data_Cati2/pv_2_3_180_', '../data_Cati2/pv_2_3_180_']
for c in ['090neg']:        
    for hour in ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23']:        
            
        sheet_name = hour + '_' + minute + '_pf_' + c
        extended_path = [path[0] + hour + '_' + minute + '_pf_' + c + '/',
                         path[1] + hour + '_' + minute + '_pf_' + c + '/']

        Nodes, Lines = system_topology('../data/pv_2_3.json')
        Meas, mjson, stdjson = system_measurements(extended_path, 
                                                   'measurements.json', 
                                                   'std_2.json', 
                                                   Nodes, 
                                                   Lines, 
                                                   add_noise = False)
        P_gen.append(Meas[0]['value'])



# Leemos el json de resultados
with open(file_name,'r') as file:
    data = json.load(file)     
    
# '090neg', '090pos', '100pos'
# '08', '09', '10', '11', '12', '13', '14'
# 'P', 'Q', 'U'

# Recordamos los valores de lambda considerados
num_lmb = 100
lmb_range = np.linspace(0.01, 50, num_lmb)

fig, axs = plt.subplots(4, 2, figsize=(12,8))
plt.subplots_adjust(wspace=0.1) 
        
axs[0,0].stackplot(
    list(range(1,24)), 
    P_gen, 
    alpha=0.7
)
axs[0,0].grid(True)
for it in range(8, 15):
    axs[0,0].plot([it, it],[0,0.35], 'k-.', alpha=0.5)
axs[0,0].set_ylim([0.0, 0.4])

labels_time = ['8h', '9h', '10h', '11h', '12h', '13h', '14h']

# Generamos los ataques para cada variable
for c in ['090neg']:
    i, j = 0, 0
    for hour in ['08', '09', '10', '11', '12', '13', '14']:
        i += 1       
        if i > 3:
            j +=1
            i = 0
        
        # Compartir eje y en las 3 últimas filas
        if i > 0:
            axs[i, j].sharey = axs[1, j]        
        
        # Eliminar etiquetas de números en el eje x
        if j == 1 and i > 0:
            axs[i, j].set_yticklabels([])
            
        # Compartir eje x en la segunda columna
        if j == 1:
            axs[i, j].sharex = axs[3, j]
        
        # Compartir eje x en la primera columna excepto la primera fila
        if j == 0 and i > 0:
            axs[i, j].sharex = axs[3, j]
        
        # Eliminar etiquetas de números en el eje x
        if i < 3:
            axs[i, j].set_xticklabels([])
        
        # Etiquetas solo en la última fila
        if i == 3:
            axs[i, j].set_xlabel(r'$\lambda$')
            
        x_values = [str(item) for item in np.linspace(0.01, 50, 100)]
        
        
        # Definimos los colores del plot
        colors = plot_tools.set_style(plt)
        colors.pop(3)
        
        # Establecemos las etiquetas
        if len(data[c][hour][x_values[0]][tipo].values()) == 4:
            labels = ['Detection', 'Detection and others', 'Incorrect detection', 'No detection']
        else:
            labels = ['Detection', 'Detection and others', 'Partial detection', 'Partial detection and others', 'No detection', 'Incorrect detection']        
        
        
        
        # Inicializamos figura
        counts = []
        
        for x in x_values:
            values = list(np.array(list(data[c][hour][x][tipo].values()))/10)
            counts.append(values)
    
        counts = np.array(counts).T  # Transponer para separar por 0, 1, 2, 3
    
        axs[i,j].stackplot(
            lmb_range, 
            counts, 
            labels=labels,
            colors=colors,
            alpha=0.7
        )
    
    
        if j > 0:
            axs[i, j].yaxis.set_label_position('right')
            
        if i != 0 or j != 0:
            axs[i,j].set_ylabel(labels_time[j*4+i-1])
            axs[i,j].set_xlim([0,50])
            axs[i,j].set_ylim([0,100])
        axs[i,j].grid(True)
    
    
lines = axs[0, 1].collections

if len(labels) == 6:
    legend=fig.legend(lines, labels, loc='upper center', ncol=3, bbox_to_anchor=(0.688, 0.96))
    legend_edge_color = legend.get_frame().get_edgecolor()
    fig.text(0.18, 0.901, 'Double attack - ' + tipo, fontsize=12,
             bbox=dict(facecolor='white', edgecolor=legend_edge_color, boxstyle='round,pad=0.3'))
else:
    legend=fig.legend(lines, labels, loc='upper center', ncol=4, bbox_to_anchor=(0.674, 0.93))   
    legend_edge_color = legend.get_frame().get_edgecolor() 
    fig.text(0.18, 0.901, 'Single attack - ' + tipo, fontsize=12,
             bbox=dict(facecolor='white', edgecolor=legend_edge_color, boxstyle='round,pad=0.3'))

# fig.text(0.18, 0.901, 'Single attack - ' + tipo, fontsize=12)


plt.savefig('figs/'+ file_name.split('.')[0] + '_' + tipo + '.pdf')