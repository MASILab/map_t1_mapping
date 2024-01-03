# Plot 2D histogram of Monte Carlo simulation
import os
import t1_mapping
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

delta_t1 = 0.05
t1 = np.arange(delta_t1, 5+delta_t1, delta_t1)

num_points = t1.shape[0]
m = np.linspace(-0.5, 0.5, num_points)
delta_m = (0.5 - (-0.5))/(num_points-1)

# Load Monte Carlo simulation
X,Y = np.meshgrid(m, t1)
counts = np.load(os.path.join(t1_mapping.definitions.SIMULATION_DATA, 'counts_100M_s1_3_0.0006.npy'))
counts_nonzero = np.where(counts == 0, 1, counts)

# Create histogram 
fig, ax = plt.subplots(figsize=(6.5,4))
m = ax.pcolormesh(m, t1, counts_nonzero, cmap='viridis', norm='log')
ax.set_xlabel('$S_{1,2}$')
ax.set_ylabel('$T_1$ (s)')
ax.set_title('Monte Carlo counts')
fig.colorbar(m, ax=ax, label='Counts (log scale)')

plt.show()