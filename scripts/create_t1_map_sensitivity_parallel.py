# Create T1 map using MP2RAGE data (3 GREs)
import os
import t1_mapping
import nibabel as nib
import numpy as np
import pandas as pd
from tqdm import tqdm
import re
from joblib import Parallel, delayed

def generate_map(subject, noise_level):
    subject = str(subject)
    subj_id = int(subject)
    scan = os.listdir(os.path.join(t1_mapping.definitions.DATA, subject))

    # Get scan IDs
    scan_id = [s.split('-')[0] for s in scan]
    primary_scan_ids = [int(s) for s in scan_id if s.endswith('1')]
    primary_scan_ids = sorted(primary_scan_ids)
    highest_primary_scan_id = primary_scan_ids[-1]

    # Get scan that starts with highest primary scan ID
    chosen_scan = [s for s in scan if s.startswith(str(highest_primary_scan_id))][0]

    # Find scan times
    data_files = os.listdir(os.path.join(t1_mapping.definitions.DATA, subject, chosen_scan))

    # Get scan times from files
    # times = [re.findall(r'\d{4}(?=\.)', s)[0] for s in data_files]
    times = [1010, 3310, 5610]

    # Get unique items and sort
    times = list(set(times))
    times = sorted(t for t in times)

    # Create MP2RAGE subject
    times_dict = {
        's1_2': [times[0], times[1]],
        's1_3': [times[0], times[2]],
        'all': times,
    }
    for method in ['s1_2', 's1_3', 'all']:

        subj = t1_mapping.mp2rage.MP2RAGESubject(
            subject_id=subject,
            scan=chosen_scan,
            scan_times=times_dict[method],
            monte_carlo=os.path.join(t1_mapping.definitions.SIMULATION_DATA, f'counts_100M_{method}_{noise_level}.npy'), 
            all_inv_combos=False,
        )

        # Calculate T1 map and save
        save_folder = os.path.join(t1_mapping.definitions.OUTPUTS, 'results', 'sensitivity', f't1_maps_likelihood_{method}_{noise_level}', str(subj_id))
        os.makedirs(save_folder, exist_ok=True)
        subj.t1_map(method='likelihood', thresh=0.5).to_filename(os.path.join(save_folder, 't1_map.nii.gz'))

    # ev_save_folder = os.path.join(t1_mapping.definitions.OUTPUTS, 'results', 'ev_maps_s1_2_0.005', str(subj_id))
    # std_save_folder = os.path.join(t1_mapping.definitions.OUTPUTS, 'results', 'std_maps_s1_2_0.005', str(subj_id))
    # os.makedirs(ev_save_folder, exist_ok=True)
    # os.makedirs(std_save_folder, exist_ok=True)
    # subj.t1_ev.to_filename(os.path.join(ev_save_folder, 'ev_map.nii.gz'))
    # subj.t1_std.to_filename(os.path.join(std_save_folder, 'std_map.nii.gz'))

# Loop over subjects in parallel
if __name__ == '__main__':
    num_processes = 6
    noise_levels = [0.0005, 0.001, 0.005, 0.01, 0.015, 0.02]
    groups = pd.read_csv(os.path.join(t1_mapping.definitions.OUTPUTS, 'ground_truth_subjects.csv'))
    subjects = groups['Subject'].to_numpy()
    print(subjects)
    Parallel(n_jobs=num_processes)(delayed(generate_map)(subject, n) for subject in tqdm(subjects) for n in tqdm(noise_levels, leave=False))
