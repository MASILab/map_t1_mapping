# Generate figure 1: problem
import os
import t1_mapping
import nibabel as nib
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib
import pandas as pd
from adam_utils.nifti import load_slice
from scipy.interpolate import RegularGridInterpolator, interpn

# Seaborn and matplotlib defaults
sns.set_style('ticks')
sns.set_context('paper')
matplotlib.rcParams['grid.linewidth'] = 1
matplotlib.rcParams['axes.linewidth'] = 1
plt.rcParams['axes.labelsize'] = 14
plt.rcParams['xtick.labelsize'] = 14
plt.rcParams['ytick.labelsize'] = 14
save_fig = False
monte_carlo = '/nfs/masi/saundam1/outputs/t1_mapping/distr/counts_100M_s1_2_0.0006.npy'

# Display T1 versus S1,2
subj = t1_mapping.mp2rage.MP2RAGESubject(
    subject_id='334264',
    scan='401-x-WIPMP2RAGE_0p7mm_1sTI_best_oneSENSE-x-WIPMP2RAGE_0p7mm_1sTI_best_oneSENSE',
    scan_times=['1010', '3310'],
    monte_carlo=monte_carlo, 
    all_inv_combos=False,
)

GRE = t1_mapping.utils.gre_signal(
    T1=subj.t1,
    **subj.eqn_params
)

subj_data = pd.DataFrame({
    'T1': subj.t1,
    'S1_2': t1_mapping.utils.mp2rage_t1w(GRE[0,:], GRE[1,:])
})

# Plot T1 versus S1,2
fig, ax = plt.subplots(figsize=(3, 4.2), layout='constrained')
sns.lineplot(data=subj_data, x='S1_2', y='T1', ax=ax, color='k')
ax.set_xlabel('$S_{1,2}$')
ax.set_ylabel('$T_1$ (s)')
ax.grid(linewidth=1)

# Add dashed lines and point at -0.2
x = -0.2
y = np.interp(x, subj_data['S1_2'].values[::-1], subj_data['T1'].values[::-1])

# x = subj_data['S1_2'].values[50]
# y = subj_data['T1'].values[50]
xlims = ax.get_xlim()
ylims = ax.get_ylim()
ax.vlines(x, ylims[0], y, linestyle='dashed', color='b')
ax.hlines(y, xlims[0], x, linestyle='dashed', color='b')
ax.set_xlim(xlims)
ax.set_ylim(ylims)
ax.plot(x, y, 'b.', markersize=10)

if save_fig:
    fig.savefig('/home/saundam1/VM/shared_folder/mp2rage/MRM_figures/example_screenshots/eqn_lut.png', dpi=600)

# Calculate posterior
n_pairs = 2
counts = np.load(subj.monte_carlo)
posterior = counts / np.sum(counts * subj.delta_t1, axis=-1)[:,np.newaxis]

# MAP estimate
map_est = np.max(posterior, axis=-1)

# Interpolate MAP estimate along S1,2 (instead of M values)
map_int = np.interp(subj_data['S1_2'].values, subj.m[0], map_est)

# Plot 3D figure
m = subj_data['S1_2'].values
fig = plt.figure(figsize=(5,4), layout='constrained')
ax = fig.add_subplot(projection='3d')
ax.set_proj_type('ortho')
ax.plot(subj.t1, m, map_int, color='k')


# Interpolate posterior along S1,2 instead of M
s1_2_points = [-0.4, -0.2, 0, 0.2, 0.4]
X,Y = np.meshgrid(s1_2_points, subj.t1)
points = np.concatenate((X.ravel()[:,np.newaxis], Y.ravel()[:,np.newaxis]), axis=1)
posterior_int = RegularGridInterpolator((subj.m[0], subj.t1), posterior, bounds_error=False, fill_value=0)(points)
posterior_int = posterior_int.reshape(X.shape)

for s_slice in range(5):
    # Plot distribution
    s1_2 = np.full(subj.t1.shape, s1_2_points[s_slice])
    ax.plot(subj.t1, s1_2, posterior_int[:,s_slice], color='b', alpha=0.5)

    # Plot dashed line to mode
    t1_mode = subj.t1[np.argmax(posterior_int[:,s_slice])]
    ax.plot([t1_mode, t1_mode], [s1_2_points[s_slice], s1_2_points[s_slice]], [0, np.max(posterior_int[:,s_slice])], color='b', linestyle='dashed', alpha=0.5)
    
    if s1_2_points[s_slice] == -0.2:
        ax.plot(t1_mode, s1_2_points[s_slice], np.max(posterior_int[:,s_slice]), 'b.', markersize=10)
        ylims = ax.get_ylim()
        ax.plot([t1_mode, t1_mode], [s1_2_points[s_slice], ylims[0]], [0, 0], color='b', linestyle='dashed')
        ax.plot([t1_mode, 0], [s1_2_points[s_slice], s1_2_points[s_slice]], [0, 0], color='b', linestyle='dashed')

        ax.set_ylim(ylims)

ax.set_xlabel('$T_1$ (s)')
ax.set_ylabel('$S_{1,2}$')
ax.set_zlabel('$P(T_1 | S_{1,2})$', labelpad=10)
ax.view_init(20, -20, 0)
ax.invert_xaxis()
# ax.set_zlim([0, 0.05])

if save_fig:
    fig.savefig('/home/saundam1/VM/shared_folder/mp2rage/MRM_figures/example_screenshots/posterior.png', dpi=600)

# Monte carlo distribution density plot using pcolormesh
counts = np.load(subj.monte_carlo)
counts_nonzero = np.where(counts == 0, 1, counts)
fig, ax = plt.subplots(figsize=(3.8, 3), layout='constrained')
m = ax.pcolormesh(subj.m[0], subj.t1, counts_nonzero, cmap='viridis', norm='log')
ax.set_xlabel('$S_{1,2}$')
ax.set_ylabel('$T_1$ (s)')
fig.colorbar(m, ax=ax, label='Counts (log scale)')

if save_fig:
    fig.savefig('/home/saundam1/VM/shared_folder/mp2rage/MRM_figures/example_screenshots/monte_carlo.png', dpi=600)

plt.show()
