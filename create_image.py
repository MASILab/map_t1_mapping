# Create T1 map using MP2RAGE data (3 GREs)
import os
import t1_mapping
import nibabel as nib
import numpy as np
from tqdm import tqdm
import re
from joblib import Parallel, delayed
import argparse

def generate_map(scan_folder, output_folder, params_path, img_type, monte_carlo_path=None):
    # Load subject
    subj = t1_mapping.mp2rage.MP2RAGESubject(
        params_path=params_path,
        scan_folder=scan_folder,
        monte_carlo=monte_carlo_path
    )

    # Generate image based on type
    if img_type == 't1w':
        img = subj.t1w
        output_name = 't1w.nii.gz'
    elif img_type == 'robust_t1w':
        img = subj.robust_t1w
        output_name = 'robust_t1w.nii.gz'
    elif img_type == 'ev':
        img = subj.t1_ev
        output_name = 't1_ev.nii.gz'
    elif img_type == 'std':
        img = subj.t1_std
        output_name = 't1_std.nii.gz'
    elif img_type == 'var':
        img = subj.t1_var
        output_name = 't1_var.nii.gz'
    elif img_type == 'point':
        img = subj.t1_map('point')
        output_name = 't1_map.nii.gz'
    elif img_type == 'likelihood':
        img = subj.t1_map('likelihood')
        output_name = 't1_map.nii.gz'
    elif img_type == 'map':
        img = subj.t1_map('map')
        output_name = 't1_map.nii.gz'
    else:
        raise ValueError('Image type not recognized')

    # Save image
    scan = os.path.basename(scan_folder)
    rest_of_path = os.path.dirname(scan_folder)
    subject = os.path.basename(rest_of_path)
    output_path = os.path.join(output_folder, subject, scan, output_name)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.to_filename(output_path)

# Loop over subjects in parallel
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Create images from MP2RAGE data")

    parser.add_argument("--params_path", type=str, help="Path to the parameters YAML file")
    parser.add_argument("--input_folder", type=str, help="Path to the input folder containing the subjects")
    parser.add_argument("--output_folder", type=str, help="Path to output folder")
    parser.add_argument("--num_process", type=int, help="Number of processes to use")
    parser.add_argument("--image_type", type=str, help="Type of image to generate (T1 map [point, likelihood, map] or t1w, robust_t1w, ev, std, var)")
    parser.add_argument("--monte_carlo_path", type=str, help="Path to the Monte Carlo simulation file for image type likelihood, map, ev, std or var (ending in .npy)")
    
    args = parser.parse_args()

    params_path = args.params_path
    input_folder = args.input_folder
    output_folder = args.output_folder
    num_process = args.num_process
    img_type = args.image_type
    monte_carlo_path = args.monte_carlo_path

    print(f'Creating {img_type} images...')

    # Create list of subjects and scans in subject folders
    subjects = os.listdir(input_folder)
    scan_paths = []
    for subject in subjects:
        subject_path = os.path.join(input_folder, subject)
        if os.path.isdir(subject_path):
            scans = os.listdir(subject_path)
            for scan in scans:
                scan_paths.append(os.path.join(subject_path, scan))
    
    if num_process == 1:
        [generate_map(scan_folder, output_folder, params_path, img_type, monte_carlo_path) for scan_folder in tqdm(scan_paths)]
    else:
        Parallel(n_jobs=num_process)(delayed(generate_map)(scan_folder, output_folder, params_path, img_type, monte_carlo_path) for scan_folder in tqdm(scan_paths))
