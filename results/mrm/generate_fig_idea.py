# Generate figure 2: idea
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
from scipy.spatial.distance import cdist

# Seaborn and matplotlib defaults
matplotlib.rcParams['grid.linewidth'] = 1
matplotlib.rcParams['axes.linewidth'] = 1
matplotlib.rcParams['font.size'] = 12
sns.set_style('ticks')
sns.set_context('paper')
save_fig = True

# Display T1 versus S1,2

# GRE = t1_mapping.utils.gre_signal(
#     T1=subj.t1,
#     **subj.eqn_params
# )

# subj_data = pd.DataFrame({
#     'T1': subj.t1,
#     'S1_2': t1_mapping.utils.mp2rage_t1w(GRE[0,:], GRE[1,:])
# })

# # Plot T1 versus S1,2
# fig, ax = plt.subplots(figsize=(3, 4.2), layout='constrained')
# sns.lineplot(data=subj_data, x='S1_2', y='T1', ax=ax, color='k')
# ax.set_xlabel('$S_{1,2}$')
# ax.set_ylabel('$T_1$ (s)')
# ax.grid(linewidth=1)

# # Add dashed lines and point at -0.2
# x = -0.2
# y = np.interp(x, subj_data['S1_2'].values[::-1], subj_data['T1'].values[::-1])

# # x = subj_data['S1_2'].values[50]
# # y = subj_data['T1'].values[50]
# xlims = ax.get_xlim()
# ylims = ax.get_ylim()
# ax.vlines(x, ylims[0], y, linestyle='dashed', color=[0,0,1])
# ax.hlines(y, xlims[0], x, linestyle='dashed', color=[0,0,1])
# ax.set_xlim(xlims)
# ax.set_ylim(ylims)
# ax.plot(x, y, 'b.', markersize=10)
# ax.set_title('Point estimate of $T_1$ given $S_{1,2}$')

# if save_fig:
#     fig.savefig('/home/local/VANDERBILT/saundam1/Pictures/t1_mapping/mrm_figures/idea_1.pdf', dpi=1200, bbox_inches='tight')

# Display T1 versus S1,2 and S1,3
subj = t1_mapping.mp2rage.MP2RAGESubject(
    subject_id='334264',
    scan='401-x-WIPMP2RAGE_0p7mm_1sTI_best_oneSENSE-x-WIPMP2RAGE_0p7mm_1sTI_best_oneSENSE',
    scan_times=['1010', '3310', '5610'],
    monte_carlo=os.path.join(t1_mapping.definitions.SIMULATION_DATA, 'counts_100M_all_0.005.npy'), 
    all_inv_combos=False,
)

GRE = t1_mapping.utils.gre_signal(
    T1=subj.t1,
    **subj.eqn_params
)

subj_data = pd.DataFrame({
    'T1': subj.t1,
    'S1_2': t1_mapping.utils.mp2rage_t1w(GRE[0,:], GRE[1,:]),
    'S1_3': t1_mapping.utils.mp2rage_t1w(GRE[0,:], GRE[2,:])
})

# Create LUT
counts = np.load(subj.monte_carlo)
n_pairs = len(subj.pairs)
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
likelihood_thresh = 0.5
t1_lut[alpha < likelihood_thresh] = 0
interp = RegularGridInterpolator(tuple(subj.m), values=t1_lut,
    bounds_error=False, fill_value=0, method='linear')
t1_lut[alpha < likelihood_thresh] = np.nan
X, Y = np.meshgrid(subj.m[0], subj.m[1], indexing='ij')

# Plot T1 versus S1,2 and S1,3
m1 = subj_data['S1_2'].values
m2 = subj_data['S1_3'].values
fig = plt.figure(figsize=(3.25, 4), layout='constrained')
ax = fig.add_subplot(projection='3d')
# ax.plot(m1, m2, subj.t1, color='b')
ax.plot_surface(X, Y, t1_lut, cmap='viridis', edgecolor='none', alpha=0.75)
ax.set_xlabel('$S_{1,2}$')
ax.set_ylabel('$S_{1,3}$')
ax.set_zlabel('$T_1$ (s)')

t1w1 = subj.mp2rage[0].get_fdata()
t1w2 = subj.mp2rage[1].get_fdata()
indx = np.arange(0, len(t1w1.flatten()), 50000)
ax.scatter(t1w1.flatten()[indx], t1w2.flatten()[indx], zdir='z', color=[0,1,0,0.2], label='Sample unknown values')
ax.legend()
ax.set_title('Multiple MP2RAGE signals')

