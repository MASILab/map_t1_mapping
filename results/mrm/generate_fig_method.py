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
matplotlib.rcParams['font.size'] = 12
sns.set_style('ticks')
sns.set_context('paper')
save_fig = True
monte_carlo = '/nfs/masi/saundam1/outputs/t1_mapping/distr/counts_100M_s1_2_0.005.npy'

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
fig, ax = plt.subplots(figsize=(1.5, 1.5))
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

fig.tight_layout()
if save_fig:
    fig.savefig('/home/local/VANDERBILT/saundam1/Pictures/t1_mapping/mrm_figures/method_1.pdf', dpi=1200, bbox_inches='tight', transparent=True)

# Calculate posterior
n_pairs = 2
counts = np.load(subj.monte_carlo)
posterior = counts / np.sum(counts * subj.delta_t1, axis=-1)[:,np.newaxis]

# MAP estimate
map_est = np.max(posterior, axis=-1)
max_ind = np.argmax(posterior, axis=-1)

# Interpolate MAP estimate along S1,2 (instead of M values)
# map_int = np.interp(subj_data['S1_2'].values, subj.m[0], map_est)

# Plot 3D figure
m = subj_data['S1_2'].values
fig = plt.figure(figsize=(3,2))
ax = fig.add_subplot(projection='3d')
ax.set_proj_type('ortho')
ax.plot(subj.t1[max_ind], subj.m[0], map_est, color='k')


# Interpolate posterior along S1,2 instead of M
s1_2_points = [-0.3, -0.1, 0.1, 0.3]
X,Y = np.meshgrid(s1_2_points, subj.t1)
points = np.concatenate((X.ravel()[:,np.newaxis], Y.ravel()[:,np.newaxis]), axis=1)
posterior_int = RegularGridInterpolator((subj.m[0], subj.t1), posterior, bounds_error=False, fill_value=0)(points)
posterior_int = posterior_int.reshape(X.shape)

for s_slice in range(4):
    # Plot distribution
    s1_2 = np.full(subj.t1.shape, s1_2_points[s_slice])
    ax.plot(subj.t1, s1_2, posterior_int[:,s_slice], color='b', alpha=0.5)

    # Plot dashed line to mode
    t1_mode = subj.t1[np.argmax(posterior_int[:,s_slice])]
    ax.plot([t1_mode, t1_mode], [s1_2_points[s_slice], s1_2_points[s_slice]], [0, np.max(posterior_int[:,s_slice])], color='b', linestyle='dashed', alpha=0.5)

ax.set_xlabel('$T_1$ (s)')
ax.set_ylabel('$S_{1,2}$')
ax.set_zlabel('$P(T_1 | S_{1,2})$', labelpad=10)
ax.view_init(20, -20, 0)
ax.invert_xaxis()
# ax.set_zlim([0, 0.05])

# fig.tight_layout()
if save_fig:
    fig.savefig('/home/local/VANDERBILT/saundam1/Pictures/t1_mapping/mrm_figures/method_2.pdf', dpi=1200, bbox_inches='tight', transparent=True)

# Monte carlo distribution density plot using pcolormeshFalse
counts = np.load(subj.monte_carlo)
counts_nonzero = np.where(counts == 0, 1, counts)
fig, ax = plt.subplots(figsize=(2, 2))
m = ax.pcolormesh(subj.m[0], subj.t1, counts_nonzero, cmap='viridis', norm='log', alpha=1, antialiased=True, rasterized=True)
ax.set_xlabel('$S_{1,2}$')
ax.set_ylabel('$T_1$ (s)')
fig.colorbar(m, ax=ax, label='Counts (log scale)')

fig.tight_layout()
if save_fig:
    fig.savefig('/home/local/VANDERBILT/saundam1/Pictures/t1_mapping/mrm_figures/method_3.pdf', dpi=1200, bbox_inches='tight', transparent=True)

# Get slices of images
gre1 = subj.inv[0]
gre2 = subj.inv[1]
mp2rage = subj.mp2rage[0]
t1_map_lut = subj.t1_map('lut')
t1_map_like = subj.t1_map('likelihood', thresh=0.5)
std_map = subj.t1_std
ev_map = subj.t1_ev

gre1_real = nib.Nifti1Image(np.real(gre1.get_fdata(dtype=np.complex64)), gre1.affine, gre1.header)
gre2_real = nib.Nifti1Image(np.real(gre2.get_fdata(dtype=np.complex64)), gre2.affine, gre2.header)

