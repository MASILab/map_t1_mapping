import nibabel as nib
import numpy as np
import pydicom

# Load the GREs
img = nib.load('/nfs/masi/saundam1/share/t1w.nii.gz')
print(img.dataobj.shape)

dcm = pydicom.dcmread('/nfs/masi/saundam1/datasets/MP2RAGE/334264/334264/401-x-WIPMP2RAGE_0p7mm_1sTI_best_oneSENSE-x-WIPMP2RAGE_0p7mm_1sTI_best_oneSENSE/DICOM/1.3.46.670589.11.9904.5.0.6620.2018041810422588000-401-1-zrtqjq.dcm')
print(dcm)