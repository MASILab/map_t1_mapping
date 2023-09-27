# Plot from saved distr*.npy
import os
import t1_mapping
import nibabel as nib
from nilearn.plotting import plot_img
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import RegularGridInterpolator

# Load data
distr = np.load(os.path.join('examples', 'outputs', 'distr_50000000.npy'))
mp2rage = np.array([[-0.13,-0.11],[0.34,0.33],[0.50,-0.32]])
delta_t1 = 0.05
t1_estimate = np.arange(delta_t1, 5 + delta_t1, delta_t1)


# Plot PDF of example points
fig, ax = plt.subplots()
pts = [(50, 50), (20, 20), (5, 95)]
for idx, (i, j) in enumerate(pts):
    print(sum(distr[i,j,:]*delta_t1))
    ax.stairs(distr[i,j,:], np.append(t1_estimate, 5 + delta_t1), label=f'MP2RAGE_1={mp2rage[idx,0]:.2f}, MP2RAGE_2={mp2rage[idx,1]:.2f}')
ax.set_xlabel('T1 (s)')
ax.set_ylabel('P(T1)')
ax.set_title('PDF for several values of MP2RAGE_1 and MP2RAGE_2')
ax.legend()

plt.show()