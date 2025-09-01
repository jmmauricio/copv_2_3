import json
import matplotlib.pyplot as plt
import numpy as np

# Cargar el archivo JSON
with open('detection.json') as f:
    data = json.load(f)

# Parámetros fijos
power_factor = '100pos'
time_instants = ['08', '10', '13']
magnitudes = ['P', 'Q', 'U']

# Crear figura con subplots
fig, axs = plt.subplots(3, 3, figsize=(12, 9), sharex=True, sharey=True)
fig.suptitle('Power factor: ' + power_factor)
# Iterar sobre cada combinación de instante y magnitud
for i, time in enumerate(time_instants):
    for j, magnitude in enumerate(magnitudes):
        ax = axs[i, j]
        lambda_keys = list(data[power_factor][time].keys())
        lambda_keys.sort(key=lambda x: float(x))  # Ordenar por valor numérico

        true_percentages = []
        false_percentages = []

        for lam in lambda_keys:
            detections = data[power_factor][time][lam][magnitude]['Detection']
            total = len(detections)
            trues = sum(detections)
            falses = total - trues
            true_percentages.append(100 * trues / total)
            false_percentages.append(100 * falses / total)

        lambda_values = [float(l) for l in lambda_keys]

        # Gráfica
        ax.plot(lambda_values, true_percentages, label='Detected (%)', color='skyblue')
        ax.plot(lambda_values, false_percentages, label='Not detected (%)', color='salmon')
        if i == 2:
            ax.set_xlabel('$\lambda$')
        if j == 0 and i == 0:
            ax.set_ylabel('8 h')        
        if j == 0 and i == 1:
            ax.set_ylabel('10 h')        
        if j == 0 and i == 2:
            ax.set_ylabel('13 h')
        if i == 0 and j == 0:
            ax.set_title('P')        
        if i == 0 and j == 1:
            ax.set_title('Q')        
        if i == 0 and j == 2:
            ax.set_title('U')
        ax.grid(True)

        if i == 0 and j == 0:
            ax.legend()
        ax.set_xlim([0, 10])

plt.tight_layout(rect=[0, 0, 0.95, 0.95])
plt.show()
plt.savefig('detection_' + power_factor + '.pdf')
