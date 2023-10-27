# Investigate why CSF is being thresholded
import os
import t1_mapping
import nibabel as nib
from nilearn import plotting 
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from adam_utils.nifti import plot_nifti

# Load subject
subj = t1_mapping.mp2rage.MP2RAGESubject(
    subject_id='334264',
    scan='401-x-WIPMP2RAGE_0p7mm_1sTI_best_oneSENSE-x-WIPMP2RAGE_0p7mm_1sTI_best_oneSENSE',
    scan_times=['1010', '3310', '5610'],
    monte_carlo=os.path.join(t1_mapping.definitions.SIMULATION_DATA, 'counts_1M.npy')
)

print('Expected ranges of MP2RAGE images given these parameters: ', [(np.min(m), np.max(m)) for m in subj.m])

# Get mask
t1_truth = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 't1_maps_truth_affine', '334264', 'Warped.nii.gz'))
t1_truth_data = t1_truth.get_fdata()
mask = t1_truth_data > 0

print('Measured ranges of MP2RAGE images in brain ROI: ', [(np.min(m.get_fdata()[mask > 0]), np.max(m.get_fdata()[mask > 0])) for m in subj.mp2rage])


# Plot roi with t1 map
roi = (slice(105, 110), slice(266, 282), slice(255, 272))
roi_mask_data = np.zeros(subj.mp2rage[0].get_fdata().shape)
roi_mask_data[roi] = 1

fig, ax = plot_nifti(subj.t1_map, slice=(107, 270, 260), mask=roi_mask_data, title='CSF ROI')

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
T = 0.5
alpha[alpha < T] = 0

# Plot alpha using max likelihood
m1 = np.arange(-0.5, 0.5, subj.delta_m)
# X,Y = np.meshgrid(subj.m[0], subj.m[1])
X, Y = np.meshgrid(m1, m1)
fig3 = plt.figure()
ax4 = fig3.add_subplot(projection='3d')
ax4.plot_surface(X, Y, alpha)
ax4.set_xlabel('MP2RAGE_1')
ax4.set_ylabel('MP2RAGE_2')
ax4.set_zlabel(r'$\alpha$')
ax4.set_title(r'$\alpha$ using max likelihood')
ax4.set_zlim([0, 1])

# Plot CSF ROIs
m1 = subj.mp2rage[0].dataobj[roi].flatten()
m2 = subj.mp2rage[1].dataobj[roi].flatten()
# alpha_csf = alpha[(np.round(m1 + 0.5) / subj.delta_m).astype(int) -1, (np.round(m2 + 0.5) / subj.delta_m).astype(int)-1]
ax4.scatter(m1, m2, np.zeros(m1.shape), c='g')

# Save
subj.t1_map.to_filename(os.path.join(t1_mapping.definitions.T1_MAPS_LIKELIHOOD, subj.subject_id, 't1_map.nii'))

plt.show()