# Add dashed lines and point 
pt = np.array([-0.35, -0.3])[:,np.newaxis]
nodes = np.array([t1w1.flatten()[indx], t1w2.flatten()[indx]])
print(pt.shape, nodes.shape)
closest_ind = cdist(pt.T, nodes.T).argmin()
x = t1w1.flatten()[indx][closest_ind]
y = t1w2.flatten()[indx][closest_ind]
z = interp((x,y))
xlims = ax.get_xlim()
ylims = ax.get_ylim()
zlims = ax.get_zlim()
ax.plot(x,y,z, 'b.')
ax.plot([x, xlims[1]], [y,y], [zlims[0],zlims[0]], 'b--', linewidth=1)
ax.plot([x,x], [ylims[0],y], [zlims[0],zlims[0]], 'b--', linewidth=1)
ax.plot([x,x], [y,y], [zlims[0],z], 'b--', linewidth=1)
ax.set_xlim(xlims)
ax.set_ylim(ylims)
ax.set_zlim(zlims)
fig.tight_layout()

if save_fig:
    fig.savefig('/home/local/VANDERBILT/saundam1/Pictures/t1_mapping/mrm_figures/idea_1.pdf', dpi=1200)

# Calculate posterior for 3D distribution figure
subj = t1_mapping.mp2rage.MP2RAGESubject(
    subject_id='334264',
    scan='401-x-WIPMP2RAGE_0p7mm_1sTI_best_oneSENSE-x-WIPMP2RAGE_0p7mm_1sTI_best_oneSENSE',
    scan_times=['1010', '3310'],
    monte_carlo=os.path.join(t1_mapping.definitions.SIMULATION_DATA, 'counts_100M_s1_2_0.005.npy'), 
    all_inv_combos=False,
)

n_pairs = 2
counts = np.load(subj.monte_carlo)
posterior = counts / np.sum(counts * subj.delta_t1, axis=1)[...,np.newaxis]

# MAP estimate
max_ind = np.argmax(posterior, axis=-1)
map_est = np.max(posterior, axis=-1)

# Plot 3D figure
fig = plt.figure(figsize=(3.25, 4))
ax = fig.add_subplot(projection='3d')
ax.set_proj_type('ortho')
X, Y = np.meshgrid(subj.t1, subj.m[0])
ax.plot(subj.t1[max_ind], subj.m[0], map_est, color='k')

# Also plot original LUT and surface
# ax.plot_surface(X, Y, posterior, cmap='viridis', edgecolor='no
# ax.plot(subj.t1, t1_mapping.utils.mp2rage_t1w(GRE[0,:], GRE[1,:]), 0, color='k')ne', alpha=0.25)

# Plot probability density functions at certain points along S1_2
s1_2_points = [-0.3, -0.1, 0.1, 0.3]


X,Y = np.meshgrid(s1_2_points, subj.t1)
points = np.concatenate((X.ravel()[:,np.newaxis], Y.ravel()[:,np.newaxis]), axis=1)
posterior_int = RegularGridInterpolator((subj.m[0], subj.t1), posterior, bounds_error=False, fill_value=0)(points)
posterior_int = posterior_int.reshape(X.shape)

for s_slice in range(len(s1_2_points)):
    # Plot distribution
    s1_2 = np.full(subj.t1.shape, s1_2_points[s_slice])
    ax.plot(subj.t1, s1_2, posterior_int[:,s_slice], color='b')

    # Plot dashed line to mode
    t1_mode = subj.t1[np.argmax(posterior_int[:,s_slice])]
    ax.plot([t1_mode, t1_mode], [s1_2_points[s_slice], s1_2_points[s_slice]], [0, np.max(posterior_int[:,s_slice])], color='b', linestyle='dashed')
    
    if s1_2_points[s_slice] == -0.3:
        ax.plot(t1_mode, s1_2_points[s_slice], np.max(posterior_int[:,s_slice]), 'b.', markersize=10)
        ylims = ax.get_ylim()
        ax.plot([t1_mode, t1_mode], [s1_2_points[s_slice], ylims[0]], [0, 0], color=[0,0,1], linestyle='dashed')
        ax.plot([t1_mode, 0], [s1_2_points[s_slice], s1_2_points[s_slice]], [0, 0], color=[0,0,1], linestyle='dashed')

        ax.set_ylim(ylims)

ax.set_xlabel('$T_1$ (s)')
ax.set_ylabel('$S_{1,2}$')
ax.set_zlabel('$P(T_1 | S_{1,2})$')
ax.view_init(20, -25, 0)
ax.invert_xaxis()
# ax.set_zlim([0, 0.05])
ax.set_title('Posterior distribution $P(T_1 | S_{1,2})$')

if save_fig:
    fig.savefig('/home/local/VANDERBILT/saundam1/Pictures/t1_mapping/mrm_figures/idea_2.pdf', dpi=1200, bbox_inches='tight')

plt.show()