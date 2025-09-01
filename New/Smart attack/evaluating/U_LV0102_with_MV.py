# -*- coding: utf-8 -*-
"""
Created on Tue Jul 22 18:54:48 2025

@author: alvar
"""

import matplotlib.pyplot as plt
import numpy as np
import json
from pydae import plot_tools

plt.rcParams.update({
    'font.size': 11,
    'axes.labelsize': 11,
    'axes.titlesize': 11,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'legend.fontsize': 10,
    'figure.titlesize': 12
})



case_MT = 'with_MT'
file_name = f'results/' + case_MT + '.json'

with open(file_name, 'r') as file:
    data_with_MT = json.load(file)
    
KPIs = ['Precision', 'Recall', 'Accuracy', 'F1', 'z', 'norm2']
KPIs_fancy = ['Precision (%)', 'Recall (%)', 'Accuracy (%)', 'F1 (%)', '$||z-\hat{z}||_2$ (%)', '$||v-\hat{v}||_2$ (%)']
percent_attacked = ['5', '10', '20', '40']
percent_attacked_fancy = ['5 %', '10 %', '20 %', '40 %']
scenarios_U_poi = ['2', '3']
scenarios_P_poi = ['6', '7']
scenarios_Q_poi = ['4', '5']
scenarios_U_inversor = ['0']

colors = ['tab:blue', 'tab:orange']

label_legend = ['$U_{inv} = 0.98·U_{meas}$']

# Create figure and subplots (2 rows x 3 columns)
fig, axes = plt.subplots(2, 3, figsize=(7, 4))

bar_width = 0.5
x_indexes = np.arange(len(percent_attacked))

# Loop over each KPI
for idx, kpi in enumerate(KPIs):
    if idx < 3:
        ax = axes[0, idx]
    else:
        ax = axes[1, idx-3]
            
    for i, scenario in enumerate(scenarios_U_inversor):
        values = [np.mean(data_with_MT[pct][scenario][kpi]) for pct in percent_attacked]
        bar_positions = x_indexes   # shift left and right
        bars = ax.bar(bar_positions, values, width=bar_width, label=f'Scenario {scenario}', color='skyblue')


    ax.set_xticks(x_indexes)
    ax.set_xticklabels(percent_attacked_fancy)

    # Set title and labels
    if idx == 4:
        ax.set_xlabel('Percent Attacked')
    ax.set_ylabel(KPIs_fancy[idx])
    ax.grid(True)


plt.tight_layout()
plt.savefig('figs/especial_fig.pdf')

