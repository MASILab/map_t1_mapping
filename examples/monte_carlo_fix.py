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
    scan_times=['1010', '5610'], #5610
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
# Original LUT
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
ax.plot(m, t1, 'w.-', label='Original point estimate')

y = subj.t1
x = subj.m 
X,Y = np.meshgrid(subj.m,subj.t1,indexing='ij')
# Calculate posterior distribution
# counts = np.load(os.path.join(t1_mapping.definitions.SIMULATION_DATA, 'counts_test.npy'))

# For each M, normalize T1
counts = np.load(os.path.join(t1_mapping.definitions.SIMULATION_DATA, 'counts_100M_s1_3_0.0006.npy'))
posterior = counts / np.sum(counts*subj.delta_t1, axis=-1)[...,np.newaxis]

# For each M, find the T1 with the highest probability
max_inds = np.argmax(posterior, axis=-1)
x_coords = subj.m[0]
y_coords = subj.t1[max_inds]
ax.plot(x_coords, y_coords, 'g.-', label='MAP T1 using $S_{1,2}$ alone')

ax.legend()

# Monte carlo distribution density plot using pcolormesh
nonzero = np.where(posterior == 0, 1e-6, posterior)
mesh = ax.pcolormesh(X, Y, counts, cmap='viridis', norm='log')
ax.set_xlabel('$S_{1,2}$')
ax.set_ylabel('$T_1$ (s)')
# ax.plot(m[0], t1_lut, 'w.-', label='MAP T1 using $S_{1,2}$ alone')
fig.colorbar(mesh, ax=ax, label='Counts (log scale)')

# # Try plotting P(T1 | S1,2) for low values of M
# fig, ax = plt.subplots()
# ax.plot(subj.t1, posterior[7,:], 'g.-', label=f'P(T1 | S1,2) for M = {subj.m[0][7]}')
# ax.set_xlabel('$T_1$ (s)')
# ax.set_ylabel('Probability')
# ax.legend()
# ax.grid('on')

# Plot original LUT with added noise
fig, axes = plt.subplots(2,2)
fig2, ax = plt.subplots()
rng = np.random.default_rng()
for n in [0.0006, 0]:
    t1 = np.linspace(0, 5, 10000)
    GRE = t1_mapping.utils.gre_signal(
        T1=t1,
        **eqn_params
    )
    noise = rng.standard_normal(size=GRE.shape)*n #+ 1j * rng.standard_normal(size=GRE.shape)*n
    GRE = GRE + noise
    m = t1_mapping.utils.mp2rage_t1w(GRE[0,:], GRE[1,:])
    # sorted_idx = np.argsort(m)
    # m = m[sorted_idx]
    # t1 = t1[sorted_idx]

    axes[0,0].scatter(t1, GRE[0,:], label=f'Noise = {n}', s=0.5)
    axes[0,1].scatter(t1, GRE[1,:], label=f'Noise = {n}', s=0.5)
    axes[1,0].scatter(GRE[0,:], m, label=f'Noise = {n}', s=0.5)
    axes[1,1].scatter(GRE[1,:], m, label=f'Noise = {n}', s=0.5)
    ax.scatter(m, t1, label=f'Noise = {n}', s=0.5)

axes[0,0].set_xlabel('$T_1$ (s)')
axes[0,0].set_ylabel('GRE1')
axes[0,1].set_xlabel('$T_1$ (s)')
axes[0,1].set_ylabel('GRE2')
axes[1,0].set_xlabel('GRE1')
axes[1,0].set_ylabel('MP2RAGE')
axes[1,1].set_xlabel('GRE2')
axes[1,1].set_ylabel('MP2RAGE')
axes[1,1].legend()

ax.set_xlabel('MP2RAGE')
ax.set_ylabel('$T_1$ (s)')
ax.legend()

plt.show()