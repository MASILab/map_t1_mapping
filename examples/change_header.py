import nibabel as nib
import numpy as np
import pydicom

# Load the GREs
img = nib.load('/nfs/masi/saundam1/share/t1w.nii.gz')
print(img.header)

blank_header = nib.Nifti1Header()
img_blank = nib.Nifti1Image(img.dataobj, affine=img.affine, header=blank_header)
print(img_blank.header)
img_blank.to_filename('/nfs/masi/saundam1/test/t1w_new_header.nii.gz')

print(nib.affines.to_matvec(img.affine))