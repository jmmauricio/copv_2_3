import json
import matplotlib.pyplot as plt
from pydae import plot_tools

# Set style and get colors
colors = plot_tools.set_style(plt)

# Define the type of measurement
type_of_measurement = 'Q'

# Read the JSON file
file_name = "std_medidas_1ataque.json"
with open(file_name, 'r') as file:
    data = json.load(file)

# Define keys
power_factors = ['090neg', '090pos']
power_factors_labels = ['0.90 (inductive)', '0.90 (capacitive)']
# power_factors = ['090neg', '090pos', '100pos']
times = ['08', '10', '13']
times_labels = ['08 h', '10 h', '13 h']
categories = ['TP', 'TN', 'FP', 'FN']

# Prepare the figure
fig, axes = plt.subplots(2, 3, figsize=(12, 6))
# fig, axes = plt.subplots(3, 3, figsize=(12, 8))

# Loop through each power factor and time to create subplots
for i, pf in enumerate(power_factors):
    for j, time in enumerate(times):
        # Collect data for the current subplot
        boxplot_data = []
        labels = []
        for category in categories:
            values = data[pf][time][type_of_measurement][category]  
            boxplot_data.append(values)
            labels.append(category)
        
        # Create the boxplot with custom colors
        ax = axes[i, j]
        bplot = ax.boxplot(boxplot_data, labels=labels, patch_artist=True, whis=100000)
        
        # Assign colors to the boxplots
        for k, patch in enumerate(bplot['boxes']):
            if labels[k] in ['TP', 'FP']:  # Grey background for TP and FP
                patch.set_facecolor('lightgrey')
            else:  # Use colors from the 'colors' dictionary for TN and FN
                patch.set_facecolor(colors[k % len(colors)])
        
        # Customize medians and means
        for median in bplot['medians']:
            median.set_color('black')  # Median line in black
        for mean in bplot['means']:
            mean.set_markerfacecolor('red')  # Mean marker in red
            mean.set_markeredgecolor('black')

axes[0,0].set_xticks([])
axes[0,1].set_xticks([])

for index in [0, 2]:
    axes[0, 0].axvspan(0.5 + index, 1.5 + index, color='Gray', alpha=0.20) 
    axes[0, 1].axvspan(0.5 + index, 1.5 + index, color='Gray', alpha=0.20) 
    axes[0, 2].axvspan(0.5 + index, 1.5 + index, color='Gray', alpha=0.20)  


for index in [1, 3]:
    axes[1, 0].axvspan(0.5 + index, 1.5 + index, color='Gray', alpha=0.20) 
    axes[1, 1].axvspan(0.5 + index, 1.5 + index, color='Gray', alpha=0.20) 
    axes[1, 2].axvspan(0.5 + index, 1.5 + index, color='Gray', alpha=0.20)       
    
    
axes[0,0].set_title(times_labels[0])
axes[0,1].set_title(times_labels[1])
axes[0,2].set_title(times_labels[2])
axes[0,0].set_ylabel(power_factors_labels[0])
axes[1,0].set_ylabel(power_factors_labels[1])

axes[0,0].set_ylim([0,100])
axes[0,1].set_ylim([0,100])
axes[0,2].set_ylim([0,100])
axes[1,0].set_ylim([0,100])
axes[1,1].set_ylim([0,100])
axes[1,2].set_ylim([0,100])

fig.suptitle('Attacks on ' + type_of_measurement)
    
# Adjust layout and display the plot
plt.tight_layout()  
plt.show()

plt.savefig('figs/1_ataqus_std' + '_' + type_of_measurement + '.pdf')
plt.savefig('figs/1_ataque_std' + '_' + type_of_measurement + '.png')
plt.close()
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    