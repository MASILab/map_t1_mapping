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
matplotlib.rcParams['grid.linewidth'] = 1
matplotlib.rcParams['axes.linewidth'] = 1
sns.set_style('ticks')
sns.set_context('paper')
save_fig = False

# Display T1 versus S1,2
subj = t1_mapping.mp2rage.MP2RAGESubject(
    subject_id='334264',
    scan='401-x-WIPMP2RAGE_0p7mm_1sTI_best_oneSENSE-x-WIPMP2RAGE_0p7mm_1sTI_best_oneSENSE',
    scan_times=['1010', '3310'],
    monte_carlo=os.path.join(t1_mapping.definitions.SIMULATION_DATA, 'counts_100M_s1_2.npy'), 
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
fig, ax = plt.subplots(figsize=(3.5, 4.2))
sns.lineplot(data=subj_data, x='S1_2', y='T1', ax=ax)
ax.set_xlabel('$S_{1,2}$')
ax.set_ylabel('$T_1$ (s)')
ax.grid(linewidth=1)

# Add dashed lines and point
x = subj_data['S1_2'].values[50]
y = subj_data['T1'].values[50]
xlims = ax.get_xlim()
ylims = ax.get_ylim()
ax.vlines(x, ylims[0], y, linestyle='dashed', color='b')
ax.hlines(y, xlims[0], x, linestyle='dashed', color='b')
ax.set_xlim(xlims)
ax.set_ylim(ylims)
ax.plot(x, y, 'b.', markersize=10)

if save_fig:
    fig.savefig('/home/saundam1/VM/shared_folder/mp2rage/MRM_figures/fig2_part1.png', dpi=600)

# Calculate posterior
n_pairs = 2
counts = np.load(subj.monte_carlo)
posterior = counts / np.sum(counts * subj.delta_t1, axis=(0,1))

# MAP estimate
map_est = np.max(posterior, axis=-1)

# Interpolate MAP estimate along S1,2 (instead of M values)
map_int = np.interp(subj_data['S1_2'].values, subj.m[0], map_est)

# Interpolate posterior along S1,2 instead of M
X,Y = np.meshgrid(subj_data['S1_2'].values, subj.t1)
points = np.concatenate((X.ravel()[:,np.newaxis], Y.ravel()[:,np.newaxis]), axis=1)
posterior_int = RegularGridInterpolator((subj.m[0], subj.t1), posterior, bounds_error=False, fill_value=0)(points)
posterior_int = posterior_int.reshape(X.shape)

# Plot 3D figure
m = subj_data['S1_2'].values
fig = plt.figure(figsize=(4.2, 4))
ax = fig.add_subplot(projection='3d')
ax.set_proj_type('ortho')
ax.plot(subj.t1, m, map_int, color='b')

for s_slice in [30, 40, 50, 60]:
    s1_2 = np.full(subj.t1.shape, m[s_slice])
    ax.plot(subj.t1, s1_2, posterior_int[s_slice], color='b')

ax.set_xlabel('$T_1$ (s)')
ax.set_ylabel('$S_{1,2}$')
ax.set_zlabel('$P(T_1 | S_{1,2})$')
ax.view_init(20, -20, 0)
ax.invert_xaxis()

plt.show()