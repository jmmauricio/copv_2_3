import json
import matplotlib.pyplot as plt

# Función para cargar los datos desde un archivo JSON
def load_data(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

# Cargar los datos de los dos archivos
file1 = 'data_n_attacks_KPI_15_20.json'
file2 = 'data_n_attacks_KPI_10_15.json'

data1 = load_data(file1)
data2 = load_data(file2)

# Extraer los factores de potencia (niveles superiores)
power_factors = list(data1.keys())[:2]  # ['090neg', '090pos', '100pos']

# Número de ataques comunes en ambos archivos
num_attacks = ['3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18']

# Definir colores para cada archivo
colors = {
    file1: 'blue',
    file2: 'orange'
}

# Definir estilos de línea para las métricas
line_styles = {
    'Precision': '-',
    'Accuracy': '--',
    'Recall': '-.',
    'F1': ':'
}

texto_pf = [r'$\cos \varphi = 0.9 \, (i)$', r'$\cos \varphi = 0.9 \, (c)$']

# Crear una figura con 3 filas y 1 columna de subplots
fig, axes = plt.subplots(2, 1, figsize=(7, 5))

# Iterar sobre cada factor de potencia
for i, pf in enumerate(power_factors):
    ax = axes[i]
    
    # Obtener los datos para este factor de potencia en ambos archivos
    metrics1 = data1[pf]['10']['2.5']
    metrics2 = data2[pf]['10']['2.5']
    
    # Graficar las métricas para el primer archivo
    for metric, style in line_styles.items():
        if metric == 'F1':
            values = [(2*metrics1[attack]['Precision']*metrics1[attack]['Recall']/(metrics1[attack]['Precision']+metrics1[attack]['Recall'])) * 100 for attack in num_attacks]
            ax.plot(num_attacks, values, label=f'{metric} ({file1})', color=colors[file1], linestyle=style)
        else:
            values = [metrics1[attack][metric] * 100 for attack in num_attacks]
            ax.plot(num_attacks, values, label=f'{metric} ({file1})', color=colors[file1], linestyle=style)
    
    # Graficar las métricas para el segundo archivo
    for metric, style in line_styles.items():
        if metric == 'F1':
            values = [(2*metrics2[attack]['Precision']*metrics2[attack]['Recall']/(metrics2[attack]['Precision']+metrics2[attack]['Recall'])) * 100 for attack in num_attacks]
            ax.plot(num_attacks, values, label=f'{metric} ({file2})', color=colors[file2], linestyle=style)
        else:
            values = [metrics2[attack][metric] * 100 for attack in num_attacks]
            ax.plot(num_attacks, values, label=f'{metric} ({file2})', color=colors[file2], linestyle=style)

    
    ax.text(
        0.98, 0.98, texto_pf[i],  # Posición relativa (esquina superior derecha)
        transform=ax.transAxes,  # Coordenadas relativas al eje
        fontsize=10, color='black',
        ha='right', va='top',  # Alineación horizontal y vertical
        bbox=dict(facecolor='white', edgecolor='black', boxstyle='round,pad=0.3')  # Estilo del marco
    )
    
    # Configurar el subplot
    ax.set_ylabel('%')
    ax.set_ylim([40, 100])
    ax.grid(True)

# Compartir ejes x entre los subplots
axes[1].set_xlabel('Number of attacks')

# Crear una leyenda personalizada encima del primer subplot
handles_metrics = [
    plt.Line2D([0], [0], color='black', linestyle='-', label='Precision'),
    plt.Line2D([0], [0], color='black', linestyle='--', label='Accuracy'),
    plt.Line2D([0], [0], color='black', linestyle='-.', label='Recall'),
    plt.Line2D([0], [0], color='black', linestyle=':', label='F1')
]

legend_metrics = fig.legend(
    handles=handles_metrics,
    loc='upper center',
    bbox_to_anchor=(0.3, 1.0),  # Posición ajustada a la izquierda
    ncol=2,  # Dos columnas
    frameon=False
)

# Segunda leyenda: Rangos de porcentaje
handles_ranges = [
    plt.Line2D([0], [0], color=colors[file1], linestyle='-', label=r'$\pm 15-20 \%$'),
    plt.Line2D([0], [0], color=colors[file2], linestyle='-', label=r'$\pm 10-15 \%$')
]

legend_ranges = fig.legend(
    handles=handles_ranges,
    loc='upper center',
    bbox_to_anchor=(0.72, 0.98),  # Posición ajustada a la derecha
    ncol=2,  # Una sola columna
    frameon=False
)

plt.savefig('figs/n_attacks.pdf')
plt.savefig('figs/n_attacks.png')
# plt.close()