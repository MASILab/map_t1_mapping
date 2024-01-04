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
save_fig = False

fig, axes = plt.subplots(3,5, figsize=(6, 3.75))
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
    t = axes[i,0].imshow(truth_slice, 'gray', vmin=0, vmax=5)
    axes[i,1].imshow(lut_slice, 'gray', vmin=0, vmax=5)
    axes[i,2].imshow(map_slice, 'gray', vmin=0, vmax=5)
    axes[i,3].imshow(ev_slice, 'gray', vmin=0, vmax=5)
    s = axes[i,4].imshow(std_slice, 'gray', vmin=0, vmax=1)

    axes[i,0].set_axis_off()
    axes[i,1].set_axis_off()
    axes[i,2].set_axis_off()
    axes[i,3].set_axis_off()
    axes[i,4].set_axis_off()

    xlims = [[48, 207], [48, 207], [48, 207]]
    ylims = [[43, 225], [43, 235], [25, 235]]
    for j in range(5):
        axes[i,j].set_xlim(xlims[i])
        axes[i,j].set_ylim(ylims[i])
        axes[i,j].set_xticks([])
        axes[i,j].set_yticks([])
        axes[i,j].set_frame_on(False)

# Add colorbars
cbar1 = fig.colorbar(t, ax=axes[:,0:4])
cbar1.ax.set_xlabel('s')
cbar2 = fig.colorbar(s, ax=axes[:,4])
cbar2.ax.set_xlabel('s')

plt.show()

if save_fig:
    fig.savefig('/home/local/VANDERBILT/saundam1/Pictures/t1_mapping/mrm_figures/qual_results.pdf', dpi=1200)