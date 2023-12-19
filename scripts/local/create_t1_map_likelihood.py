# Create T1 map using MP2RAGE data (3 GREs)
import os
import t1_mapping
import nibabel as nib
import numpy as np
import pandas as pd
from tqdm import tqdm
from scipy.interpolate import RegularGridInterpolator
import re

def t1_map_likelihood(t1w, t1, m, delta_m, monte_carlo, likelihood_thresh=0.5):
    counts = np.load('/home/saundam1/temp_data/distr/counts_100M_s1_2_0.0006.npy')
    n_pairs = len(counts.shape) - 1
    m_ranges = [np.max(m) - np.min(m) for i in range(n_pairs)]
    posterior = counts / np.sum(counts*delta_t1, axis=-1)[...,np.newaxis]
    max_inds = np.argmax(posterior, axis=-1)
    t1_vals = t1[max_inds]

    # Calculate likelihoods
    L_gauss = counts / np.sum(counts * np.prod(delta_m), axis=tuple(range(n_pairs)))
    L_gauss = np.nan_to_num(L_gauss, nan=0)

    # Maximum likelihood of gaussian
    max_L_gauss = np.max(L_gauss, axis=-1)

    # Uniform likelihood
    total_vol = np.prod(m[1]-m[0] for m in m_ranges)
    m_squares = np.array([len(mp2rage) for mp2rage in m])
    total_squares = np.prod(m_squares)
    uni_value = 1/(total_squares*np.prod(delta_m))
    L_uni = np.full(tuple(m_squares), uni_value)

    # Relative likelihood
    alpha = max_L_gauss / (max_L_gauss + L_uni)

    # Create LUT
    max_L_gauss_ind = np.argmax(L_gauss, axis=-1)
    t1_lut = t1[max_L_gauss_ind]
    t1_lut[alpha < likelihood_thresh] = 0

    # Create grid
    interp = RegularGridInterpolator(tuple(m), values=t1_lut,
        bounds_error=False, fill_value=0, method='linear')

    # Clip to [-0.5, 0.5] to accounting for floating-point errors
    t1w = [np.clip(t, -0.5, 0.5) for t in t1w]

    # Interpolate along new values
    pts = tuple([t.flatten() for t in t1w])
    t1_calc = interp(pts).reshape(t1w[0].shape)

    return t1_calc

# Loop through subjects
save_path = '/home/saundam1/temp_data/t1_maps_likelihood'
for subject in tqdm(os.listdir('/home/saundam1/temp_data/mp2rage_t1w_strip')):
    subj_id = int(subject)

    # Load T1-weighted image
    t1w_nifti = nib.load(os.path.join('/home/saundam1/temp_data/mp2rage_t1w_mask', subject, 't1w.nii.gz'))
    t1w = t1w_nifti.get_fdata()

    # Calculate T1 map
    delta_t1 = 0.05
    m = [np.linspace(-0.5, 0.5, 100)]
    delta_m = np.array([m_arr[1]-m_arr[0] for m_arr in m])
    t1_map = t1_map_likelihood(
        t1w=[t1w],
        t1=np.arange(delta_t1, 5 + delta_t1, delta_t1),
        m=m, 
        delta_m=delta_m,
        monte_carlo='/home/saundam1/temp_data/distr/counts_100M_s1_2_0.0006.npy'
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