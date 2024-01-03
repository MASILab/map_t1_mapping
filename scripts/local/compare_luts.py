# Run Monte Carlo with no noise to see how it affects results compared to LUT
# Compare lookup tables
import numpy as np
import matplotlib.pyplot as plt
import t1_mapping
import nibabel as nib
import os
import pandas as pd

acq_params : t1_mapping.utils.MP2RAGEParameters = {
    "MP2RAGE_TR": 8.25,
    "TR": 0.006,
    "flip_angles": [4.0, 4.0],
    "inversion_times": [1010/1000, 3310/1000],
    "n": [225],
    "eff": 0.84,
}
delta_t1 = 0.05
t1=np.arange(delta_t1, 5 + delta_t1, delta_t1)

# Set equation parameters
eqn_params = t1_mapping.utils.acq_to_eqn_params(acq_params)
GRE = t1_mapping.utils.gre_signal(
    T1=t1,
    **eqn_params
)
m = t1_mapping.utils.mp2rage_t1w(GRE[0,:], GRE[1,:])
sorted_idx = np.argsort(m)
m = m[sorted_idx]
t1 = t1[sorted_idx]

# Pad LUT
m[0] = -0.5
m[-1] = 0.5

# Plot regular LUT
fig, ax = plt.subplots()
ax.plot(m, t1, 'k.-', label='Original point estimate')

t1 = np.arange(delta_t1, 5+delta_t1, delta_t1)
m = np.linspace(-0.5, 0.5, 100)
counts = np.load('/home/saundam1/temp_data/distr/counts_100M_s1_2_0.0006.npy')
posterior = counts / np.sum(counts*delta_t1, axis=-1)[...,np.newaxis]
max_inds = np.argmax(posterior, axis=-1)
t1_vals = t1[max_inds]
ax.plot(m, t1_vals, 'g.-', label='MAP T1 using $S_{1,2}$ alone')

# Monte carlo distribution density plot using pcolormesh
X, Y = np.meshgrid(m, t1, indexing='ij')
nonzero = np.where(posterior == 0, 1e-6, posterior)
mesh = ax.pcolormesh(X, Y, nonzero, cmap='viridis', norm='log')
plt.colorbar(mesh, label='P(T1 | S_1,2) (log scale)')

ax.legend()
ax.grid('on')
plt.show()