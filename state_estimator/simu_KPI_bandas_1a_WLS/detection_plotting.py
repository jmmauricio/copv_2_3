import json
import matplotlib.pyplot as plt

from pydae import plot_tools

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

# Función para cargar los datos desde un archivo JSON
def load_data(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

# Cargar los datos
file1 = 'detection_n_0.json'

data1 = load_data(file1)

# Parámetros comunes
power_factors = ['090pos']
num_attacks = [str(n) for n in range(2, 19)]

labels_pf = [r'$\cos \varphi = 0.9 \, (c)$']

# Crear la figura
fig, axes = plt.subplots(1, 1, figsize=(7, 3))

# Iterar por cada factor de potencia
for i, pf in enumerate(power_factors):
    ax = axes

    # Extraer datos de detección por número de ataques
    true_percent_1 = []

    for n in num_attacks:
        try:
            detections1 = data1[pf]['13'][n]['2.5']['Detection']
            true_percent_1.append(100 * sum(detections1) / len(detections1))
        except:
            true_percent_1.append(None)

        

    # Dibujar las líneas
    ax.plot(num_attacks, true_percent_1, color=colors[0])


    ax.set_ylabel('Detection (%)')
    ax.set_ylim([0, 100])
    ax.grid(True)

# # Etiqueta X común
axes.set_xlabel('Number of attacks')

# # Leyenda común de rangos
# handles_ranges = [
#     plt.Line2D([0], [0], color=colors[file1], linestyle='-', label=r'$\pm 15-20\%$'),
#     plt.Line2D([0], [0], color=colors[file2], linestyle='-', label=r'$\pm 10-15\%$')
# ]

# legend_ranges = fig.legend(
#     handles=handles_ranges,
#     loc='upper center',
#     bbox_to_anchor=(0.5, 1.0),
#     ncol=2,
#     frameon=False
# )

# # Guardar resultados
plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.savefig('figs/n_attacks_detection_wls.pdf')
# plt.close()
