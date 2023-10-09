# Load ground truth
import t1_mapping
import os
import numpy as np
import nibabel as nib
from nilearn.plotting import plot_anat
from scipy.io import loadmat
import matplotlib.pyplot as plt

# Load data
subj_id = 334317
subj_path = os.path.join(t1_mapping.definitions.GROUND_TRUTH, f'filteredData_{subj_id}.mat')
subj = loadmat(subj_path, variable_names=['R1fs', 'MD_SIR'])

# Calculate affine
spacing = np.squeeze(subj['MD_SIR']['Spc'][0][0])
R = subj['MD_SIR']['Orientation'][0][0]
flip_elem = np.array([[1,0,1],[1,0,1],[0,1,0]]).astype(bool)
R[flip_elem] = -R[flip_elem]
rot_matrix = R @ np.diag(spacing)
trans_vector = np.squeeze(subj['MD_SIR']['Origin'][0][0])
affine = np.eye(4)
affine[0:3,0:3] = rot_matrix
affine[0:3,3] = trans_vector
print(affine)

def do_reorientation(data_array, init_axcodes, final_axcodes):
    """
    Performs the reorientation (changing order of axes).

    :param data_array: Array to reorient
    :param init_axcodes: Initial orientation
    :param final_axcodes: Target orientation
    :return data_reoriented: New data array in its reoriented form
    """
    ornt_init = nib.orientations.axcodes2ornt(init_axcodes)
    ornt_fin = nib.orientations.axcodes2ornt(final_axcodes)
    if np.array_equal(ornt_init, ornt_fin):
        return data_array
    if np.any(np.isnan(ornt_init)) or np.any(np.isnan(ornt_fin)):
        raise ValueError
    try:
        ornt_transf = nib.orientations.ornt_transform(ornt_init, ornt_fin)
        data_reoriented = nib.orientations.apply_orientation(data_array, ornt_transf)
    except (ValueError, IndexError):
        raise ValueError

    return data_reoriented

reoriented = do_reorientation(subj['R1fs'], ('P', 'R', 'S'), ('R', 'A', 'S'))

subj_nifti = nib.nifti1.Nifti1Image(reoriented, affine)

subj_nifti.to_filename('examples/outputs/example_ground_truth.nii.gz')