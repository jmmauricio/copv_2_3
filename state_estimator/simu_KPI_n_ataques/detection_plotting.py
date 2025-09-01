import json
import matplotlib.pyplot as plt

# Función para cargar los datos desde un archivo JSON
def load_data(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

# Cargar los datos
file1 = 'detection_15_20.json'
file2 = 'detection_10_15.json'

data1 = load_data(file1)
data2 = load_data(file2)

# Parámetros comunes
power_factors = ['090neg', '090pos']
num_attacks = [str(n) for n in range(3, 19)]
colors = {
    file1: 'skyblue',
    file2: 'salmon'
}
labels_pf = [r'$\cos \varphi = 0.9 \, (i)$', r'$\cos \varphi = 0.9 \, (c)$']

# Crear la figura
fig, axes = plt.subplots(2, 1, figsize=(7, 5), sharex=True)

# Iterar por cada factor de potencia
for i, pf in enumerate(power_factors):
    ax = axes[i]

    # Extraer datos de detección por número de ataques
    true_percent_1 = []
    true_percent_2 = []

    for n in num_attacks:
        try:
            detections1 = data1[pf]['10']['2.5'][n]['Detection']
            true_percent_1.append(100 * sum(detections1) / len(detections1))
        except:
            true_percent_1.append(None)

        try:
            detections2 = data2[pf]['10']['2.5'][n]['Detection']
            true_percent_2.append(100 * sum(detections2) / len(detections2))
        except:
            true_percent_2.append(None)

    # Dibujar las líneas
    ax.plot(num_attacks, true_percent_1, color=colors[file1], label=r'$\pm 15-20\%$')
    ax.plot(num_attacks, true_percent_2, color=colors[file2], label=r'$\pm 10-15\%$')

    # Etiqueta superior izquierda con FP
    ax.text(
        0.98, 0.8, labels_pf[i],
        transform=ax.transAxes,
        fontsize=10,
        ha='right', va='top',
        bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.3')
    )

    ax.set_ylabel('Detection (%)')
    ax.set_ylim([90, 101])
    ax.grid(True)

# Etiqueta X común
axes[1].set_xlabel('Number of attacks')

# Leyenda común de rangos
handles_ranges = [
    plt.Line2D([0], [0], color=colors[file1], linestyle='-', label=r'$\pm 15-20\%$'),
    plt.Line2D([0], [0], color=colors[file2], linestyle='-', label=r'$\pm 10-15\%$')
]

legend_ranges = fig.legend(
    handles=handles_ranges,
    loc='upper center',
    bbox_to_anchor=(0.5, 1.0),
    ncol=2,
    frameon=False
)

# Guardar resultados
plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.savefig('figs/n_attacks_detection_true.pdf')
plt.savefig('figs/n_attacks_detection_true.png')
# plt.close()
