import nibabel as nib
import numpy as np
import pydicom
from scipy.spatial.transform import Rotation 

# Load image and change header
img = nib.load('/nfs/masi/saundam1/test/t1w.nii.gz')

header = img.header.copy()
header.set_sform(affine=None, code=0)
A = img.affine
A[0:3, 0:3] = np.eye(3)*np.diag(nib.affines.voxel_sizes(img.affine))

img_new = nib.Nifti1Image(img.dataobj, affine=A, header=header)
img_new.header.set_sform(affine=None, code=0)
img_new.header.set_qform(affine=A, code=1)

img_new.to_filename('/nfs/masi/saundam1/test/t1w_new_header.nii.gz')

# Load new image and change back to old header
img = nib.load('/nfs/masi/saundam1/test/t1w.nii.gz')
img_new = nib.load('/nfs/masi/saundam1/test/t1w_new_header.nii.gz')
img_old = nib.Nifti1Image(img_new.dataobj, affine=img.affine, header=img.header)
img_old.to_filename('/nfs/masi/saundam1/test/t1w_old_header.nii.gz')
