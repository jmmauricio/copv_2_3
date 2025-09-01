import json
import matplotlib.pyplot as plt

for band in [str(item) for item in range(10)]:
    # Cargar el JSON
    with open('detection_bands_' + band + '.json', 'r') as f:
        data = json.load(f)
    
    # Seleccionar el factor de potencia que quieras analizar
    for power_factor in ['090neg', '090pos', '100pos']:
    
        # Orden de las horas y magnitudes
        horas = ['08', '10', '13']
        magnitudes = ['P', 'Q', 'U']
        
        # Crear figura con subplots 3x3
        fig, axs = plt.subplots(3, 3, figsize=(12, 8), sharex=True, sharey=True)
        
        for i, hora in enumerate(horas):
            for j, magnitud in enumerate(magnitudes):
                ax = axs[i, j]
                
                # Obtener el conjunto de lambdas y listas de detección
                lambda_keys = sorted(data[power_factor][hora].keys(), key=lambda x: float(x))
                porcentajes_true = []
                porcentajes_false = []
                
                for lmbd in lambda_keys:
                    detecciones = data[power_factor][hora][lmbd][magnitud]['Detection']
                    total = len(detecciones)
                    verdaderos = sum(detecciones)
                    falsos = total - verdaderos
                    porcentajes_true.append(100 * verdaderos / total)
                    porcentajes_false.append(100 * falsos / total)
                
                # Dibujar las líneas
                lambdas_float = [float(l) for l in lambda_keys]
                ax.plot(lambdas_float, porcentajes_true, color='skyblue', label='Detected (%)')
                ax.plot(lambdas_float, porcentajes_false, color='salmon', label='Not detected (%)')
                
                ax.grid(True)
                ax.set_xlim([0, 10])
                if i == 2:
                    ax.set_xlabel('$\lambda$')
                if j == 0:
                    if i == 0:
                        ax.set_ylabel('8 h')
                    if i == 1:
                        ax.set_ylabel('10 h')
                    if i == 2:
                        ax.set_ylabel('13 h')
                if i == 0:
                    if j == 0:
                        ax.set_title('P')
                    if j == 1:
                        ax.set_title('Q')
                    if j == 2:
                        ax.set_title('U')
                    
        
        
        # Agregar leyenda común
        axs[0,0].legend()
        plt.tight_layout()
        plt.savefig('figs/detection_bands_' + band + '_' + power_factor + '.pdf')
        plt.close()