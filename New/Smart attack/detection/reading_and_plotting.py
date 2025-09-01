import matplotlib.pyplot as plt
import numpy as np
import json

plt.rcParams.update({
    'font.size': 11,
    'axes.labelsize': 11,
    'axes.titlesize': 11,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'legend.fontsize': 10,
    'figure.titlesize': 12
})

name = 'detection_with_MT'

with open('results/' + name + '.json', 'r') as file:
    Res = json.load(file)

# Define percent_attacked values and scenarios
percent_values = ['5', '10', '20', '40']
scenarios = [0,1,8,9,4,5,6,7,8,9]

# Set up the figure and 2x2 subplots
fig, axes = plt.subplots(2, 2, figsize=(7, 5))
axes = axes.flatten()  # Flatten to easily iterate

for idx, percent in enumerate(percent_values):
    ax = axes[idx]
    true_percentages = []
    false_percentages = []

    for scenario in scenarios:
        detections = Res[percent][str(scenario)]['Detection']
        true_count = sum(detections)
        total = len(detections)
        true_percentage = (true_count / total) * 100
        false_percentage = 100 - true_percentage

        true_percentages.append(true_percentage)
        false_percentages.append(false_percentage)
        
    print(percent)
    print(true_percentages)

    x_indexes = np.arange(len(scenarios))
    bar_width = 0.4

    # Plot bars
    ax.bar(x_indexes, true_percentages, width=bar_width, label='Detected (%)', color='skyblue')
    ax.bar(x_indexes + bar_width, false_percentages, width=bar_width, label='Not Detected (%)', color='salmon')

    # Formatting
    ax.set_ylabel(f'{percent}% Attacked')
    if idx >1:
        ax.set_xlabel('Scenario')
    if idx <=1:
        ax.set_xticks([])
    else:
        ax.set_xticks(x_indexes + bar_width / 2)
        ax.set_xticklabels(scenarios)
    if idx == 2:
        ax.legend(loc='center')
    ax.grid(axis='y', linestyle='--', alpha=0.7)

# Adjust layout
plt.tight_layout()
plt.show()
plt.savefig(name + '.pdf')