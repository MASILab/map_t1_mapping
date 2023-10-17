import t1_mapping
import numpy as np
import os
from glob import glob
from scipy.io import loadmat

# Check affines of rigid registrations
rigid_output = os.path.join(t1_mapping.definitions.OUTPUTS, 't1_maps_truth_rigid')

for subject in os.listdir(rigid_output):
    mat = loadmat(os.path.join(rigid_output, subject, 'GenericAffine.mat'))
    aff = np.eye(4)
    aff[:3, :3] = mat['AffineTransform_double_3_3'][:9].reshape((3,3))
    aff[:3, 3] =  mat['AffineTransform_double_3_3'][9:].squeeze()

    print(f'Rigid registration determinant: {np.linalg.det(aff)}')

# Check affine of affine registrations
affine_output = os.path.join(t1_mapping.definitions.OUTPUTS, 't1_maps_truth_affine')

for subject in os.listdir(affine_output):
    mat = loadmat(os.path.join(affine_output, subject, 'GenericAffine.mat'))
    aff = np.eye(4)
    aff[:3, :3] = mat['AffineTransform_double_3_3'][:9].reshape((3,3))
    aff[:3, 3] =  mat['AffineTransform_double_3_3'][9:].squeeze()

    print(f'Affine registration determinant: {np.linalg.det(aff)}')