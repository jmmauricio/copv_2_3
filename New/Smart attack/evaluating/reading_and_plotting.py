import matplotlib.pyplot as plt
import numpy as np
import json
from pydae import plot_tools

for case_MT in ['with_MT', 'with_PSM', 'wo_MT']:
    file_name = f'results/' + case_MT + '.json'
    with open(file_name, 'r') as file:
        data_with_MT = json.load(file)
        
    KPIs = ['Precision', 'Recall', 'Accuracy', 'F1', 'z', 'norm2']
    KPIs_fancy = ['Precision (%)', 'Recall (%)', 'Accuracy (%)', 'F1 (%)', 'z (%)', '$||r||_2$ (%)']
    percent_attacked = ['5', '10', '20', '40']
    percent_attacked_fancy = ['5 %', '10 %', '20 %', '40 %']
    scenarios_U_poi = ['2', '3']
    scenarios_P_poi = ['6', '7']
    scenarios_Q_poi = ['4', '5']
    scenarios_U_inversor = ['0']
    
    colors = ['tab:blue', 'tab:orange']
    
    label_legend = ['$U_{poi} = 0.98·U_{meas}$', '$U_{poi} = 1.02·U_{meas}$']
    
    # Create figure and subplots (2 rows x 3 columns)
    fig, axes = plt.subplots(2, 3, figsize=(16, 8))
    
    bar_width = 0.35
    x_indexes = np.arange(len(percent_attacked))
    
    # Loop over each KPI
    for idx, kpi in enumerate(KPIs):
        if idx < 3:
            ax = axes[0, idx]
        else:
            ax = axes[1, idx-3]
                
        for i, scenario in enumerate(scenarios_U_poi):
            values = [np.mean(data_with_MT[pct][scenario][kpi]) for pct in percent_attacked]
            bar_positions = x_indexes + (i - 0.5) * bar_width  # shift left and right
            bars = ax.bar(bar_positions, values, width=bar_width, label=f'Scenario {scenario}', color=colors[i])
    
    
        ax.set_xticks(x_indexes)
        ax.set_xticklabels(percent_attacked_fancy)
    
        # Set title and labels
        if idx == 4:
            ax.set_xlabel('Percent Attacked')
        ax.set_ylabel(KPIs_fancy[idx])
        ax.grid(True)
    
    axes[1,1].legend(label_legend)
    
    plt.tight_layout()
    plt.savefig('figs/U_poi_' + case_MT + '.pdf')
    plt.close()



for case_MT in ['with_MT', 'with_PSM', 'wo_MT']:
    file_name = f'results/' + case_MT + '.json'
    with open(file_name, 'r') as file:
        data_with_MT = json.load(file)
        
    KPIs = ['Precision', 'Recall', 'Accuracy', 'F1', 'z', 'norm2']
    KPIs_fancy = ['Precision (%)', 'Recall (%)', 'Accuracy (%)', 'F1 (%)', 'z (%)', '$||r||_2$ (%)']
    percent_attacked = ['5', '10', '20', '40']
    percent_attacked_fancy = ['5 %', '10 %', '20 %', '40 %']
    scenarios_U_poi = ['2', '3']
    scenarios_P_poi = ['6', '7']
    scenarios_Q_poi = ['4', '5']
    scenarios_U_inversor = ['0']
    
    colors = ['tab:blue', 'tab:orange']
    
    label_legend = ['$P_{poi} = 0.8·P_{meas}$', '$P_{poi} = 1.2·P_{meas}$']
    
    # Create figure and subplots (2 rows x 3 columns)
    fig, axes = plt.subplots(2, 3, figsize=(16, 8))
    
    bar_width = 0.35
    x_indexes = np.arange(len(percent_attacked))
    
    # Loop over each KPI
    for idx, kpi in enumerate(KPIs):
        if idx < 3:
            ax = axes[0, idx]
        else:
            ax = axes[1, idx-3]
                
        for i, scenario in enumerate(scenarios_P_poi):
            values = [np.mean(data_with_MT[pct][scenario][kpi]) for pct in percent_attacked]
            bar_positions = x_indexes + (i - 0.5) * bar_width  # shift left and right
            bars = ax.bar(bar_positions, values, width=bar_width, label=f'Scenario {scenario}', color=colors[i])
    
    
        ax.set_xticks(x_indexes)
        ax.set_xticklabels(percent_attacked_fancy)
    
        # Set title and labels
        if idx == 4:
            ax.set_xlabel('Percent Attacked')
        ax.set_ylabel(KPIs_fancy[idx])
        ax.grid(True)
    
    axes[1,1].legend(label_legend)
    
    plt.tight_layout()
    plt.savefig('figs/P_poi_' + case_MT + '.pdf')
    plt.close()


