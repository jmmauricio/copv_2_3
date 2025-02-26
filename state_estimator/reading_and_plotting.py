import numpy as np
import json
import matplotlib.pyplot as plt
from pydae import plot_tools
from collections import Counter

# Leemos el json de resultados
with open('data_simus_ts.json','r') as file:
    data = json.load(file)     
    
# '090neg', '090pos', '100pos'
# '08', '09', '10', '11', '12', '13', '14'
# 'P', 'Q', 'U'

# Recordamos los valores de lambda considerados
num_lmb = 100
lmb_range = np.linspace(0.01, 50, num_lmb)

# Generamos los ataques para cada variable
c = '090neg'
hour = '14'
x_values = [str(item) for item in np.linspace(0.01, 50, 100)]
subplots_titles = ['P', 'Q', 'U']

fig, axs = plt.subplots(3, 1, figsize=(8, 6), sharex=True)

# Definimos los colores del plot
colors = plot_tools.set_style(plt)
colors.pop(3)

# Establecemos las etiquetas
labels = ['Detection', 'Detection and others', 'Incorrect detection', 'No detection']

# Inicializamos figura
for i, pqu in enumerate(subplots_titles):
    counts = []

    for x in x_values:
        values = list(data[c][hour][x][pqu].values())
        counts.append(values)

    counts = np.array(counts).T  # Transponer para separar por 0, 1, 2, 3

    axs[i].stackplot(
        lmb_range, 
        counts, 
        labels=labels,
        alpha=0.7
    )

    axs[i].set_ylabel(subplots_titles[i])
    axs[i].grid(True)

axs[-1].legend()
axs[-1].set_xlabel('$\lambda$')
plt.tight_layout()
plt.show()