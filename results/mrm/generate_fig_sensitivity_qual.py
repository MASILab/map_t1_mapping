# Create T1 map using MP2RAGE data (3 GREs)
import os
import t1_mapping
import nibabel as nib
import numpy as np
import matplotlib.pyplot as plt
from adam_utils.nifti import load_slice
import matplotlib

matplotlib.rcParams['grid.linewidth'] = 1
matplotlib.rcParams['axes.linewidth'] = 1
matplotlib.rcParams['font.size'] = 12
save_fig = True

noise_levels = [0.0005, 0.001, 0.005, 0.01, 0.015, 0.02]
fig, axes = plt.subplots(3,len(noise_levels), figsize=(6.5, 3.75), layout='constrained')
fig2, axes2 = plt.subplots(3, len(noise_levels), figsize=(6.5, 3.75), layout='constrained')
for i, subject in enumerate(['334264', '335749', '336954']):
    # Load niftis
    truth = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 'results', 't1_maps_truth_mask', subject, f't1_map.nii.gz'))
    noisy_maps = [nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 'results', 'sensitivity', f't1_maps_likelihood_s1_2_{noise_level}_mask', subject, 't1_map.nii.gz')) for noise_level in noise_levels]

    # Calculate error NIFTIs
    error_maps = [nib.Nifti1Image(truth.get_fdata() - n.get_fdata(), truth.affine) for n in noisy_maps]

    # Load slices
    truth_slice = load_slice(truth, view=2)
    error_slices = [load_slice(e, view=2) for e in error_maps]
    noise_slice = [load_slice(n, view=2) for n in noisy_maps]

    vmin = -3
    vmax = 3
    norm = matplotlib.colors.SymLogNorm(
        linthresh=0.1,
        linscale=0.2,
        vmin=vmin,
        vmax=vmax,
    )
    # Plot slices
    for j, error_slice in enumerate(error_slices):
        t = axes[i,j].imshow(error_slice, 'RdBu', norm=norm)
        t2 = axes2[i,j].imshow(noise_slice[j], 'gray', vmin=0, vmax=5)

    for k, noise_level in enumerate(noise_levels):
        axes[0, k].set_title(f'$\sigma = {noise_level}$')
        axes2[0, k].set_title(f'$\sigma = {noise_level}$')

    xlims = [[48, 207], [48, 207], [48, 207]]
    ylims = [[43, 225], [43, 235], [25, 235]]
    ylims = [[256-y[1], 256-y[0]] for y in ylims] # account for flip
    for j in range(6):
        axes[i,j].set_xlim(xlims[i])
        axes[i,j].set_ylim(ylims[i])
        axes[i,j].set_xticks([])
        axes[i,j].set_yticks([])
        axes[i,j].set_frame_on(False)

        axes2[i,j].set_xlim(xlims[i])
        axes2[i,j].set_ylim(ylims[i])
        axes2[i,j].set_xticks([])
        axes2[i,j].set_yticks([])
        axes2[i,j].set_frame_on(False)

    _ = [a.set_axis_off() for a in axes[i,:]]
    _ = [a.set_axis_off() for a in axes2[i,:]]

# Add colorbars
# cbar1 = fig.colorbar(t, ax=axes)
# cbar1.ax.set_xlabel('s')
# cbar1.ax.set_ylabel('Error compared to ground truth')

# cbar2 = fig2.colorbar(t2, ax=axes2)
# cbar2.ax.set_xlabel('s')
# cbar2.ax.set_ylabel('$T_1$')

plt.show()

if save_fig:
    fig.savefig('/home/local/VANDERBILT/saundam1/Pictures/t1_mapping/mrm_figures/sensitivity_errors.pdf', dpi=1200, bbox_inches='tight', transparent=True)
    fig2.savefig('/home/local/VANDERBILT/saundam1/Pictures/t1_mapping/mrm_figures/sensitivity_qual.pdf', dpi=1200, bbox_inches='tight', transparent=True)