for case_MT in ['with_MT', 'with_PSM', 'wo_MT']:
    file_name = f'results/' + case_MT + '.json'
    with open(file_name, 'r') as file:
        data_with_MT = json.load(file)
        
    KPIs = ['Precision', 'Recall', 'Accuracy', 'F1', 'z', 'norm2']
    KPIs_fancy = ['Precision (%)', 'Recall (%)', 'Accuracy (%)', 'F1 (%)', 'z (%)', '$||r||_2$ (%)']
    percent_attacked = ['5', '10', '20', '40']
    percent_attacked_fancy = ['5 %', '10 %', '20 %', '40 %']
    scenarios_U_poi = ['2', '3']
    scenarios_P_poi = ['6', '7']
    scenarios_Q_poi = ['4', '5']
    scenarios_U_inversor = ['0']
    
    colors = ['tab:blue', 'tab:orange']
    
    label_legend = ['$Q_{poi} = 0.8·Q_{meas}$', '$Q_{poi} = 1.2·Q_{meas}$']
    
    # Create figure and subplots (2 rows x 3 columns)
    fig, axes = plt.subplots(2, 3, figsize=(16, 8))
    
    bar_width = 0.35
    x_indexes = np.arange(len(percent_attacked))
    
    # Loop over each KPI
    for idx, kpi in enumerate(KPIs):
        if idx < 3:
            ax = axes[0, idx]
        else:
            ax = axes[1, idx-3]
                
        for i, scenario in enumerate(scenarios_Q_poi):
            values = [np.mean(data_with_MT[pct][scenario][kpi]) for pct in percent_attacked]
            bar_positions = x_indexes + (i - 0.5) * bar_width  # shift left and right
            bars = ax.bar(bar_positions, values, width=bar_width, label=f'Scenario {scenario}', color=colors[i])
    
    
        ax.set_xticks(x_indexes)
        ax.set_xticklabels(percent_attacked_fancy)
    
        # Set title and labels
        if idx == 4:
            ax.set_xlabel('Percent Attacked')
        ax.set_ylabel(KPIs_fancy[idx])
        ax.grid(True)
    
    axes[1,1].legend(label_legend)
    
    plt.tight_layout()
    plt.savefig('figs/Q_poi_' + case_MT + '.pdf')
    plt.close()



for case_MT in ['with_MT', 'with_PSM', 'wo_MT']:
    file_name = f'results/' + case_MT + '.json'
    with open(file_name, 'r') as file:
        data_with_MT = json.load(file)
        
    KPIs = ['Precision', 'Recall', 'Accuracy', 'F1', 'z', 'norm2']
    KPIs_fancy = ['Precision (%)', 'Recall (%)', 'Accuracy (%)', 'F1 (%)', 'z (%)', '$||r||_2$ (%)']
    percent_attacked = ['5', '10', '20', '40']
    percent_attacked_fancy = ['5 %', '10 %', '20 %', '40 %']
    scenarios_U_poi = ['2', '3']
    scenarios_P_poi = ['6', '7']
    scenarios_Q_poi = ['4', '5']
    scenarios_U_inversor = ['0']
    
    colors = ['tab:blue', 'tab:orange']
    
    label_legend = ['$U_{inv} = 0.98·U_{meas}$']
    
    # Create figure and subplots (2 rows x 3 columns)
    fig, axes = plt.subplots(2, 3, figsize=(16, 8))
    
    bar_width = 0.35
    x_indexes = np.arange(len(percent_attacked))
    
    # Loop over each KPI
    for idx, kpi in enumerate(KPIs):
        if idx < 3:
            ax = axes[0, idx]
        else:
            ax = axes[1, idx-3]
                
        for i, scenario in enumerate(scenarios_U_inversor):
            values = [np.mean(data_with_MT[pct][scenario][kpi]) for pct in percent_attacked]
            bar_positions = x_indexes + (i - 0.5) * bar_width  # shift left and right
            bars = ax.bar(bar_positions, values, width=bar_width, label=f'Scenario {scenario}', color=colors[i])
    
    
        ax.set_xticks(x_indexes)
        ax.set_xticklabels(percent_attacked_fancy)
    
        # Set title and labels
        if idx == 4:
            ax.set_xlabel('Percent Attacked')
        ax.set_ylabel(KPIs_fancy[idx])
        ax.grid(True)
    
    axes[1,1].legend(label_legend)
    
    plt.tight_layout()
    plt.savefig('figs/U_inversor_' + case_MT + '.pdf')
    plt.close()
