import numpy as np
import json
    
with open('data_std_2.json', 'r') as f:
    data = json.load(f)
    
std_medidas = data['std_medidas'] 
std_solucion = data['std_solucion']
    
names = [
  "P_LV0101",  "Q_LV0101",  "U_LV0101",  "I_LV0101_MV0101",
  "P_LV0102",  "Q_LV0102",  "U_LV0102",  "I_LV0102_MV0102",
  "P_LV0103",  "Q_LV0103",  "U_LV0103",  "I_LV0103_MV0103",
  "P_LV0201",  "Q_LV0201",  "U_LV0201",  "I_LV0201_MV0201",
  "P_LV0202",  "Q_LV0202",  "U_LV0202",  "I_LV0202_MV0202",
  "P_LV0203",  "Q_LV0203",  "U_LV0203",  "I_LV0203_MV0203",
  "P_POIMV_MV0101",  "Q_POIMV_MV0101",  "U_POIMV",  "I_POIMV_MV0101",
  "P_POIMV_MV0201",  "Q_POIMV_MV0201",  "I_POIMV_MV0201",  "P_POI_POIMV",
  "Q_POI_POIMV",  "U_POI",  "I_POI_POIMV"
  ]

import matplotlib.pyplot as plt
from pydae import plot_tools
col = plot_tools.set_style(plt)
from matplotlib.lines import Line2D

f, ax = plt.subplots(1, 1, figsize=(4, 3))

std_P_medidas = [item[0:21:4] for item in std_medidas]
std_Q_medidas = [item[1:22:4] for item in std_medidas]
std_U_medidas = [item[2:23:4] for item in std_medidas]
std_I_medidas = [item[3:24:4] for item in std_medidas]

std_P_solucion = [item[0:21:4] for item in std_solucion]
std_Q_solucion = [item[1:22:4] for item in std_solucion]
std_U_solucion = [item[2:23:4] for item in std_solucion]
std_I_solucion = [item[3:24:4] for item in std_solucion]

for idx, (p_m, q_m, u_m, i_m, p_s, q_s, u_s, i_s) in enumerate(zip(std_P_medidas, std_Q_medidas, std_U_medidas, std_I_medidas,
                                                                   std_P_solucion, std_Q_solucion, std_U_solucion, std_I_solucion)):
    
    if idx in [1, 3]:
        ax.axvspan(idx - 0.5, idx + 0.5, color='lightgray', alpha=0.5)

    lw = 0.2

    ax.scatter(1 * np.ones(len(p_m)) -0.25, p_m, color=col[0], marker = 'o', edgecolor = 'k', linewidth = lw)
    ax.scatter(2 * np.ones(len(q_m)) -0.25, q_m, color=col[1], marker = 'o', edgecolor = 'k', linewidth = lw)
    ax.scatter(3 * np.ones(len(u_m)) -0.25, u_m, color=col[2], marker = 'o', edgecolor = 'k', linewidth = lw)
    ax.scatter(4 * np.ones(len(i_m)) -0.25, i_m, color=col[3], marker = 'o', edgecolor = 'k', linewidth = lw)


    ax.scatter(1 * np.ones(len(p_s)) +0.25, p_s, color=col[0], marker = 's', edgecolor = 'k', linewidth = lw)
    ax.scatter(2 * np.ones(len(q_s)) +0.25, q_s, color=col[1], marker = 's', edgecolor = 'k', linewidth = lw)
    ax.scatter(3 * np.ones(len(u_s)) +0.25, u_s, color=col[2], marker = 's', edgecolor = 'k', linewidth = lw)
    ax.scatter(4 * np.ones(len(i_s)) +0.25, i_s, color=col[3], marker = 's', edgecolor = 'k', linewidth = lw)

# Etiquetas y leyenda
ax.set_xticks([1, 2, 3, 4])
ax.set_xticklabels(['P', 'Q', 'U', 'I'])
ax.set_ylabel('$\sigma$')
plt.tight_layout()
plt.show()
f.savefig('std2_fig.svg')


