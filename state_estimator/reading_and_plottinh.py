import numpy as np
import json
import matplotlib.pyplot as plt
from pydae import plot_tools

# Leemos el json de resultados
with open('data_simus_ts.json','r') as file:
    data = json.load(file)     
    
# '090neg', '090pos', '100pos'
# '08', '09', '10', '11', '12', '13', '14'
# 'P', 'Q', 'U'

# Recordamos los valores de lambda considerados
num_lmb = 3
lmb_range = np.linspace(0.01, 50, num_lmb)

# Generamos los ataques para cada variable
c = '100pos'
hour = '12'
tipo = 'P'

# Definimos los colores del plot
colors = plot_tools.set_style(plt)
colors.pop(3)

# Establecemos las etiquetas
labels = ['Detection', 'Detection and others', 'Incorrect detection', 'No detection']

# Inicializamos figura
fig, axes = plt.subplots(3, 1, figsize=(8, 10), sharex=True)

for i, ax in enumerate(axes):
    counts = {num: [] for num in range(4)} 
    for idx in range(len(lmb_range)):
        sublist = data[c][hour][tipo][idx]
        for num in range(4):
            counts[num].append(sublist.count(num))
            
    values = [counts[num] for num in range(4)]
    
    ax.stackplot(lmb_range, *values, labels=labels, colors=colors, alpha=0.6)  

    ax.grid(True)

  
# Establecemos los adornos
axes[0].set_ylabel('$P$')
axes[1].set_ylabel('$Q$')
axes[2].set_ylabel('$U$')

axes[-1].set_xlabel('$\lambda$')
axes[-1].legend()
plt.show()
