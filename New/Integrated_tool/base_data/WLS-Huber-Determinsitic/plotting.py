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

# Etiquetas
label_P = ["P(LV0102) × 0.5", "P(LV0102) × 1.2", "P(LV0102) × 3.0", "P(LV0102)"]

# Función para leer JSON
def leer_json(ruta):
    with open(ruta, 'r') as f:
        return json.load(f)

# Conversión True/False a niveles (1.0, 0.9, 0.8)
def asignar_nivel(lista, valor):
    return [valor if x else 0 for x in lista]

# Carpeta
carpeta = "results"

# Archivos JSON
archivos_potencia = [
    os.path.join(carpeta, "P_poi_integrated_dummy_0_5.json"),
    os.path.join(carpeta, "P_poi_integrated_dummy_1_2.json"),
    os.path.join(carpeta, "P_poi_integrated_dummy_3.json"),
    os.path.join(carpeta, "P_poi_integrated_scenarios.json")
]

archivos_huber = [
    os.path.join(carpeta, "Huber_integrated_dummy_0_5.json"),
    os.path.join(carpeta, "Huber_integrated_dummy_1_2.json"),
    os.path.join(carpeta, "Huber_integrated_dummy_3.json")
]

archivos_wls = [
    os.path.join(carpeta, "WLS_integrated_dummy_0_5.json"),
    os.path.join(carpeta, "WLS_integrated_dummy_1_2.json"),
    os.path.join(carpeta, "WLS_integrated_dummy_3.json")
]

# Leer datos JSON
potencias = [leer_json(f) for f in archivos_potencia]
niveles = [1.0, 0.9, 0.8]
huber_data = [asignar_nivel(leer_json(f), niveles[i]) for i, f in enumerate(archivos_huber)]
wls_data = [asignar_nivel(leer_json(f), niveles[i]) for i, f in enumerate(archivos_wls)]

# Leer datos desde Excel
df_excel = pd.read_excel("results/Detect_plausability.xlsx")
bendford_real = df_excel["Bendford"].tolist()
hellinger_real = df_excel["Hellinger"].tolist()

# Crear eje temporal
ano, mes, dia, hora, minuto = 2024, 8, 10, 5, 48
intervalo = dt.timedelta(minutes=5)
n_puntos = len(potencias[0])
tiempos = [dt.datetime(ano, mes, dia, hora, minuto) + i*intervalo for i in range(n_puntos)]

# Crear arrays adicionales (dos líneas de ceros para Bendford y Hellinger)
bendford_zeros_1 = [0] * n_puntos
bendford_zeros_2 = [0] * n_puntos
hellinger_zeros_1 = [0] * n_puntos
hellinger_zeros_2 = [0] * n_puntos

# Añadir rutas de archivos Deterministic
archivos_deterministic = [
    os.path.join(carpeta, "deterministic_integrated_dummy_0_5.json"),
    os.path.join(carpeta, "deterministic_integrated_dummy_1_2.json"),
    os.path.join(carpeta, "deterministic_integrated_dummy_3.json")
]

# Leer y procesar los datos de Deterministic
deterministic_data = [asignar_nivel(leer_json(f), niveles[i]) for i, f in enumerate(archivos_deterministic)]

# Crear figura con 6 subplots
fig, axs = plt.subplots(7, 1, figsize=(7, 8),
                        sharex=True,
                        gridspec_kw={'height_ratios': [2, 1, 1, 1, 1, 1, 1]})

# === Subplot 1: Potencia activa ===
for i, data in enumerate(potencias):
    if i == 3:
        axs[0].plot(tiempos, [x*10 for x in data], color='black', linewidth=2.5, label=label_P[i])
    else:
        axs[0].plot(tiempos, [x*10 for x in data], color=colors[i % len(colors)], label=label_P[i])
axs[0].set_ylabel("Active power (MW)")
axs[0].legend(loc="upper right")
axs[0].set_ylim(min(min(p)*10 for p in potencias)*0.95, max(max(p)*10 for p in potencias)*1.05)
axs[0].grid(True)

# === Subplot 2: Deterministic ===
for i, data in enumerate(deterministic_data):
    axs[1].step(tiempos, data, where='mid', color=colors[i % len(colors)])
axs[1].set_ylabel("Deterministic")
axs[1].set_ylim(-0.1, 1.1)
axs[1].set_yticks([0, 1])
axs[1].grid(True)

# === Subplot 3: Bendford ===
axs[2].step(tiempos, bendford_zeros_1, where='mid', color=colors[0])
axs[2].step(tiempos, bendford_zeros_2, where='mid', color=colors[1])
axs[2].step(tiempos, bendford_real, where='mid', color=colors[2])
axs[2].set_ylabel("Bendford")
axs[2].set_ylim(-0.1, 1.1)
axs[2].set_yticks([0, 1])
axs[2].grid(True)

# === Subplot 4: Hellinger ===
axs[3].step(tiempos, hellinger_zeros_1, where='mid', color=colors[0])
axs[3].step(tiempos, hellinger_zeros_2, where='mid', color=colors[1])
axs[3].step(tiempos, hellinger_real, where='mid', color=colors[2])
axs[3].set_ylabel("Hellinger")
axs[3].set_ylim(-0.1, 1.1)
axs[3].set_yticks([0, 1])
axs[3].grid(True)

# === Subplot 5: WLS ===
for i, data in enumerate(wls_data):
    axs[4].step(tiempos, data, where='mid', color=colors[i % len(colors)])
axs[4].set_ylabel("WLS")
axs[4].set_ylim(-0.1, 1.1)
axs[4].set_yticks([0, 1])
axs[4].grid(True)

# === Subplot 6: Huber ===
for i, data in enumerate(huber_data):
    axs[5].step(tiempos, data, where='mid', color=colors[i % len(colors)])
axs[5].set_ylabel("Huber")
axs[5].set_ylim(-0.1, 1.1)
axs[5].set_yticks([0, 1])
axs[5].grid(True)

# === Subplot 7: Huber ===
detection0 = [1 if any(item) else 0 for item in zip(deterministic_data[0], wls_data[0], huber_data[0])]
detection1 = [1 if any(item) else 0 for item in zip(deterministic_data[1], wls_data[1], huber_data[1])]
detection2 = [1 if any(item) else 0 for item in zip(deterministic_data[2], wls_data[2], huber_data[2])]



axs[6].step(tiempos, [item*1 for item in detection0], where='mid', color=colors[0])
axs[6].step(tiempos, [item*0.9 for item in detection1], where='mid', color=colors[1])
axs[6].step(tiempos, [item*0.8 for item in detection2], where='mid', color=colors[2])
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
plt.savefig('integrated.pdf')
plt.show()


import numpy as np
total = np.sum([True if item > 0 else False for item in potencias[0]])
det = [detection0, detection1, detection2]

for idx in range(3):
    print(f'Deterministic: {np.sum([True if item > 0 else False for item in deterministic_data[idx]])*100/total}')
    print(f'Bendford: {np.sum([True if item > 0 else False for item in bendford_real])*100/total}')
    print(f'Hellinger: {np.sum([True if item > 0 else False for item in hellinger_real])*100/total}')
    print(f'WLS: {np.sum([True if item > 0 else False for item in wls_data[idx]])*100/total}')
    print(f'Huber: {np.sum([True if item > 0 else False for item in huber_data[idx]])*100/total}')
    print(f'Overall: {np.sum([True if item > 0 else False for item in det[idx]])*100/total}')
    print('')






