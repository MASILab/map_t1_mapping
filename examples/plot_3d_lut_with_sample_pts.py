# Plot 3D LUT with some example T1w points
import numpy as np
import matplotlib.pyplot as plt
import t1_mapping
import nibabel as nib
import os
import pandas as pd
from adam_utils.nifti import plot_nifti

# Load equation parameters
monte_carlo=os.path.join(t1_mapping.definitions.SIMULATION_DATA, 'counts_100M_all_0.001.npy')
subj = t1_mapping.mp2rage.MP2RAGESubject(
    subject_id='334264',
    scan='401-x-WIPMP2RAGE_0p7mm_1sTI_best_oneSENSE-x-WIPMP2RAGE_0p7mm_1sTI_best_oneSENSE',
    scan_times=['1010', '3310', '5610'],
    all_inv_combos=False,
    monte_carlo=monte_carlo,
)

counts = np.load(monte_carlo)
posterior = counts / np.sum(counts*subj.delta_t1, axis=-1)
max_inds = np.argmax(posterior, axis=-1)
x_coords = subj.m[0]
y_coords = subj.t1[max_inds]

n_pairs = len(subj.pairs)
n_readouts = len(subj.inv)
print(f'Number of pairs: {n_pairs}, number of readouts: {n_readouts}')

# Calculate likelihoods
L_gauss = counts / np.sum(counts * np.prod(subj.delta_m), axis=tuple(range(n_pairs)))
L_gauss = np.nan_to_num(L_gauss, nan=0)

# Maximum likelihood of gaussian
max_L_gauss = np.max(L_gauss, axis=-1)

# Uniform likelihood
total_vol = np.prod(m[1]-m[0] for m in subj.m_ranges)
m_squares = np.array([len(mp2rage) for mp2rage in subj.m])
total_squares = np.prod(m_squares)
uni_value = 1/(total_squares*np.prod(subj.delta_m))
L_uni = np.full(tuple(m_squares), uni_value)

# Relative likelihood
alpha = max_L_gauss / (max_L_gauss + L_uni)

# Create LUT
max_L_gauss_ind = np.argmax(L_gauss, axis=-1)
t1_lut = subj.t1[max_L_gauss_ind]
likelihood_thresh = 0.
t1_lut[alpha < likelihood_thresh] = 0

# Create grid
print(t1_lut)
fig, ax = plt.subplots()
# ax.plot(x_coords, y_coords, 'g.-', label='MAP T1 using $S_{1,2}$ alone')

# Monte carlo distribution density plot using pcolormesh
X, Y = np.meshgrid(subj.m[0], subj.m[1], indexing='ij')
nonzero = np.where(posterior == 0, 1e-6, posterior)
mesh = ax.pcolormesh(X, Y, t1_lut, cmap='viridis')
ax.set_xlabel('$S_{1,2}$')
ax.set_ylabel('$S_{1,3}$')
fig.colorbar(mesh, ax=ax, label='T1 (s)')

# Plot example points
t1w1 = subj.mp2rage[0].get_fdata().flatten()
t1w2 = subj.mp2rage[1].get_fdata().flatten()
ind = np.arange(0, len(t1w1), 50000)
ax.scatter(t1w1[ind], t1w2[ind], c='r', marker='x', label='Example T1w points')

# Plot example LUTs
acq_params_s1_2 = subj.acq_params
acq_params_s1_2['flip_angles'] = [4,4]
acq_params_s1_2['inversion_times'] = subj.acq_params['inversion_times'][0:2]
eqn_params_s1_2 = t1_mapping.utils.acq_to_eqn_params(acq_params_s1_2)
acq_params_s1_3 = subj.acq_params
acq_params_s1_3['flip_angles'] = [4,4]
acq_params_s1_2['inversion_times'] = [subj.acq_params['inversion_times'][0], subj.acq_params['inversion_times'][2]]
eqn_params_s1_3 = t1_mapping.utils.acq_to_eqn_params(acq_params_s1_3)

GRE = t1_mapping.utils.gre_signal(
    T1=subj.t1,
    **eqn_params_s1_2
)
m_s1_2 = t1_mapping.utils.mp2rage_t1w(GRE[0,:], GRE[1,:])
sorted_idx = np.argsort(m_s1_2)
m_s1_2 = m_s1_2[sorted_idx]
t1_lut_s1_2 = subj.t1[sorted_idx]

GRE = t1_mapping.utils.gre_signal(
    T1=subj.t1,
    **eqn_params_s1_3
)
m_s1_3 = t1_mapping.utils.mp2rage_t1w(GRE[0,:], GRE[1,:])
sorted_idx = np.argsort(m_s1_3)
m_s1_3 = m_s1_3[sorted_idx]
t1_lut_s1_3 = subj.t1[sorted_idx]

fig, ax = plt.subplots(1,2)
ax[0].plot(m_s1_2, t1_lut_s1_2, 'k.-', label='Lookup Table')
ax[0].plot(subj.m[0], t1_lut[:, 0], label=f'$S_{1,2}$={subj.m[1][0]}')
ax[0].plot(subj.m[0], t1_lut[:, 20], label=f'$S_{1,2}$={subj.m[1][20]}')
ax[0].plot(subj.m[0], t1_lut[:, 40], label=f'$S_{1,2}$={subj.m[1][40]}')
ax[0].plot(subj.m[0], t1_lut[:, 60], label=f'$S_{1,2}$={subj.m[1][60]}')
ax[0].plot(subj.m[0], t1_lut[:, 80], label=f'$S_{1,2}$={subj.m[1][80]}')

ax[0].set_xlabel('$S_{1,2}$')
ax[0].set_ylabel('$T_1$ (s)')

ax[1].plot(m_s1_3, t1_lut_s1_3, 'k.-', label='Lookup Table')
ax[1].plot(subj.m[1], t1_lut[0,:], label=f'$S_{1,3}$={subj.m[0][0]}')
ax[1].plot(subj.m[1], t1_lut[20,:], label=f'$S_{1,3}$={subj.m[0][20]}')
ax[1].plot(subj.m[1], t1_lut[40,:], label=f'$S_{1,3}$={subj.m[0][40]}')
ax[1].plot(subj.m[1], t1_lut[60,:], label=f'$S_{1,3}$={subj.m[0][60]}')
ax[1].plot(subj.m[1], t1_lut[80,:], label=f'$S_{1,3}$={subj.m[0][80]}')

ax[1].set_xlabel('$S_{1,3}$')
ax[1].set_ylabel('$T_1$ (s)')

ax[0].legend()
ax[1].legend()

plt.show()
