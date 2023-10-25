# Investigate why CSF is being thresholded
import os
import t1_mapping
import nibabel as nib
from nilearn import plotting 
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Load subject
subj = t1_mapping.mp2rage.MP2RAGESubject(
    subject_id='334264',
    scan='401-x-WIPMP2RAGE_0p7mm_1sTI_best_oneSENSE-x-WIPMP2RAGE_0p7mm_1sTI_best_oneSENSE',
    scan_times=['1010', '3310', '5610'],
    monte_carlo=os.path.join(t1_mapping.definitions.SIMULATION_DATA, 'counts_100M.npy'), 
)

# Plot roi with t1 map
roi_mask_data = np.zeros(subj.mp2rage[0].get_fdata().shape)
roi_mask_data[105:110, 266:282, 252:272] = 1
roi_mask = nib.Nifti1Image(roi_mask_data, subj.affine)

fig, ax = plt.subplots()
plotting.plot_roi(roi_mask, bg_img=subj.t1_map, cut_coords=(5,5,8), radiological=True,
    axes=ax, colorbar=True, cmap='Set1')
ax.set_title('ROI')

# Load NumPy array for counts
counts = np.load(subj.monte_carlo)
n_pairs = 2

# Calculate likelihoods
L_gauss = counts / np.sum(counts *subj.delta_m**n_pairs, axis=tuple(range(n_pairs)))
L_gauss = np.nan_to_num(L_gauss, nan=0)

# Maximum likelihood of gaussian
max_L_gauss = np.max(L_gauss, axis=-1)

# Uniform likelihood
m_squares = np.array([len(mp2rage) for mp2rage in subj.m])
total_squares = np.prod(m_squares)
uni_value = 1/(total_squares*subj.delta_m**n_pairs)
L_uni = np.full(tuple(m_squares), uni_value)

# Relative likelihood
alpha = max_L_gauss / (max_L_gauss + L_uni)

# Plot alpha using max likelihood
X,Y = np.meshgrid(subj.m[0], subj.m[1])
fig3 = plt.figure()
ax4 = fig3.add_subplot(projection='3d')
ax4.plot_surface(X, Y, alpha)
ax4.set_xlabel('MP2RAGE_1')
ax4.set_ylabel('MP2RAGE_2')
ax4.set_zlabel(r'$\alpha$')
ax4.set_title(r'$\alpha$ using max likelihood')
ax4.set_zlim([0, 1])
# Save
# t1_map.to_filename(os.path.join(t1_mapping.definitions.T1_MAPS_LIKELIHOOD, subj.subject_id, 't1_map.nii'))

plt.show()