import numpy as np
import json
import matplotlib.pyplot as plt
from pydae import plot_tools
from lib_timeseries import system_topology, system_measurements
import matplotlib.gridspec as gridspec


tipo = 'Q'
file_name = 'data_simus_ts_1ataque_KPI.json'
fp_list = ['090neg', '090pos', '100pos']


# Leemos el json de resultados
with open(file_name,'r') as file:
    data = json.load(file)     
    


P_gen = list() 

minute = '00'
path = ['../../data_Cati2/pv_2_3_180_', '../../data_Cati2/pv_2_3_180_']
for c in ['090neg']:        
    for hour in ['01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', '23']:        
            
        sheet_name = hour + '_' + minute + '_pf_' + c
        extended_path = [path[0] + hour + '_' + minute + '_pf_' + c + '/',
                         path[1] + hour + '_' + minute + '_pf_' + c + '/']

        Nodes, Lines = system_topology('../../data/pv_2_3.json')
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
num_lmb = 20
lmb_range = np.linspace(0.01, 10, num_lmb)



# Generamos los ataques para cada variable
for c in fp_list:
    fig = plt.figure(figsize=(12, 8))
    gs = gridspec.GridSpec(4, 2, height_ratios=[1.5, 1, 1, 1])  # Primera fila más alta
    plt.subplots_adjust(wspace=0.1, hspace=0.3)
            
    ax = fig.add_subplot(gs[0, :])
    ax_pos = ax.get_position()
    ax.set_position([ax_pos.x0, ax_pos.y0 + 0.09, ax_pos.width, ax_pos.height * (1 / 1.5)])

    axs = np.empty((4, 2), dtype=object)  # Creamos una matriz vacía de objetos

    for i in range(3):
        for j in range(2):
            axs[i, j] = fig.add_subplot(gs[i+1, j]) 


    ax.stackplot(
        list(range(1,24)), 
        P_gen, 
        alpha=0.7
    )
    ax.grid(True)
    for it in [8,10,13]:
        ax.plot([it, it],[0,0.35], 'k-.', alpha=0.5)
    ax.set_ylim([0.0, 0.4])
    ax.set_xlim([0.0, 23])

    labels_time = ['8h', '10h', '13h']
    i, j = -1, 0
    for hour in ['08', '10', '13']:
        i += 1       
        if i > 3:
            j +=1
            i = 0
                      
        # Compartir ejes entre columnas
        axs[i, j+1].sharey(axs[i, j])

        # Eliminar ticks de la columna derecha
        axs[i, 1].set_yticks([0,25,50,75,100])
                      
                    
        # Compartir eje x en la segunda columna
        if j == 1:
            axs[i, j].sharex = axs[3, j]
        
        # Compartir eje x en la primera columna excepto la primera fila
        if j == 0 and i > -1:
            axs[i, j].sharex = axs[3, j]
        
        # Eliminar etiquetas de números en el eje x
        if i < 2:
            axs[i, j].set_xticklabels([])
        
        # Etiquetas solo en la última fila
        if i == 2:
            axs[i, j].set_xlabel(r'$\lambda$')
            axs[i, j+1].set_xlabel(r'$\lambda$')
            
        x_values = [str(item) for item in np.linspace(0.01, 10, num_lmb)]
        
        
        # Definimos los colores del plot
        colors = plot_tools.set_style(plt)
        # colors.pop(3)
        
        # Establecemos las etiquetas
        labels = ['Detection', 'Detection and others', 'Incorrect detection', 'No detection']
               
        
    
        
        # Inicializamos figura
        counts = []
        kpis = []
        
        for x in x_values:            
            values = list(np.array(list([data[c][hour][x][tipo][k] for k in ['0', '1', '2', '3'] if k in data[c][hour][x][tipo]]))/10)
            counts.append(values)        
            values = list(np.array(list([data[c][hour][x][tipo][k] for k in ['Precision', 'Accuracy', 'Recall'] ])))            
            kpis.append(values)            
            

    
        counts = np.array(counts).T  # Transponer para separar por 0, 1, 2, 3
    
        axs[i,j].stackplot(
            lmb_range, 
            counts, 
            labels=labels,
            colors=colors,
            alpha=0.7
        )
        
        axs[i,j+1].plot(lmb_range, [item[0]*100 for item in kpis], 'b', label='avg precision')
        axs[i,j+1].plot(lmb_range, [item[1]*100 for item in kpis], 'r', label='avg accuracy')
        axs[i,j+1].plot(lmb_range, [item[2]*100 for item in kpis], 'k', label='avg recall')
        axs[i,j+1].plot(lmb_range, [200*item[0]*item[2]/(item[0] + item[2]) for item in kpis], 'g', label='avg F1')
    
    
            
        
        axs[i,j].set_ylabel(labels_time[i])
        axs[i,j].set_xlim([0,10])
        axs[i,j+1].set_xlim([0,10])
        # axs[i,j].set_ylim([0,103])
        axs[i,j].grid(True)
        axs[i,j+1].grid(True)
    
    lines = axs[1, 0].collections      
        
        
    # Debajo del subplot de la primera fila, añadir el label "time (h)"
    ax.set_xlabel("time (h)")
    
    # Mover la leyenda principal a 2 columnas y colocarla en posición (1, 0)
    legend = fig.legend(lines, labels, loc='upper center', ncol=2, bbox_to_anchor=(0.255, 0.7))
    legend_edge_color = legend.get_frame().get_edgecolor() 
    
    # Centrar el texto "Single attack - X" arriba del plot
    fig.text(0.5, 0.92, 'Single attack - ' + tipo, fontsize=12, ha='center',
             bbox=dict(facecolor='white', edgecolor=legend_edge_color, boxstyle='round,pad=0.3'))
    
    
    # Nueva leyenda encima del subplot en posición (1,1) para las métricas de precisión, recall y accuracy
    lines = axs[1, 1].lines   
    legend_metrics = fig.legend(lines, ['avg precision', 'avg accuracy', 'avg recall', 'avg F1'], 
                                loc='upper center', ncol=4, bbox_to_anchor=(0.715, 0.68))
    
    plt.savefig('figs/'+ file_name.split('.')[0] + '_' + tipo + '_' + c + '_kpi.pdf')
    plt.savefig('figs/'+ file_name.split('.')[0] + '_' + tipo + '_' + c + '_kpi.png')
    plt.close()