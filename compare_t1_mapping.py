# Compare LUT T1 map with ground truth
import t1_mapping
import os
import nibabel as nib
import nibabel.processing
import numpy as np
from scipy.stats import gaussian_kde
import matplotlib.pyplot as plt
import matplotlib
from nilearn.plotting import plot_anat

# Load data
subj_id = 334264
subj = t1_mapping.mp2rage.MP2RAGESubject(
    subject=str(subj_id),
    scan='401-x-WIPMP2RAGE_0p7mm_1sTI_best_oneSENSE-x-WIPMP2RAGE_0p7mm_1sTI_best_oneSENSE',
    scan_times=['1010', '3310']
)
t1_lut = subj.t1_map
t1_truth = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 't1_maps_truth_affine', str(subj_id), 'Warped.nii.gz'))

# Mask by zero values of ground truth
t1_lut_data = t1_lut.get_fdata()
t1_truth_data = t1_truth.get_fdata()
mask = t1_truth_data > 0
t1_lut_data_masked = t1_lut_data[mask > 0]
t1_truth_data_masked = t1_truth_data[mask > 0]

# Get error and ground truth arrays
ground_truth = t1_truth_data_masked
error = t1_truth_data_masked - t1_lut_data_masked

# Plot histogram
nbins = 50
fig, ax = plt.subplots(1,2)
counts, xbins, ybins, hist = ax[0].hist2d(ground_truth, error, bins=[nbins, nbins], norm='log', cmap='viridis')
ax[0].set_xlabel('Ground truth')
ax[0].set_ylabel('Error')

# Add colorbar
cbar = fig.colorbar(hist, ax=ax[0])
cbar.set_label('Count (log scale)')

# Calculate levels we want to show on contour
stop_exp = np.ceil(np.log10(counts.max())).astype(np.int64)
levels = np.logspace(0, stop_exp, stop_exp + 1)

# Plot contour (log scale)data = {
#     'Ground Truth': ground_truth,
#     'Error': error,
# }
# df = pd.DataFrame(data, columns=['Ground Truth', 'Error'])
# print(df)
# fig, ax = plt.subplots()
# kdeplot(data=df.iloc[::100], x='Ground Truth', y='Error')
log_counts = np.log(counts, out=np.zeros(counts.shape), where=(counts>0))
c = ax[1].contour(counts.T, extent=[xbins.min(), xbins.max(),ybins.min(),ybins.max()], norm='log', levels=levels, cmap='viridis')
ax[1].set_xlabel('Ground truth')
ax[1].set_ylabel('Error')

# Add colorbar (log scale)
cbar = fig.colorbar(c, ax=ax[1])
cbar.set_label('Count (log scale)')
cbar.set_ticks(levels)
tick_labels = [f'$10^{int(np.log10(p))}$' for p in levels]
cbar.set_ticklabels(tick_labels)

fig.suptitle(f'Subject {subj_id} MP2RAGE Error Density')

print(np.sum(counts*np.diff(xbins)*np.diff(ybins)))

plt.show()