

def plotting_analysis(ataque, dict_res, names):
    
    import json
    import numpy as np
    import matplotlib.pyplot as plt
    from pydae import plot_tools
    
    data = dict_res
    std_solucion = data['std'] 
    Q = data['Q']
    l = data['lmb']
    labels = ['WLS']
    for index, item in enumerate(zip(l, Q)):
        labels.append('$\lambda$ = ' + str(np.round(item[0],2)) + ', Q = ' + str(np.round(item[1],2)))
     
    
    # Agrupar índices por prefijo
    groups = {
        'P_': [i for i, name in enumerate(names) if name.startswith('P_LV')],
        'Q_': [i for i, name in enumerate(names) if name.startswith('Q_LV')],
        'I_': [i for i, name in enumerate(names) if name.startswith('I_LV')],
        'U_': [i for i, name in enumerate(names) if name.startswith('U_LV')]
    }
    
    # Estilo
    col = plot_tools.set_style(plt)
    
    # Crear la figura con 4 subgráficos
    f, ax = plt.subplots(2, 2, figsize=(14, 8))
    bar_width = 0.8/len(std_solucion)
    
    for idx, (key, indices) in enumerate(groups.items()):
        row = 0 if idx == 0 or idx == 1 else 1
        column = idx if idx < 2 else idx - 2 
        
        x = np.arange(len(indices))  
        x_positions = [x + i * bar_width - 0.3 for i in range(len(std_solucion))]  
    
        for i in range(len(x)):
            if i % 2 != 0:
                ax[row, column].axvspan(i - 0.5, i + 0.5, color='gray', alpha=0.1)
    
        max_value = 0
        min_value = 1
        for i, std_vals in enumerate(std_solucion):
            ax[row, column].bar(
                x_positions[i],                      
                [std_vals[item] for item in indices],                  
                width=bar_width,                    
                color=col[i % len(col)],            
                label=labels[i] if idx == 1 else "" 
            )
            if np.max([std_vals[item] for item in indices]) > max_value:
                max_value = np.max([std_vals[item] for item in indices])
            if np.min([std_vals[item] for item in indices]) < min_value:
                min_value = np.min([std_vals[item] for item in indices])
        
        # Etiquetas y formato
        delta = (max_value - min_value)/5
        ax[row, column].set_ylim([min_value - delta, max_value + delta])
        ax[row, column].set_xticks(x)
        ax[row, column].set_xticklabels([names[i] for i in indices], rotation=0, fontsize=8)
        ax[row, column].set_ylabel('$\sigma$')
    
    ax[0,1].legend(ncol=4)
    plt.tight_layout()
    plt.show()
    plt.close()
    f.savefig('figs/std2_comparative_fig' + ataque + '.pdf')
    
    if ataque.startswith('I_') == False:
    
        # Parte de MV
        import numpy as np
        import json
        import matplotlib.pyplot as plt
        from pydae import plot_tools
        
            
        std_solucion = data['std'] 
        Q = data['Q']
        l = data['lmb']
        labels = ['WLS']
        for index, item in enumerate(zip(l, Q)):
            labels.append('$\lambda$ = ' + str(np.round(item[0],2)) + ', Q = ' + str(np.round(item[1],2)))
                
        # Definir nombres de las variables
        
        
        # Configuración de subplots
        subplot_config = {
            (0, 0): ["P_POIMV_MV0101", "P_POIMV_MV0201"],
            (0, 1): ["Q_POIMV_MV0101", "Q_POIMV_MV0201"],
            (0, 2): ["P_POI_POIMV", "Q_POI_POIMV"],
            (1, 0): ["U_POIMV"],
            (1, 1): ["I_POIMV_MV0101"],
            (1, 2): ["I_POIMV_MV0201", "I_POI_POIMV"]  # Combinadas
        }
        
        # Estilo
        col = plot_tools.set_style(plt)
        
        f, ax = plt.subplots(2, 3, figsize=(14, 8))
        bar_width = 0.8 / len(std_solucion)
        
        for idx, keys in enumerate(subplot_config.items()):
            indices = [names.index(item) for item in keys[1]]
            row = 0 if idx < 3 else 1
            column = idx if idx < 3 else idx - 3 
            
            x = np.arange(len(indices))  
            x_positions = [x + i * bar_width - 0.3 for i in range(len(std_solucion))]  
        
            for i in range(len(x)):
                if i % 2 != 0:
                    ax[row, column].axvspan(i - 0.5, i + 0.5, color='gray', alpha=0.1)
        
            max_value = 0
            min_value = 1
            for i, std_vals in enumerate(std_solucion):
                ax[row, column].bar(
                    x_positions[i],
                    [std_vals[item] for item in indices],
                    width=bar_width,
                    label=labels[i] if idx == 1 else "" 
                )
                if np.max([std_vals[item] for item in indices]) > max_value:
                    max_value = np.max([std_vals[item] for item in indices])
                if np.min([std_vals[item] for item in indices]) < min_value:
                    min_value = np.min([std_vals[item] for item in indices])
        
            # Etiquetas y formato
            delta = (max_value - min_value)/5
            ax[row, column].set_ylim([min_value - delta, max_value + delta])
            ax[row, column].set_xticks(x)
            ax[row, column].set_xticklabels([names[i] for i in indices], rotation=0, fontsize=8)
            ax[row, column].set_ylabel('$\sigma$')
        
        
        
        ax[0,1].legend(ncol=1)
        plt.tight_layout()
        plt.show()
        plt.close()
        f.savefig('figs/std2_comparative_fig_MV' + ataque + '.pdf')



















