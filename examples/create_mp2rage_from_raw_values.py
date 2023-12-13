# Create MP2RAGE image from raw values (same as DICOM)
import numpy as np
import nibabel as nib
import os
import t1_mapping

folder = '/nfs/masi/saundam1/outputs/t1_mapping/mp2rage_converted_test/336547'

gre1_nifti = nib.load(os.path.join(folder, '1101_real_t1010_raw.nii.gz'))
gre1_real = nib.load(os.path.join(folder, '1101_real_t1010_raw.nii.gz')).get_fdata()
gre1_imag = nib.load(os.path.join(folder, '1101_imaginary_t1010_raw.nii.gz')).get_fdata()
gre2_real = nib.load(os.path.join(folder, '1101_real_t3310_raw.nii.gz')).get_fdata()
gre2_imag = nib.load(os.path.join(folder, '1101_imaginary_t3310_raw.nii.gz')).get_fdata()

gre1 = gre1_real + 1j*gre1_imag
gre2 = gre2_real + 1j*gre2_imag

s1_2 = t1_mapping.utils.mp2rage_t1w(gre1, gre2)
s1_2_nifti = nib.Nifti1Image(s1_2, gre1_nifti.affine)
s1_2_nifti.to_filename(os.path.join(folder, 'test_mp2rage.nii.gz'))