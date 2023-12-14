# Run Monte Carlo with no noise to see how it affects results compared to LUT
# Compare lookup tables
import numpy as np
import matplotlib.pyplot as plt
import t1_mapping
import nibabel as nib
import os
import pandas as pd

# Load equation parameters
subj = t1_mapping.mp2rage.MP2RAGESubject(
    subject_id='334264',
    scan='401-x-WIPMP2RAGE_0p7mm_1sTI_best_oneSENSE-x-WIPMP2RAGE_0p7mm_1sTI_best_oneSENSE',
    scan_times=['1010', '3310'], #5610
    all_inv_combos=False
)
eqn_params = subj.eqn_params
t1 = subj.t1
delta_t1 = subj.delta_t1
m = subj.m 
delta_m = subj.delta_m
pairs = subj.pairs
m_ranges = subj.m_ranges

fig, ax = plt.subplots()

counts = np.zeros((len(subj.m[0]), len(subj.t1)))
m = subj.m[0]
for i in range(1000):
    # Get original point estimate LUT
    GRE = t1_mapping.utils.gre_signal(
        T1=t1,
        **eqn_params
    )
    # Add complex-valued Gaussian noise
    GRE = GRE.astype(np.complex64)
    GRE += np.random.normal(0, 0.005, GRE.shape) + 1j*np.random.normal(0, 0.005, GRE.shape)

    m_iter = t1_mapping.utils.mp2rage_t1w(GRE[0,:], GRE[1,:])

    dist = np.abs(m[:,np.newaxis] - m_iter)
    m_idx = np.argmin(dist, axis=0)
    t1_idx = np.arange(len(t1))

    # Add to counts
    counts[m_idx, t1_idx] += 1
    # ax.plot(m_iter, t1, 'g.')

# Original LUT
GRE = t1_mapping.utils.gre_signal(
    T1=t1,
    **eqn_params
)
print(np.min(GRE[0,:]), np.max(GRE[0,:]), np.mean(GRE[0,:]), np.std(GRE[0,:]))
m = t1_mapping.utils.mp2rage_t1w(GRE[0,:], GRE[1,:])
sorted_idx = np.argsort(m)
m = m[sorted_idx]
t1 = t1[sorted_idx]

# Pad LUT
m[0] = -0.5
m[-1] = 0.5

# Plot regular LUT
ax.plot(m, t1, 'w.-', label='Original point estimate')

y = subj.t1
x = subj.m 
X,Y = np.meshgrid(subj.m,subj.t1,indexing='ij')
# Calculate posterior distribution
# counts = np.load(os.path.join(t1_mapping.definitions.SIMULATION_DATA, 'counts_test.npy'))

# For each M, normalize T1
counts = np.load(os.path.join(t1_mapping.definitions.SIMULATION_DATA, 'counts_100M_s1_2.npy'))
posterior = counts / np.sum(counts*subj.delta_t1, axis=-1)[:,np.newaxis]

# For each M, find the T1 with the highest probability
max_inds = np.argmax(posterior, axis=-1)
# x_coords = X[max_inds, np.arange(counts.shape[0])]
# y_coords = Y[max_inds, np.arange(counts.shape[0])]
x_coords = subj.m[0]
y_coords = subj.t1[max_inds]

# max_inds = np.argmax(posterior, axis=0)
# max_vals = np.max(posterior, axis=0)

# Get the x and y coordinates of the maximum values
# x_coords = X[max_inds, np.arange(counts.shape[-1])]
# y_coords = Y[max_inds, np.arange(counts.shape[-1])]
ax.plot(x_coords, y_coords, 'g.-', label='MAP T1 using $S_{1,2}$ alone')

# Monte carlo distribution density plot using pcolormesh
nonzero = np.where(posterior == 0, 1e-6, posterior)
mesh = ax.pcolormesh(X, Y, nonzero, cmap='viridis', norm='log')
ax.set_xlabel('$S_{1,2}$')
ax.set_ylabel('$T_1$ (s)')
# ax.plot(m[0], t1_lut, 'w.-', label='MAP T1 using $S_{1,2}$ alone')
fig.colorbar(mesh, ax=ax, label='P(T1 | S_1,2) (log scale)')


ax.legend()
ax.grid('on')
plt.show()
plt.pause(1)