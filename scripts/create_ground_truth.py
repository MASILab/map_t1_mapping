# Load ground truth from .mat and convert to NIFTI
import t1_mapping
import os
import numpy as np
import nibabel as nib
from nilearn.plotting import plot_anat
from scipy.io import loadmat
import pandas as pd
from glob import glob
from tqdm import tqdm

def do_reorientation(data_array, init_axcodes, final_axcodes):
    """
    Performs the reorientation (changing order of axes).

    :param data_array: Array to reorient
    :param init_axcodes: Initial orientation
    :param final_axcodes: Target orientation
    :return data_reoriented: New data array in its reoriented form
    """
    ornt_init = nib.orientations.axcodes2ornt(init_axcodes)
    ornt_fin = nib.orientations.axcodes2ornt(final_axcodes)
    if np.array_equal(ornt_init, ornt_fin):
        return data_array
    if np.any(np.isnan(ornt_init)) or np.any(np.isnan(ornt_fin)):
        raise ValueError
    try:
        ornt_transf = nib.orientations.ornt_transform(ornt_init, ornt_fin)
        data_reoriented = nib.orientations.apply_orientation(data_array, ornt_transf)
    except (ValueError, IndexError):
        raise ValueError

    return data_reoriented


ground_truth = '/home/saundam1/temp_data/7T_SIRqMT_R1maps' # t1_mapping.definitions.GROUND_TRUTH_MAT
for file in tqdm(glob(os.path.join(ground_truth, '*.mat'))):
    # Get subject ID
    file_name = os.path.basename(file)
    subj_id = file_name.split('_')[1].split('.')[0]
    
    # Load data
    subj = loadmat(file, variable_names=['R1fs', 'MD_SIR'])

    # Calculate affine
    # spacing = np.squeeze(subj['MD_SIR']['Spc'][0][0])
    # R = subj['MD_SIR']['Orientation'][0][0]
    # flip_elem = np.array([[1,0,1],[1,0,1],[0,1,0]]).astype(bool)
    # R[flip_elem] = -R[flip_elem]
    # rot_matrix = R @ np.diag(spacing)D
    # trans_vector = np.squeeze(subj['MD_SIR']['Origin'][0][0])
    # affine = np.eye(4)
    # affine[0:3,0:3] = rot_matrix
    # affine[0:3,3] = trans_vector

    # Get affine from NIFTIs generated from PAR/REC files
    nifti_files = glob(os.path.join(ground_truth, 'SIRqMT_nii', str(subj_id), '*_real.nii'))
    try:
        readouts = nib.load(nifti_files[0])
        affine = readouts.affine

        # Reorient axes
        reoriented = do_reorientation(subj['R1fs'], ('P', 'R', 'S'), ('R', 'A', 'S'))

        # Calculate T1 from R1fs
        T1 = 1/reoriented

        # Save to NIFTI if possible
        subj_nifti = nib.nifti1.Nifti1Image(T1, affine)
        save_folder = os.path.join(ground_truth, str(subj_id))
        save_path = os.path.join(save_folder, 'filtered_t1_map.nii.gz')
        os.makedirs(save_folder, exist_ok=True)

        subj_nifti.to_filename(save_path)

        # Update progress
        tqdm.write(f'Saved {subj_id} to {save_path}')
    except Exception as e:
        print(e)
        tqdm.write(f'No data found for {subj_id}')