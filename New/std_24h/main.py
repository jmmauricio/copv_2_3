import lib
import numpy as np
import matplotlib.pyplot as plt

minutes = ['00', '15', '30', '45']
hours = ['00', '01', '02', '03', '04', '05', '06', '07', '08', '09', 
         '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', 
         '20', '21', '22', '23']  # Nota: eliminé '24' porque no hay hora 24:00 (sería 00:00 del día siguiente)

P_std, Q_std, U_std, I_std = [], [], [], []
P_value = []

for h in hours:
    for m in minutes:
        net = lib.grid(path_topology='../../data/pv_2_3.json', 
                       path_measurements=f'../../data/pv_2_3_180_{h}_{m}_pf_090pos/measurements.json',
                       MT=True)   
        P_std.append(net.meas[0].std)
        Q_std.append(net.meas[1].std)
        U_std.append(net.meas[2].std)
        I_std.append(net.meas[3].std)
        P_value.append(net.meas[0].value)

# Convertir a arrays si es necesario (opcional, pero útil)
P_value = np.array(P_value)
P_std = np.array(P_std)
Q_std = np.array(Q_std)
U_std = np.array(U_std)
I_std = np.array(I_std)

# Vector de tiempo en horas
time_hours = np.array([i * 0.25 for i in range(len(P_value))])

# --- Configuración con gridspec ---
fig = plt.figure(figsize=(8, 5))  # Ajusta altura según necesidad

# Crear un GridSpec: dividido en 6 filas (primera subplot usa 2 filas, las otras 4 usan 1 cada una)
gs = fig.add_gridspec(6, 1, hspace=0.3)

axs = []
# Subplot 1: P_value (ocupa 2 filas)
ax1 = fig.add_subplot(gs[0:2, 0])  # Filas 0 y 1
ax1.plot(time_hours, np.array(P_value)*100, color='blue')
ax1.set_ylabel('Active power (%)')
ax1.grid(True)
ax1.set_yticks([0, 25, 50])
ax1.set_ylim([0, 50])
axs.append(ax1)

# Subplot 2: P_std
ax2 = fig.add_subplot(gs[2, 0], sharex=ax1)
ax2.plot(time_hours, np.array(P_std)*100, color='green')
ax2.set_ylabel('$\sigma$-P (%)')
ax2.grid(True)
ax2.set_ylim([0, 0.55])
axs.append(ax2)

# Subplot 3: Q_std
ax3 = fig.add_subplot(gs[3, 0], sharex=ax1)
ax3.plot(time_hours, np.array(Q_std)*100, color='red')
ax3.set_ylabel('$\sigma$-Q (%)')
ax3.grid(True)
ax3.set_ylim([0, 0.55])
axs.append(ax3)

# Subplot 4: U_std
ax4 = fig.add_subplot(gs[4, 0], sharex=ax1)
ax4.plot(time_hours, np.array(U_std)*100, color='orange')
ax4.set_ylabel('$\sigma$-U (%)')
ax4.grid(True)
ax4.set_ylim([0.25, 0.28])
ax4.set_yticks([0.25, 0.28])
axs.append(ax4)

# Subplot 5: I_std
ax5 = fig.add_subplot(gs[5, 0], sharex=ax1)
ax5.plot(time_hours, np.array(I_std)*100, color='purple')
ax5.set_ylabel('$\sigma$-I (%)')
ax5.grid(True)
ax5.set_xlabel('Time (h)')
ax5.set_ylim([0, 0.2])
axs.append(ax5)

# --- Configurar eje X solo en el último subplot ---
xtick_positions = np.arange(0, 24, 1)
ax5.set_xticks(xtick_positions)
ax5.set_xlim(0, 23.75)

# Mostrar etiquetas solo en el último eje X
for ax in axs[:-1]:
    ax.label_outer()  # Oculta etiquetas de tick laterales (incluye xticks)

# Alinear etiquetas Y
fig.align_ylabels(axs)

# Opcional: título
# fig.suptitle('Measurements Over 24 Hours', fontsize=12)

plt.tight_layout()
plt.show()