import json
import matplotlib.pyplot as plt
import os
import datetime as dt
import pandas as pd
from matplotlib.dates import DateFormatter, HourLocator
from pydae import plot_tools

# Estilo y colores
colors = plot_tools.set_style(plt)

plt.rcParams.update({
    'font.size': 11,
    'axes.labelsize': 11,
    'axes.titlesize': 11,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'legend.fontsize': 10,
    'figure.titlesize': 12
})

# Función para leer JSON
def leer_json(ruta):
    with open(ruta, 'r') as f:
        return json.load(f)

# Carpeta
carpeta = "results"

# Archivos
archivo_p_smart = os.path.join(carpeta, "P_poi_integrated_smart.json")
archivo_p_scenarios = os.path.join(carpeta, "P_poi_integrated_scenarios.json")

archivo_deterministic = os.path.join(carpeta, "deterministic_integrated_smart.json")
archivo_huber = os.path.join(carpeta, "Huber_integrated_smart.json")
archivo_wls = os.path.join(carpeta, "WLS_integrated_smart.json")

# Leer datos
potencia_smart = leer_json(archivo_p_smart)
potencia_scenarios = leer_json(archivo_p_scenarios)

deterministic = leer_json(archivo_deterministic)
huber = leer_json(archivo_huber)
wls = leer_json(archivo_wls)

# Crear eje temporal
ano, mes, dia, hora, minuto = 2024, 8, 10, 5, 48
intervalo = dt.timedelta(minutes=5)
n_puntos = len(potencia_smart)
tiempos = [dt.datetime(ano, mes, dia, hora, minuto) + i*intervalo for i in range(n_puntos)]

# Crear arrays de ceros para Hellinger y Bendford
bendford = [0] * n_puntos
hellinger = [0] * n_puntos

# Crear figura con 6 subplots
fig, axs = plt.subplots(7, 1, figsize=(7, 8),
                        sharex=True,
                        gridspec_kw={'height_ratios': [2, 1, 1, 1, 1, 1, 1]})

# === Subplot 1: Potencia activa ===
axs[0].plot(tiempos, [-x*10 for x in potencia_smart], color=colors[2], label=r"P(POI)$\times$ 0.8")
axs[0].plot(tiempos, [-x*10 for x in potencia_scenarios], color='black', linewidth=2.5, label="P(POI)")
axs[0].set_ylabel("Active power (MW)")
axs[0].legend(loc="upper right")
axs[0].grid(True)

# === Subplot 2: Deterministic ===
axs[1].step(tiempos, deterministic, where='mid', color=colors[2])
axs[1].set_ylabel("Deterministic")
axs[1].set_ylim(-0.1, 1.1)
axs[1].set_yticks([0, 1])
axs[1].grid(True)

# === Subplot 3: Bendford ===
axs[2].step(tiempos, bendford, where='mid', color=colors[2])
axs[2].set_ylabel("Bendford")
axs[2].set_ylim(-0.1, 1.1)
axs[2].set_yticks([0, 1])
axs[2].grid(True)

# === Subplot 4: Hellinger ===
axs[3].step(tiempos, hellinger, where='mid', color=colors[2])
axs[3].set_ylabel("Hellinger")
axs[3].set_ylim(-0.1, 1.1)
axs[3].set_yticks([0, 1])
axs[3].grid(True)

# === Subplot 5: WLS ===
axs[4].step(tiempos, wls, where='mid', color=colors[2])
axs[4].set_ylabel("WLS")
axs[4].set_ylim(-0.1, 1.1)
axs[4].set_yticks([0, 1])
axs[4].grid(True)

# === Subplot 6: Huber ===
axs[5].step(tiempos, huber, where='mid', color=colors[2])
axs[5].set_ylabel("Huber")
axs[5].set_ylim(-0.1, 1.1)
axs[5].set_yticks([0, 1])
axs[5].grid(True)

# === Subplot 7: Huber ===
detection = [1 if any(item) else 0 for item in zip(deterministic, wls, huber)]


axs[6].step(tiempos, detection, where='mid', color=colors[2])
axs[6].set_ylabel("Detection")
axs[6].set_ylim(-0.1, 1.1)
axs[6].set_yticks([0, 1])
axs[6].grid(True)

# Eje X: formato y límites
axs[6].xaxis.set_major_locator(HourLocator())
axs[6].xaxis.set_major_formatter(DateFormatter('%H'))
for ax in axs:
    plt.setp(ax.get_xticklabels(), rotation=45)

inicio = dt.datetime(ano, mes, dia, 6, 0)
fin = tiempos[-60]
axs[6].set_xlim(left=inicio, right=fin)
axs[6].set_xlabel('time (h)')

fig.align_ylabels(axs)
plt.tight_layout()
plt.savefig('integrated_smart_poi.pdf')
plt.show()

# Detection!



import numpy as np
total = np.sum([True if np.abs(item) > 0.0001 else False for item in potencia_scenarios])


print(f'Deterministic: {np.sum([True if item > 0 else False for item in deterministic])*100/total}')
print(f'Bendford: {np.sum([True if item > 0 else False for item in bendford])*100/total}')
print(f'Hellinger: {np.sum([True if item > 0 else False for item in hellinger])*100/total}')
print(f'WLS: {np.sum([True if item > 0 else False for item in wls])*100/total}')
print(f'Huber: {np.sum([True if item > 0 else False for item in huber])*100/total}')
print(f'Overall: {np.sum([True if item > 0 else False for item in detection])*100/total}')
print('')