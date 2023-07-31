# Simple plot to show the relationship between the two gradient echos sequences
# Some code generated using ChatGPT

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Sample data for the 3D surface
GRE1 = np.linspace(-50, 50, 200)
GRE2 = np.linspace(-50, 50, 200)
GRE1, GRE2 = np.meshgrid(GRE1, GRE2)
MP2RAGE = (GRE1*GRE2)/(GRE1**2 + GRE2**2)

# Create a 3D plot
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Plot the 3D surface
surf = ax.plot_surface(GRE1, GRE2, MP2RAGE, cmap='viridis')

# Set labels for the axes
ax.set_xlabel('GRE$_{TI1}$')
ax.set_ylabel('GRE$_{TI2}$')
ax.set_zlabel('MP2RAGE')

# Add a color bar to show the scale
fig.colorbar(surf)

# Show the plot
plt.show()
