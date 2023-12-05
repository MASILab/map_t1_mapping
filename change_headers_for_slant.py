import nibabel as nib
import numpy as np
import pydicom
from scipy.spatial.transform import Rotation 
import os

t1w_files = '/nfs/masi/saundam1/outputs/t1_mapping/mp2rage_t1w'
t1w_outputs = '/home/masi/saundam1/mp2rage_t1w_slant_ss'
for subject in ['334264']: #os.listdir('/nfs/masi/saundam1/outputs/t1_mapping/mp2rage_t1w'):
    
    raw_t1w = nib.load(os.path.join(t1w_files, subject, 't1w.nii.gz'))

    # Change header
    header = raw_t1w.header.copy()
    A = raw_t1w.affine
    A[0:3, 0:3] = np.eye(3)*np.diag(nib.affines.voxel_sizes(raw_t1w.affine))

    # Assign new header
    new_t1w = nib.Nifti1Image(raw_t1w.dataobj, affine=A, header=header)
    new_t1w.header.set_sform(affine=None, code=0)
    new_t1w.header.set_qform(affine=A, code=1)

    # Save new image
    new_t1w.to_filename(os.path.join(t1w_files, subject, 't1w.nii.gz'))

# # Load new image and change back to old header
# img = nib.load('/nfs/masi/saundam1/test/t1w.nii.gz')
# img_new = nib.load('/nfs/masi/saundam1/test/t1w_new_header.nii.gz')
# img_old = nib.Nifti1Image(img_new.dataobj, affine=img.affine, header=img.header)
# img_old.to_filename('/nfs/masi/saundam1/test/t1w_old_header.nii.gz')
