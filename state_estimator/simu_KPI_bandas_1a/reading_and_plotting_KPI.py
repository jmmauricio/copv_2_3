import numpy as np
import json
import matplotlib.pyplot as plt
from pydae import plot_tools
from lib_timeseries import system_topology, system_measurements
import matplotlib.gridspec as gridspec

fp_list = ['090neg', '090pos', '100pos']
tipo = 'U'
bandas_array = [{'P': [0.80, 0.05], 'Q': [0.80, 0.05], 'U': [0.980, 0.005]},
                {'P': [0.85, 0.05], 'Q': [0.85, 0.05], 'U': [0.985, 0.005]},
                {'P': [0.90, 0.05], 'Q': [0.90, 0.05], 'U': [0.990, 0.005]},
                {'P': [0.95, 0.05], 'Q': [0.95, 0.05], 'U': [0.995, 0.005]},
                {'P': [1.00, 0.05], 'Q': [1.00, 0.05], 'U': [1.000, 0.005]},
                {'P': [1.05, 0.05], 'Q': [1.05, 0.05], 'U': [1.005, 0.005]},
                {'P': [1.10, 0.05], 'Q': [1.10, 0.05], 'U': [1.010, 0.005]},
                {'P': [1.15, 0.05], 'Q': [1.15, 0.05], 'U': [1.015, 0.005]}]
colores = ["#007bff",  # Azul brillante
                             "#d63384",  # Rosa fuerte
                             "#28a745",  # Verde intenso
                             "#dc3545",  # Rojo vibrante
                             "#fd7e14",  # Naranja llamativo
                             "#ffc107",  # Amarillo oscuro
                             "#6610f2",  # Morado fuerte
                             "#17a2b8"]
P_gen = list() 
minute = '00'
path = ['../../data_Cati2/pv_2_3_180_', '../../data_Cati2/pv_2_3_180_']
c = '100pos'
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

for c in fp_list:

    fig = plt.figure(figsize=(12, 8))
    gs = gridspec.GridSpec(4, 3, height_ratios=[1.2, 1, 1, 1])  # Primera fila más alta 
    plt.subplots_adjust(wspace=0.1, hspace=0.3)    
    ax = fig.add_subplot(gs[0, :])
    ax_pos = ax.get_position()
    ax.set_position([ax_pos.x0, ax_pos.y0 + 0.08, ax_pos.width, ax_pos.height * (1 / 1.5)])
    axes = np.empty((3, 3), dtype=object)  
    for i in range(3): 
        for j in range(3):  
            axes[i, j] = fig.add_subplot(gs[i+1, j]) 
    ax.stackplot(
        list(range(1, 24)), 
        P_gen, 
        alpha=0.7
    )
    ax.grid(True)
    for it in [8, 10, 13]:
        ax.plot([it, it], [0, 0.35], 'k-.', alpha=0.5)
    ax.set_ylim([0.0, 0.4])
    ax.set_xlim([0.0, 23])






    for index_hour, hour in enumerate(['08', '10', '13']):
        for index_bandas, bandas in enumerate(bandas_array):  
        
            file_name = 'data_simus_ts_banda_' + str(index_bandas) + '_1ataque_KPI.json'
            fp_list = ['090neg']          
            
            # Leemos el json de resultados
            with open(file_name,'r') as file:
                data = json.load(file)     
            
            # Recordamos los valores de lambda considerados
            num_lmb = 20
            lmb_range = np.linspace(0.01, 10, num_lmb)
        
            labels_time = ['8h', '10h', '13h']
                        
            x_values = [str(item) for item in np.linspace(0.01, 10, num_lmb)]
            colors = plot_tools.set_style(plt)
            
           
            kpis = []            
            for x in x_values:              
                values = list(np.array(list([data[c][hour][x][tipo][k] for k in ['Precision', 'Accuracy', 'Recall'] ])))
                kpis.append(values)  
                
            axes[index_hour, 0].plot(lmb_range, [item[0]*100 for item in kpis], color=colores[index_bandas], label='avg precision')
            axes[index_hour, 1].plot(lmb_range, [item[1]*100 for item in kpis], color=colores[index_bandas], label='avg accuracy')
            axes[index_hour, 2].plot(lmb_range, [item[2]*100 for item in kpis], color=colores[index_bandas], label='avg recall')
            
        

    axes[0,0].sharex = axes[2,0]
    axes[1,0].sharex = axes[2,0]
    axes[2,0].set_xlim([0,10])
    axes[0,1].sharex = axes[2,1]
    axes[1,1].sharex = axes[2,1]
    axes[2,1].set_xlim([0,10])
    axes[0,2].sharex = axes[2,2]
    axes[1,2].sharex = axes[2,2]
    axes[2,2].set_xlim([0,10])
    
    axes[0,1].sharey = axes[0,0]
    axes[0,2].sharex = axes[0,0]
    axes[1,1].sharey = axes[1,0]
    axes[1,2].sharex = axes[1,0]
    axes[2,1].sharey = axes[2,0]
    axes[2,2].sharex = axes[2,0]
    
    for i in range(3):
        for j in range(3):
            axes[i, j].grid(True)
                  
    axes[0,0].set_yticks([0,25,50,75,100])
    axes[0,0].set_xticklabels([])
    axes[0,1].set_xticklabels([])
    axes[0,2].set_xticklabels([])
    axes[1,0].set_xticklabels([])
    axes[1,1].set_xticklabels([])
    axes[1,2].set_xticklabels([])
    
    axes[0,1].set_yticklabels([])
    axes[0,2].set_yticklabels([])
    axes[1,1].set_yticklabels([])
    axes[1,2].set_yticklabels([])
    axes[2,1].set_yticklabels([])
    axes[2,2].set_yticklabels([])
    
    axes[2,0].set_xlabel(r'$\lambda$')
    axes[2,1].set_xlabel(r'$\lambda$')
    axes[2,2].set_xlabel(r'$\lambda$')
    
    axes[0,0].set_ylabel(labels_time[0])
    axes[1,0].set_ylabel(labels_time[1])
    axes[2,0].set_ylabel(labels_time[2])
    
    
    
    
    # Mover la leyenda principal a 2 columnas y colocarla en posición (1, 0)
    lines = axes[0, 0].lines     
    if tipo == 'U':
        labels = ['98-98.5%', '98.5-99%', '99-99.5%', '99.5-100%', '100-100.5%', '100.5-101%', '101-101.5%', '101.5-102%']
    else:
        labels = ['80-85%', '85-90%', '90-95%', '95-100%', '100-105%', '105-110%', '110-115%', '115-120%']
    legend = fig.legend(lines, labels, loc='upper center', ncol=8, bbox_to_anchor=(0.51, 0.7))
    legend_edge_color = legend.get_frame().get_edgecolor() 
    
    column_titles = ['avg precision', 'avg accuracy', 'avg recall']
    for i, title in enumerate(column_titles):
        fig.text(0.22 + i * 0.27, 0.70, title, fontsize=12, ha='center')
    fig.text(0.5, 0.92, 'Single attack - ' + tipo, fontsize=12, ha='center',
             bbox=dict(facecolor='white', edgecolor=legend_edge_color, boxstyle='round,pad=0.3'))        
    ax.set_xlabel("time (h)")    
    
    plt.savefig('figs/1_ataque_bandas' + '_' + tipo + '_' + c + '.pdf')
    plt.savefig('figs/1_ataque_bandas' + '_' + tipo + '_' + c + '.png')
    plt.close()














