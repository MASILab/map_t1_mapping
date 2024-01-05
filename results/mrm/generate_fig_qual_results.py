# Create T1 map using MP2RAGE data (3 GREs)
import os
import t1_mapping
import nibabel as nib
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from adam_utils.nifti import load_slice

matplotlib.rcParams['grid.linewidth'] = 1
matplotlib.rcParams['axes.linewidth'] = 1
matplotlib.rcParams['font.size'] = 12
save_fig = True

for i, subject in enumerate(['334264', '335749', '336954']):
    # Load niftis
    truth = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 'results', 't1_maps_truth_mask', subject, f't1_map.nii.gz'))
    lut = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 'results', 't1_maps_lut_mask', subject, f't1_map.nii.gz'))
    map = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 'results', 't1_maps_likelihood_s1_2_0.005_mask', subject, f't1_map.nii.gz'))
    ev = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 'results', 'ev_maps_s1_2_0.005_mask', subject, f'ev_map.nii.gz'))
    std = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 'results', 'std_maps_s1_2_0.005_mask', subject, f'std_map.nii.gz'))

    # Load slices
    truth_slice = load_slice(truth, view=2)
    lut_slice = load_slice(lut, view=2)
    map_slice = load_slice(map, view=2)
    ev_slice = load_slice(ev, view=2)
    std_slice = load_slice(std, view=2)

    # Plot slices
    fig, ax = plt.subplots(1, 5, figsize=(5,1.25))
    t = ax[0].imshow(truth_slice, 'gray', vmin=0, vmax=5)
    ax[1].imshow(lut_slice, 'gray', vmin=0, vmax=5)
    ax[2].imshow(map_slice, 'gray', vmin=0, vmax=5)
    ax[3].imshow(ev_slice, 'gray', vmin=0, vmax=5)
    ax[4].imshow(std_slice, 'gray', vmin=0, vmax=1)

    ax[0].set_axis_off()
    ax[1].set_axis_off()
    ax[2].set_axis_off()
    ax[3].set_axis_off()
    ax[4].set_axis_off()

    xlims = [[48, 207], [48, 207], [48, 207]]
    ylims = [[43, 225], [43, 235], [25, 235]]
    for j in range(5):
        ax[j].set_xlim(xlims[i])
        ax[j].set_ylim(ylims[i])
        ax[j].set_xticks([])
        ax[j].set_yticks([])
        ax[j].set_frame_on(False)

    if save_fig:
        fig.savefig(f'/home/local/VANDERBILT/saundam1/Pictures/t1_mapping/mrm_figures/qual_results_subj{i}.pdf', dpi=1200)
# Add colorbars
# cbar1 = fig.colorbar(t, ax=axes[:,0:4])
# cbar1.ax.set_xlabel('s')
# cbar2 = fig.colorbar(s, ax=axes[:,4])
# cbar2.ax.set_xlabel('s')

fig = plt.figure(figsize=(1,4))
ax = fig.add_axes([0.25, 0.05, 0.15, 0.9])
cb = matplotlib.colorbar.ColorbarBase(ax, cmap='gray', norm=matplotlib.colors.Normalize(vmin=0, vmax=5))
if save_fig:
    fig.savefig('/home/local/VANDERBILT/saundam1/Pictures/t1_mapping/mrm_figures/qual_results_cbar1.pdf', dpi=1200)

fig = plt.figure(figsize=(1,4))
ax = fig.add_axes([0.25, 0.05, 0.15, 0.9])
cb = matplotlib.colorbar.ColorbarBase(ax, cmap='gray', norm=matplotlib.colors.Normalize(vmin=0, vmax=1))
if save_fig:
    fig.savefig('/home/local/VANDERBILT/saundam1/Pictures/t1_mapping/mrm_figures/qual_results_cbar2.pdf', dpi=1200)

plt.show()