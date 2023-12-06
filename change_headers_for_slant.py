import nibabel as nib
import numpy as np
import pydicom
from scipy.spatial.transform import Rotation 
import os

t1w_files = '/nfs/masi/saundam1/outputs/t1_mapping/mp2rage_t1w'
mask = '/nfs/masi/saundam1/outputs/t1_mapping/t1w_strip'
t1w_outputs = '/home/saundam1/temp_data/mp2rage_t1w_slant_ss'
for subject in os.listdir('/nfs/masi/saundam1/outputs/t1_mapping/mp2rage_t1w'):
    print(subject)
    
    raw_t1w = nib.load(os.path.join(t1w_files, subject, 't1w.nii.gz'))
    try:
        raw_mask = nib.load(os.path.join(mask, subject, 'mask.nii'))
    except FileNotFoundError:
        continue
    # Change header
    header = raw_t1w.header.copy()
    A = raw_t1w.affine
    A[0:3, 0:3] = np.eye(3)*np.diag(nib.affines.voxel_sizes(raw_t1w.affine))

    # Image goes from 0 to 1 (not -0.5 to 0.5)
    new_t1w_data = raw_t1w.get_fdata() + np.full(raw_t1w.shape, 0.5)

    # Mask image
    new_t1w_data = new_t1w_data * raw_mask.get_fdata()
    new_t1w = nib.Nifti1Image(new_t1w_data, affine=raw_t1w.affine, header=raw_t1w.header)

    # Assign new header
    new_t1w = nib.Nifti1Image(new_t1w.dataobj, affine=A, header=header)
    new_t1w.header.set_sform(affine=None, code=0)
    new_t1w.header.set_qform(affine=A, code=1)

    new_mask = nib.Nifti1Image(raw_mask.dataobj, affine=A, header=header)
    new_mask.header.set_sform(affine=None, code=0)
    new_mask.header.set_qform(affine=A, code=1)

    # Save new image
    os.makedirs(os.path.join(t1w_outputs, subject, 'in', 'pre'), exist_ok=True)
    os.makedirs(os.path.join(t1w_outputs, subject, 'in', 'post'), exist_ok=True)
    os.makedirs(os.path.join(t1w_outputs, subject, 'out', 'pre'), exist_ok=True)
    os.makedirs(os.path.join(t1w_outputs, subject, 'out', 'post'), exist_ok=True)
    os.makedirs(os.path.join(t1w_outputs, subject, 'out', 'dl'), exist_ok=True)
    new_t1w.to_filename(os.path.join(t1w_outputs, subject, 'in', 'pre', 't1w.nii.gz'))
    new_mask.to_filename(os.path.join(t1w_outputs, subject, 'in', 'pre', 't1w_label.nii.gz'))

# # Load new image and change back to old header
# img = nib.load('/nfs/masi/saundam1/test/t1w.nii.gz')
# img_new = nib.load('/nfs/masi/saundam1/test/t1w_new_header.nii.gz')
# img_old = nib.Nifti1Image(img_new.dataobj, affine=img.affine, header=img.header)
# img_old.to_filename('/nfs/masi/saundam1/test/t1w_old_header.nii.gz')
