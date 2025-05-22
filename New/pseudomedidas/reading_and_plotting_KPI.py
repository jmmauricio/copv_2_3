import matplotlib.pyplot as plt
import numpy as np
import json
from pydae import plot_tools

# Initial parameters
cosphi = '090pos'
medida = 'I'

colores = plot_tools.set_style(plt)

bandas_array = [{'P': [0.80, 0.05], 'Q': [0.80, 0.05], 'U': [0.980, 0.005], 'I': [0.80, 0.05]},
                {'P': [0.85, 0.05], 'Q': [0.85, 0.05], 'U': [0.985, 0.005], 'I': [0.85, 0.05]},
                {'P': [0.90, 0.05], 'Q': [0.90, 0.05], 'U': [0.990, 0.005], 'I': [0.90, 0.05]},
                {'P': [0.95, 0.05], 'Q': [0.95, 0.05], 'U': [0.995, 0.005], 'I': [0.95, 0.05]},
                {'P': [1.00, 0.05], 'Q': [1.00, 0.05], 'U': [1.000, 0.005], 'I': [1.00, 0.05]},
                {'P': [1.05, 0.05], 'Q': [1.05, 0.05], 'U': [1.005, 0.005], 'I': [1.05, 0.05]},
                {'P': [1.10, 0.05], 'Q': [1.10, 0.05], 'U': [1.010, 0.005], 'I': [1.10, 0.05]},
                {'P': [1.15, 0.05], 'Q': [1.15, 0.05], 'U': [1.015, 0.005], 'I': [1.15, 0.05]}]

data_complete_sinMT_conPSM = dict()
for index_bandas, bandas in enumerate(bandas_array):
    file_name = f'results/inversor_1ataque_sinMT_conPSM_{index_bandas}.json'
    with open(file_name, 'r') as file:
        data = json.load(file)
    data_complete_sinMT_conPSM[str(index_bandas)] = data

data_complete_sinMT = dict()
for index_bandas, bandas in enumerate(bandas_array):
    file_name = f'results/inversor_1ataque_sinMT_{index_bandas}.json'
    with open(file_name, 'r') as file:
        data = json.load(file)
    data_complete_sinMT[str(index_bandas)] = data

data_complete_conMT = dict()
for index_bandas, bandas in enumerate(bandas_array):
    file_name = f'results/inversor_1ataque_conMT_{index_bandas}.json'
    with open(file_name, 'r') as file:
        data = json.load(file)
    data_complete_conMT[str(index_bandas)] = data
    
# Bands (0-7)
bands = list(range(8))  # 0 to 7

# Metrics and categories
metrics = ['Precision', 'Recall', 'F1']
categories = ['08', '10', '13']
x_label = ['80-85%', '85-90%', '90-95%', '95-100%', '100-105%', '105-110%', '110-115%', '115-120%']

# Bar width
bar_width = 0.2

# Create a figure and subplots
fig, axes = plt.subplots(6, 3, figsize=(12, 10))

# Loop through each category (columns: '08', '10', '13')
for col_idx, category in enumerate(categories):
    # Loop through each metric (rows: 'Precision', 'Accuracy', 'Recall')
    for row_idx, metric in enumerate(metrics):
        ax = axes[row_idx, col_idx]
        
        sinMT_values = []
        conMT_values = []
        sinMT_conPSM_values = []
        
        for band_idx in bands:
            band_data_sinMT = data_complete_sinMT[str(band_idx)][cosphi][category]
            band_data_conMT = data_complete_conMT[str(band_idx)][cosphi][category]
            band_data_sinMT_conPSM = data_complete_sinMT_conPSM[str(band_idx)][cosphi][category]
            
            sinMT_values.append(band_data_sinMT[medida][metric]*100)
            conMT_values.append(band_data_conMT[medida][metric]*100)
            sinMT_conPSM_values.append(band_data_sinMT_conPSM[medida][metric]*100)
        
        # X-axis positions for the bars
        x_positions = np.arange(len(bands))
        
        # Plot bars for P, Q, U, I
        ax.bar(x_positions - bar_width, sinMT_values, width=bar_width, label='w/o MT meas.', color=colores[0])
        ax.bar(x_positions, conMT_values, width=bar_width, label='with MT meas.', color=colores[1])
        ax.bar(x_positions + bar_width, sinMT_conPSM_values, width=bar_width, label='with MT psm.', color=colores[2])
        
        # Set axis labels and title
        ax.set_xticks(x_positions)
        ax.set_xticklabels([])
        
        if col_idx == 0:
            if row_idx == 0:
                ax.set_ylabel('Precision (%)')
            if row_idx == 1:
                ax.set_ylabel('Recall (%)')
            if row_idx == 2:
                ax.set_ylabel('F1 (%)')
        
        if row_idx == 0:
            if col_idx == 0:
                ax.set_title('8 h')
            if col_idx == 1:
                ax.set_title('10 h')
            if col_idx == 2:
                ax.set_title('12 h')
                
        # Add legend only once
        if row_idx == 0 and col_idx == 0:
            ax.legend(ncols=1)
        ax.grid(True)
        ax.set_ylim([-2, 102])
        
# KPIs
axes[5,0].set_xticks(x_positions) 
axes[5,1].set_xticks(x_positions) 
axes[5,2].set_xticks(x_positions)        
axes[5,0].set_xticklabels(x_label, rotation=45) 
axes[5,1].set_xticklabels(x_label, rotation=45) 
axes[5,2].set_xticklabels(x_label, rotation=45) 

for col_idx, category in enumerate(categories):
    for row_idx, metric in enumerate(['norm2', 'norminf','z']):
        ax = axes[row_idx+3, col_idx]
        
        if row_idx == 0:            
            ax.set_xticks(x_positions)
            ax.set_xticklabels([])
        
        sinMT_values = []
        conMT_values = []
        sinMT_conPSM_values = []
        
        for band_idx in bands:
            band_data_sinMT = data_complete_sinMT[str(band_idx)][cosphi][category]
            band_data_conMT = data_complete_conMT[str(band_idx)][cosphi][category]
            band_data_sinMT_conPSM = data_complete_sinMT_conPSM[str(band_idx)][cosphi][category]
            
            sinMT_values.append(band_data_sinMT[medida][metric]*100)
            conMT_values.append(band_data_conMT[medida][metric]*100)
            sinMT_conPSM_values.append(band_data_sinMT_conPSM[medida][metric]*100)
           
        x_positions = np.arange(len(bands))
        
        # Plot bars for P, Q, U, I
        ax.bar(x_positions - bar_width, sinMT_values, width=bar_width, label='w/o MT meas.', color=colores[0])
        ax.bar(x_positions, conMT_values, width=bar_width, label='with MT meas.', color=colores[1])
        ax.bar(x_positions + bar_width, sinMT_conPSM_values, width=bar_width, label='with MT psm.', color=colores[2])        
       
        ax.grid(True)
        
        # if row_idx == 0:
        #     ax.set_ylim([0, 0.9])
        # if row_idx == 1:                
        #     ax.set_ylim([0, 0.3])
       
axes[3,0].set_ylabel('$||\,v-\hat{v}\,||_2$')  
axes[4,0].set_ylabel('$||\,v-\hat{v}\,||_{\infty}$')        
axes[5,0].set_ylabel('$|\,z-\hat{z}\,|$')        
       
# Adjust layout and show the plot
fig.align_ylabels(axes)
plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.show()
plt.savefig('figs/bands_inversor_' + cosphi + '_' + medida + '.pdf')
plt.savefig('figs/bands_inversor_' + cosphi + '_' + medida + '.png')
plt.close()



