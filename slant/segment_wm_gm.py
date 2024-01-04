import nibabel as nib
import t1_mapping
import numpy as np
import os
from tqdm import tqdm

# Load SLANT 
for subject in tqdm(os.listdir(os.path.join(t1_mapping.definitions.OUTPUTS, 'slant_mp2rage_nss_0.25'))):
    # print(subject)

    slant = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 'slant_mp2rage_nss_0.25', subject, 't1w_seg.nii.gz'))

    # Segment into WM, GM and TICV/posterior fossa
    slant_data = slant.get_fdata()
    wm_mask = (slant_data >= 40) & (slant_data <= 45)  
    other_mask = (slant_data == 208) | (slant_data == 209) | (slant_data == 0) | (slant_data == 51) | (slant_data == 52)
    gm_mask = ~wm_mask & ~other_mask

    # Get data
    wm_data = np.zeros(slant_data.shape)
    wm_data[wm_mask] = slant_data[wm_mask]
    gm_data = np.zeros(slant_data.shape)
    gm_data[gm_mask] = slant_data[gm_mask]
    other_data = np.zeros(slant_data.shape)
    other_data[other_mask] = slant_data[other_mask]

    # Save to new NIFTIs
    wm = nib.Nifti1Image(wm_data, slant.affine)
    gm = nib.Nifti1Image(gm_data, slant.affine)
    other = nib.Nifti1Image(other_data, slant.affine)

    wm.to_filename(os.path.join(t1_mapping.definitions.OUTPUTS, 'slant_mp2rage_nss_0.25', subject, 't1w_seg_wm.nii.gz'))
    gm.to_filename(os.path.join(t1_mapping.definitions.OUTPUTS, 'slant_mp2rage_nss_0.25', subject, 't1w_seg_gm.nii.gz'))
    other.to_filename(os.path.join(t1_mapping.definitions.OUTPUTS, 'slant_mp2rage_nss_0.25', subject, 't1w_seg_other.nii.gz'))