# Get a slice
gre1_slice = load_slice(gre1_real, view=2)
gre2_slice = load_slice(gre2_real, view=2)
mp2rage_slice = load_slice(mp2rage, view=2)
t1_map_like_slice = load_slice(t1_map_like, view=2)
t1_map_lut_slice = load_slice(t1_map_lut, view=2)
std_map_slice = load_slice(std_map, view=2)
ev_map_slice = load_slice(ev_map, view=2)

gre1_slice_sag = load_slice(gre1_real, view=0)
gre2_slice_sag = load_slice(gre2_real, view=0)

# Plot slices and save
fig, ax = plt.subplots(figsize=(1.5, 1.5))
ax.imshow(gre1_slice, cmap='gray')
ax.set_axis_off()
fig.tight_layout()
if save_fig:
    fig.savefig('/home/local/VANDERBILT/saundam1/Pictures/t1_mapping/mrm_figures/method_gre1.pdf', dpi=1200, bbox_inches='tight', transparent=True)

fig, ax = plt.subplots(figsize=(1.5, 1.5))
ax.imshow(gre2_slice, cmap='gray')
ax.set_axis_off()
fig.tight_layout()
if save_fig:
    fig.savefig('/home/local/VANDERBILT/saundam1/Pictures/t1_mapping/mrm_figures/method_gre2.pdf', dpi=1200, bbox_inches='tight', transparent=True)

fig, ax = plt.subplots(figsize=(1.5, 1.5))
ax.imshow(mp2rage_slice, cmap='gray')
ax.set_axis_off()
fig.tight_layout()
if save_fig:
    fig.savefig('/home/local/VANDERBILT/saundam1/Pictures/t1_mapping/mrm_figures/method_mp2rage.pdf', dpi=1200, bbox_inches='tight', transparent=True)

fig, ax = plt.subplots(figsize=(1.5, 1.5))
ax.imshow(t1_map_like_slice, cmap='gray')
ax.set_axis_off()
fig.tight_layout()
if save_fig:
    fig.savefig('/home/local/VANDERBILT/saundam1/Pictures/t1_mapping/mrm_figures/method_t1_like.pdf', dpi=1200, bbox_inches='tight', transparent=True)

fig, ax = plt.subplots(figsize=(1.5, 1.5))
ax.imshow(t1_map_lut_slice, cmap='gray')
ax.set_axis_off()
fig.tight_layout()
if save_fig:
    fig.savefig('/home/local/VANDERBILT/saundam1/Pictures/t1_mapping/mrm_figures/method_t1_lut.pdf', dpi=1200, bbox_inches='tight', transparent=True)

fig, ax = plt.subplots(figsize=(1.5, 1.5))
ax.imshow(std_map_slice, cmap='gray')
ax.set_axis_off()
fig.tight_layout()
if save_fig:
    fig.savefig('/home/local/VANDERBILT/saundam1/Pictures/t1_mapping/mrm_figures/method_std.pdf', dpi=1200, bbox_inches='tight', transparent=True)

fig, ax = plt.subplots(figsize=(1.5, 1.5))
ax.imshow(ev_map_slice, cmap='gray')
ax.set_axis_off()
fig.tight_layout()
if save_fig:
    fig.savefig('/home/local/VANDERBILT/saundam1/Pictures/t1_mapping/mrm_figures/method_ev.pdf', dpi=1200, bbox_inches='tight', transparent=True)

fig, ax = plt.subplots(figsize=(1.5, 1.5))
ax.imshow(gre1_slice_sag, cmap='gray')
ax.set_axis_off()
fig.tight_layout()
if save_fig:
    fig.savefig('/home/local/VANDERBILT/saundam1/Pictures/t1_mapping/mrm_figures/method_gre1_sag.pdf', dpi=1200, bbox_inches='tight', transparent=True)

fig, ax = plt.subplots(figsize=(1.5, 1.5))
ax.imshow(gre2_slice_sag, cmap='gray')
ax.set_axis_off()
fig.tight_layout()
if save_fig:
    fig.savefig('/home/local/VANDERBILT/saundam1/Pictures/t1_mapping/mrm_figures/method_gre2_sag.pdf', dpi=1200, bbox_inches='tight', transparent=True)


plt.show()