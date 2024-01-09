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
    map_s1_2 = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 'results', 't1_maps_likelihood_s1_2_0.005_mask', subject, f't1_map.nii.gz'))
    map_s1_3 = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 'results', 't1_maps_likelihood_s1_3_0.005_mask', subject, f't1_map.nii.gz'))
    map_both = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 'results', 't1_maps_likelihood_all_0.005_mask', subject, f't1_map.nii.gz'))
    # ev = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 'results', 'ev_maps_s1_2_0.005_mask', subject, f'ev_map.nii.gz'))
    # std = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 'results', 'std_maps_s1_2_0.005_mask', subject, f'std_map.nii.gz'))

    # Load slices
    truth_slice = load_slice(truth, view=2)
    lut_slice = load_slice(lut, view=2)
    map_s1_2_slice = load_slice(map_s1_2, view=2)
    map_s1_3_slice = load_slice(map_s1_3, view=2)
    map_both_slice = load_slice(map_both, view=2)
    # std_slice = load_slice(std, view=2)

    # Plot slices
    fig, ax = plt.subplots(1, 5, figsize=(5,1.25), layout='constrained')
    t = ax[0].imshow(truth_slice, 'gray', vmin=0, vmax=5)
    ax[1].imshow(lut_slice, 'gray', vmin=0, vmax=5)
    ax[2].imshow(map_s1_2_slice, 'gray', vmin=0, vmax=5)
    ax[3].imshow(map_s1_3_slice, 'gray', vmin=0, vmax=5)
    ax[4].imshow(map_both_slice, 'gray', vmin=0, vmax=5)

    ax[0].set_axis_off()
    ax[1].set_axis_off()
    ax[2].set_axis_off()
    ax[3].set_axis_off()
    ax[4].set_axis_off()

    xlims = [[48, 207], [48, 207], [48, 207]]
    ylims = [[43, 225], [43, 235], [25, 235]]
    ylims = [[256-y[1], 256-y[0]] for y in ylims] # account for flip
    for j in range(5):
        ax[j].set_xlim(xlims[i])
        ax[j].set_ylim(ylims[i])
        ax[j].set_xticks([])
        ax[j].set_yticks([])
        ax[j].set_frame_on(False)

    if save_fig:
        fig.savefig(f'/home/local/VANDERBILT/saundam1/Pictures/t1_mapping/mrm_figures/qual_results_subj{i}.pdf', dpi=1200)

for i, subject in enumerate(['334264', '335749', '336954']):
    # Load niftis
    truth = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 'results', 't1_maps_truth_mask', subject, f't1_map.nii.gz'))
    lut = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 'results', 't1_maps_lut_mask', subject, f't1_map.nii.gz'))
    map_s1_2 = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 'results', 't1_maps_likelihood_s1_2_0.005_mask', subject, f't1_map.nii.gz'))
    map_s1_3 = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 'results', 't1_maps_likelihood_s1_3_0.005_mask', subject, f't1_map.nii.gz'))
    map_both = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 'results', 't1_maps_likelihood_all_0.005_mask', subject, f't1_map.nii.gz'))
    # ev = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 'results', 'ev_maps_s1_2_0.005_mask', subject, f'ev_map.nii.gz'))
    # std = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 'results', 'std_maps_s1_2_0.005_mask', subject, f'std_map.nii.gz'))

    lut_error = nib.Nifti1Image(truth.get_fdata() - lut.get_fdata(), truth.affine)
    map_s1_2_error = nib.Nifti1Image(truth.get_fdata() - map_s1_2.get_fdata(), truth.affine)
    map_s1_3_error = nib.Nifti1Image(truth.get_fdata() - map_s1_3.get_fdata(), truth.affine)
    map_both_error = nib.Nifti1Image(truth.get_fdata() - map_both.get_fdata(), truth.affine)

    # Load slices
    lut_slice = load_slice(lut_error, view=2)
    map_s1_2_slice = load_slice(map_s1_2_error, view=2)
    map_s1_3_slice = load_slice(map_s1_3_error, view=2)
    map_both_slice = load_slice(map_both_error, view=2)
    # std_slice = load_slice(std, view=2)

    # Symmetric log scale
    vmin = -3
    vmax = 3
    norm = matplotlib.colors.SymLogNorm(
        linthresh=0.1,
        linscale=0.2,
        vmin=vmin,
        vmax=vmax,
    )

    # Plot slices
    fig, ax = plt.subplots(1, 5, figsize=(5,1.25), layout='constrained')
    t = ax[1].imshow(lut_slice, 'RdBu', norm=norm)
    ax[2].imshow(map_s1_2_slice, 'RdBu', norm=norm)
    ax[3].imshow(map_s1_2_slice, 'RdBu', norm=norm)
    ax[4].imshow(map_both_slice, 'RdBu', norm=norm)

    ax[0].set_axis_off()
    ax[1].set_axis_off()
    ax[2].set_axis_off()
    ax[3].set_axis_off()
    ax[4].set_axis_off()

    xlims = [[48, 207], [48, 207], [48, 207]]
    ylims = [[43, 225], [43, 235], [25, 235]]
    ylims = [[256-y[1], 256-y[0]] for y in ylims] # account for flip
    for j in range(5):
        ax[j].set_xlim(xlims[i])
        ax[j].set_ylim(ylims[i])
        ax[j].set_xticks([])
        ax[j].set_yticks([])
        ax[j].set_frame_on(False)

    if save_fig:
        fig.savefig(f'/home/local/VANDERBILT/saundam1/Pictures/t1_mapping/mrm_figures/qual_error_subj{i}.pdf', dpi=1200)

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
cb = matplotlib.colorbar.ColorbarBase(ax, cmap='RdBu', norm=norm)
if save_fig:
    fig.savefig('/home/local/VANDERBILT/saundam1/Pictures/t1_mapping/mrm_figures/qual_results_cbar2.pdf', dpi=1200)

plt.show()