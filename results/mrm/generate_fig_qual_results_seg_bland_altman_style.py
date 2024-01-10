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

# Set bins
n_bins = 50
x_bins = np.linspace(1, 3, n_bins)
y_bins = np.linspace(-3, 3, n_bins)

# Loop over subjects
wm_hist = np.zeros((n_bins-1, n_bins-1))
gm_hist = np.zeros((n_bins-1, n_bins-1))
other_hist = np.zeros((n_bins-1, n_bins-1))
all_hist = np.zeros((n_bins-1, n_bins-1))
for subject in os.listdir(os.path.join(t1_mapping.definitions.OUTPUTS, 'slant_mp2rage_nss_0.25_mask')):
    print(subject) 

    # Load SLANT segmentation
    slant = nib.load(os.path.join('/nfs/masi/saundam1/outputs/t1_mapping/slant_mp2rage_nss_0.25_mask', subject, 't1w_seg.nii.gz'))

    # Load niftis
    truth = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 'results', 't1_maps_truth_mask', subject, f't1_map.nii.gz')).get_fdata()
    map = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 'results', 't1_maps_likelihood_s1_2_0.005_mask', subject, f't1_map.nii.gz')).get_fdata()

    slant_data = slant.get_fdata()
    all_mask = (slant_data > 0)
    wm_mask = (slant_data >= 40) & (slant_data <= 45) 
    other_mask = (slant_data == 208) | (slant_data == 209) | (slant_data == 51) | (slant_data == 52)
    gm_mask = np.logical_and(all_mask, np.logical_not(wm_mask | other_mask))

    wm_hist += np.histogram2d(truth[wm_mask > 0],truth[wm_mask > 0] -  map[wm_mask > 0], bins=[x_bins, y_bins])[0]
    gm_hist += np.histogram2d(truth[gm_mask > 0], truth[gm_mask > 0] - map[gm_mask > 0], bins=[x_bins, y_bins])[0]
    other_hist += np.histogram2d(truth[other_mask > 0], truth[other_mask > 0] - map[other_mask > 0], bins=[x_bins, y_bins])[0]
    all_hist += np.histogram2d(truth[all_mask > 0], truth[all_mask > 0] - map[all_mask > 0], bins=[x_bins, y_bins])[0]


fig, axes = plt.subplots(2, 2, figsize=(6, 4), layout='constrained')
titles = ['WM', 'GM', 'CSF', 'All']
for i, hist in enumerate([wm_hist, gm_hist, other_hist, all_hist]):
    # Plot histogram
    ax = axes[i // 2, i % 2]
    pcm = ax.imshow(hist.T, interpolation='nearest', cmap='viridis', norm='log', vmin=1, vmax=1e5, extent=[x_bins[-1], x_bins[0], y_bins[-1], y_bins[0]], aspect='auto')
    ax.set_xlabel('Ground Truth T1 (s)')
    ax.set_ylabel('Error (s)\nGround Truth T1 - MAP T1')
    ax.set_title(titles[i])

    # Compute mean values and standard deviations along the y-axis (difference)
    y_vals = np.sum(hist, axis=0)
    print(y_vals)
    mean_val = np.sum(y_vals * y_bins[:-1]) / np.sum(y_vals)
    std_val = np.sqrt(np.sum(y_vals * (y_bins[:-1] - mean_val)**2) / np.sum(y_vals))
    print(f'{mean_val=}, {std_val=}')

    # Plot dashed lines for +/- 1.96 standard deviations
    ax.axhline(mean_val, color='red', label='Mean')
    ax.axhline(mean_val + 1.96 * std_val, color='red', linestyle='--', label='+1.96 SD')
    ax.axhline(mean_val - 1.96 * std_val, color='red', linestyle='--', label='-1.96 SD')

cbar = fig.colorbar(pcm, ax=axes)

if save_fig:
    fig.savefig('/home/local/VANDERBILT/saundam1/Pictures/t1_mapping/mrm_figures/bland_altman_style.pdf', dpi=1200, bbox_inches='tight', transparent=True)

plt.show()

