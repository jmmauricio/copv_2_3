import matplotlib.pyplot as plt
import numpy as np
import json
from pydae import plot_tools

# Initial parameters
cosphi = '090neg'
colores = plot_tools.set_style(plt)

bandas_array = [{'P': [0.80, 0.05], 'Q': [0.80, 0.05], 'U': [0.980, 0.005], 'I': [0.80, 0.05]},
                {'P': [0.85, 0.05], 'Q': [0.85, 0.05], 'U': [0.985, 0.005], 'I': [0.85, 0.05]},
                {'P': [0.90, 0.05], 'Q': [0.90, 0.05], 'U': [0.990, 0.005], 'I': [0.90, 0.05]},
                {'P': [0.95, 0.05], 'Q': [0.95, 0.05], 'U': [0.995, 0.005], 'I': [0.95, 0.05]},
                {'P': [1.00, 0.05], 'Q': [1.00, 0.05], 'U': [1.000, 0.005], 'I': [1.00, 0.05]},
                {'P': [1.05, 0.05], 'Q': [1.05, 0.05], 'U': [1.005, 0.005], 'I': [1.05, 0.05]},
                {'P': [1.10, 0.05], 'Q': [1.10, 0.05], 'U': [1.010, 0.005], 'I': [1.10, 0.05]},
                {'P': [1.15, 0.05], 'Q': [1.15, 0.05], 'U': [1.015, 0.005], 'I': [1.15, 0.05]}]

data_complete = dict()
for index_bandas, bandas in enumerate(bandas_array):
    file_name = f'results/poi_1ataque_sinMT_{index_bandas}.json'
    with open(file_name, 'r') as file:
        data = json.load(file)
    data_complete[str(index_bandas)] = data    
    
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
        
        # Collect values for P, Q, U, I across all bands
        p_values = []
        q_values = []
        u_values = []
        i_values = []
        
        for band_idx in bands:
            band_data = data_complete[str(band_idx)][cosphi][category]
            p_values.append(band_data['P'][metric]*100)
            q_values.append(band_data['Q'][metric]*100)
            u_values.append(band_data['U'][metric]*100)
            i_values.append(band_data['I'][metric]*100)
        
        # X-axis positions for the bars
        x_positions = np.arange(len(bands))
        
        # Plot bars for P, Q, U, I
        ax.bar(x_positions - 3*bar_width/2, p_values, width=bar_width, label='P', color=colores[0])
        ax.bar(x_positions - bar_width/2, q_values, width=bar_width, label='Q', color=colores[1])
        ax.bar(x_positions + bar_width/2, u_values, width=bar_width, label='U', color=colores[2])
        ax.bar(x_positions + 3*bar_width/2, i_values, width=bar_width, label='I', color=colores[3])
        
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
            ax.legend(ncols=4)
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
    for row_idx, metric in enumerate(['norm2', 'norminf', 'z']):
        ax = axes[row_idx+3, col_idx]
        
        if row_idx == 0:            
            ax.set_xticks(x_positions)
            ax.set_xticklabels([])
        
        # Collect values for P, Q, U, I across all bands
        p_values = []
        q_values = []
        u_values = []
        i_values = []
        
        for band_idx in bands:
            band_data = data_complete[str(band_idx)][cosphi][category]
            p_values.append(band_data['P'][metric]*100)
            q_values.append(band_data['Q'][metric]*100)
            u_values.append(band_data['U'][metric]*100)
            i_values.append(band_data['I'][metric]*100)
           
        x_positions = np.arange(len(bands))
        
        # Plot bars for P, Q, U, I
        ax.bar(x_positions - 3*bar_width/2, p_values, width=bar_width, label='P', color=colores[0])
        ax.bar(x_positions - bar_width/2, q_values, width=bar_width, label='Q', color=colores[1])
        ax.bar(x_positions + bar_width/2, u_values, width=bar_width, label='U', color=colores[2])
        ax.bar(x_positions + 3*bar_width/2, i_values, width=bar_width, label='I', color=colores[3]) 
       
        ax.grid(True)
        
        if row_idx == 0:
            ax.set_ylim([0, 1])
        if row_idx == 1:                
            ax.set_ylim([0, 3])
        if row_idx == 2:                
            ax.set_ylim([0, 3])
       
axes[3,0].set_ylabel('$||\,v-\hat{v}\,||_2$ (%)')  
axes[4,0].set_ylabel('$||\,v-\hat{v}\,||_{\infty}$ (%)') 
axes[5,0].set_ylabel('$|\,z-\hat{z}\,|$ (%)')        
       
# Adjust layout and show the plot
fig.align_ylabels(axes)
plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.show()
plt.savefig('figs/bands_poi_' + cosphi + '.pdf')
plt.savefig('figs/bands_poi_' + cosphi + '.png')
plt.close()



