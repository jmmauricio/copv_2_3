import matplotlib.pyplot as plt
import numpy as np
import json
from pydae import plot_tools

# Initial parameters
cosphi = '090pos'
hora = '13'
n = '5'

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
    file_name = f'results/sinMT_conPSM_banda{index_bandas}.json'
    with open(file_name, 'r') as file:
        data = json.load(file)
    data_complete_sinMT_conPSM[str(index_bandas)] = data

data_complete_sinMT = dict()
for index_bandas, bandas in enumerate(bandas_array):
    file_name = f'results/sinMT_banda{index_bandas}.json'
    with open(file_name, 'r') as file:
        data = json.load(file)
    data_complete_sinMT[str(index_bandas)] = data

data_complete_conMT = dict()
for index_bandas, bandas in enumerate(bandas_array):
    file_name = f'results/conMT_banda{index_bandas}.json'
    with open(file_name, 'r') as file:
        data = json.load(file)
    data_complete_conMT[str(index_bandas)] = data
    
# ['090neg', '090pos'] / ['08', '10', '13'] / range(2, 11) / ['Precision', 'Accuracy', 'Recall', 'F1', 'norm2', 'norminf', 'z']   
    
    
# Bands (0-7)
bands = list(range(8))  # 0 to 7

# Metrics and categories
metrics = ['Precision', 'Recall', 'F1']
categories = ['08', '10', '13']
x_label = ['80-85%', '85-90%', '90-95%', '95-100%', '100-105%', '105-110%', '110-115%', '115-120%']

# Bar width
bar_width = 0.2

# Create a figure and subplots
fig, axes = plt.subplots(2, 3, figsize=(14, 8))

# Loop through each category (columns: '08', '10', '13')
for col_idx, metric in enumerate(metrics):
    ax = axes[0, col_idx]
    
    sinMT_values = []
    conMT_values = []
    sinMT_conPSM_values = []
    
    for band_idx in bands:
        band_data_sinMT = data_complete_sinMT[str(band_idx)][cosphi]['13']['2'][metric]*100
        band_data_conMT = data_complete_conMT[str(band_idx)][cosphi]['13']['2'][metric]*100
        band_data_sinMT_conPSM = data_complete_sinMT_conPSM[str(band_idx)][cosphi]['13']['2'][metric]*100
        
        sinMT_values.append(band_data_sinMT)
        conMT_values.append(band_data_conMT)
        sinMT_conPSM_values.append(band_data_sinMT_conPSM)
    
    # X-axis positions for the bars
    x_positions = np.arange(len(bands))
    
    # Plot bars for P, Q, U, I
    ax.bar(x_positions - bar_width, sinMT_values, width=bar_width, label='w/o MT meas.', color=colores[0])
    ax.bar(x_positions, conMT_values, width=bar_width, label='with MT meas.', color=colores[1])
    ax.bar(x_positions + bar_width, sinMT_conPSM_values, width=bar_width, label='with MT psm.', color=colores[2])
    
    # Set axis labels and title
    ax.set_xticks(x_positions)
    ax.set_xticklabels([])
    ax.grid(True)
    ax.set_ylim([-2, 102])
    
    ax.set_ylabel(metric + ' (%)')   
        



for row_idx, metric in enumerate(['norm2', 'norminf','z']):
    ax = axes[1, row_idx]
            
    sinMT_values = []
    conMT_values = []
    sinMT_conPSM_values = []
    
    for band_idx in bands:
        band_data_sinMT = data_complete_sinMT[str(band_idx)][cosphi][hora][n][metric]*100
        band_data_conMT = data_complete_conMT[str(band_idx)][cosphi][hora][n][metric]*100
        band_data_sinMT_conPSM = data_complete_sinMT_conPSM[str(band_idx)][cosphi][hora][n][metric]*100
        
        sinMT_values.append(band_data_sinMT)
        conMT_values.append(band_data_conMT)
        sinMT_conPSM_values.append(band_data_sinMT_conPSM)
       
    x_positions = np.arange(len(bands))
    
    # Plot bars for P, Q, U, I
    ax.bar(x_positions - bar_width, sinMT_values, width=bar_width, label='w/o MT meas.', color=colores[0])
    ax.bar(x_positions, conMT_values, width=bar_width, label='with MT meas.', color=colores[1])
    ax.bar(x_positions + bar_width, sinMT_conPSM_values, width=bar_width, label='with MT psm.', color=colores[2])        
   
    ax.set_xticks(x_positions)
    ax.set_xticklabels([])
    ax.grid(True)

val = np.ceil(max(sinMT_values)*10)/10
axes[1,0].set_ylim([0, val]) 
axes[1,1].set_ylim([0, val]) 
axes[1,2].set_ylim([0, val])   
axes[1,0].legend()
       
axes[1,0].set_ylabel('$||\,v-\hat{v}\,||_2 (\%)$')  
axes[1,1].set_ylabel('$||\,v-\hat{v}\,||_{\infty} (\%)$')        
axes[1,2].set_ylabel('$||\,z-\hat{z}\,||_2 (\%)$')        
       
axes[1,0].set_xticks(x_positions) 
axes[1,1].set_xticks(x_positions) 
axes[1,2].set_xticks(x_positions)        
axes[1,0].set_xticklabels(x_label, rotation=45) 
axes[1,1].set_xticklabels(x_label, rotation=45) 
axes[1,2].set_xticklabels(x_label, rotation=45) 

# Adjust layout and show the plot
fig.align_ylabels(axes)
plt.tight_layout()
plt.show()
plt.savefig('figs/bands_' + cosphi + '_' + hora + '_' + n + '.pdf')
plt.savefig('figs/bands_' + cosphi + '_' + hora + '_' + n + '.png')
plt.close()