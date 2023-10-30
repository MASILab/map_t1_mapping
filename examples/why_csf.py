# Investigate why CSF is being thresholded
import os
import t1_mapping
from t1_mapping.utils import mp2rage_t1w
import nibabel as nib
from nilearn import plotting 
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from adam_utils.nifti import plot_nifti
from scipy.interpolate import RegularGridInterpolator

# Load subject
subj = t1_mapping.mp2rage.MP2RAGESubject(
    subject_id='334264',
    scan='401-x-WIPMP2RAGE_0p7mm_1sTI_best_oneSENSE-x-WIPMP2RAGE_0p7mm_1sTI_best_oneSENSE',
    scan_times=['1010', '3310', '5610'],
    monte_carlo=os.path.join(t1_mapping.definitions.SIMULATION_DATA, 'counts_1M_spacing_full.npy'),
    all_inv_combos=True
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

# fig, ax = plot_nifti(subj.t1_map, slice=(107, 270, 260), mask=roi_mask_data, title='CSF ROI')

# Load NumPy array for counts
counts = np.load(subj.monte_carlo)
n_pairs = 3

# Calculate likelihoods
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
T = 0.5
alpha[alpha < T] = 0

# Plot alpha using max likelihood
# m = np.arange(-0.5, 0.5, subj.delta_m)
X, Y, Z = np.meshgrid(subj.m[0], subj.m[1], subj.m[2])
#fig3 = plt.figure()
#ax4 = fig3.add_subplot(projection='3d')
#ax4.plot_surface(X, Y, alpha)
#ax4.set_xlabel('MP2RAGE_1')
#ax4.set_ylabel('MP2RAGE_2')
#ax4.set_zlabel(r'$\alpha$')
#ax4.set_title(r'$\alpha$ using max likelihood')
#ax4.set_zlim([0, 1])

# Plot CSF ROIs
m1 = subj.mp2rage[0].dataobj[roi].flatten()
m2 = subj.mp2rage[1].dataobj[roi].flatten()
# alpha_csf = alpha[(np.round(m1 + 0.5) / subj.delta_m).astype(int) -1, (np.round(m2 + 0.5) / subj.delta_m).astype(int)-1]
#ax4.scatter(m1, m2, np.zeros(m1.shape), c='g')

# Save
# subj.t1_map.to_filename(os.path.join(t1_mapping.definitions.T1_MAPS_LIKELIHOOD, subj.subject_id, 't1_map.nii'))

# Create LUT
pairs = subj.pairs
t1 = subj.t1
inv = [i.get_fdata(dtype=np.complex64) for i in subj.inv]
max_L_gauss_ind = np.argmax(L_gauss, axis=-1)
t1_lut = t1[max_L_gauss_ind]
T = 0
t1_lut[alpha < T] = 0

# Create grid
interp = RegularGridInterpolator((subj.m[0], subj.m[1], subj.m[2]), values=t1_lut,
    bounds_error=False, fill_value=0, method='linear')

# Calculate MP2RAGE images to get values at
print(pairs)
t1w = [mp2rage_t1w(inv[i[0]], inv[i[1]]) for i in pairs]

# Interpolate along new values
pts = tuple([t.flatten() for t in t1w])
t1_calc = interp(pts).reshape(t1w[0].shape)
t1_calc = nib.nifti1.Nifti1Image(t1_calc, subj.affine)
fig, ax = plot_nifti(t1_calc, slice=(107, 270, 260), mask=roi_mask_data, title='CSF ROI')

# Create alpha LUT
uncertainty = alpha
interp = RegularGridInterpolator((subj.m[0], subj.m[1], subj.m[2]), values=uncertainty,
    bounds_error=False, fill_value=0, method='linear')

# Interpolate along new values
pts = tuple([t.flatten() for t in t1w])
alpha_calc = interp(pts).reshape(t1w[0].shape)
alpha_calc = nib.nifti1.Nifti1Image(alpha_calc, subj.affine)
fig, ax = plot_nifti(alpha_calc, slice=(107, 270, 260), title='Alpha values', cmap='viridis', vmin=0.8, vmax=1)


plt.show()
