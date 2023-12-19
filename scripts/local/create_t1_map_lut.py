# Create T1 map using MP2RAGE data (3 GREs)
import os
import t1_mapping
import nibabel as nib
import numpy as np
import pandas as pd
from tqdm import tqdm
import re

def t1_map_lut(t1w, t1, TD, TR, flip_angles, n, eff):
        GRE = t1_mapping.utils.gre_signal(
            T1=t1,
            TD=TD,
            TR=TR,
            flip_angles=flip_angles,
            n=n,
            eff=eff
        )
        m = t1_mapping.utils.mp2rage_t1w(GRE[0,:], GRE[1,:])

        # Sort arrays
        sorted_idx = np.argsort(m)
        m = m[sorted_idx]
        t1 = t1[sorted_idx]

        # Pad LUT
        m[0] = -0.5
        m[-1] = 0.5

        # Calculate for desired values
        t1_calc = np.interp(t1w.flatten(), m, t1, right=0.)
        t1_calc = t1_calc.reshape(t1w.shape)

        return t1_calc

# Loop through subjects
save_path = '/home/saundam1/temp_data/t1_maps_lut'
for subject in tqdm(os.listdir('/home/saundam1/temp_data/mp2rage_t1w_strip')):
    subj_id = int(subject)

    # Load T1-weighted image
    t1w_nifti = nib.load(os.path.join('/home/saundam1/temp_data/mp2rage_t1w_mask', subject, 't1w.nii.gz'))
    t1w = t1w_nifti.get_fdata()

    # Set acquisition parameters
    acq_params : t1_mapping.utils.MP2RAGEParameters = {
        "MP2RAGE_TR": 8.25,
        "TR": 0.006,
        "flip_angles": [4.0, 4.0],
        "inversion_times": [1010/1000, 3310/1000],
        "n": [225],
        "eff": 0.84,
    }

    # Set equation parameters
    eqn_params = t1_mapping.utils.acq_to_eqn_params(acq_params)

    # Calculate T1 map
    delta_t1 = 0.05
    t1_map = t1_map_lut(
        t1w=t1w,
        t1=np.arange(delta_t1, 5 + delta_t1, delta_t1),
        **eqn_params
    )

    # Mask by skull-stripped image
    mask_nifti = nib.load(os.path.join('/home/saundam1/temp_data/mp2rage_t1w_strip', subject, 'mask.nii.gz'))
    mask = mask_nifti.get_fdata()
    t1_map = t1_map * mask

    # Save
    t1_map_nifti = nib.nifti1.Nifti1Image(t1_map, t1w_nifti.affine)
    save_folder = os.path.join(save_path, subject)
    os.makedirs(save_folder, exist_ok=True)
    t1_map_nifti.to_filename(os.path.join(save_folder, 't1_map.nii.gz'))