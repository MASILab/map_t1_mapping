# Create 3D probability distribution for T1
import os
import t1_mapping
from t1_mapping.utils import mp2rage_t1w
import nibabel as nib
import numpy as np
from math import floor
from tqdm import tqdm
import itertools
from multiprocessing import Pool

# Load subject
subj = t1_mapping.mp2rage.MP2RAGESubject(
    subject_id='334264',
    scan='401-x-WIPMP2RAGE_0p7mm_1sTI_best_oneSENSE-x-WIPMP2RAGE_0p7mm_1sTI_best_oneSENSE',
    scan_times=['1010', '3310', '5610'],
    all_inv_combos=False
)

# Calculate what values would be produced using these parameters
GRE = t1_mapping.utils.gre_signal(T1=subj.t1, **subj.eqn_params)

# Now simulate with noise
shape = tuple([m.shape[0] for m in subj.m])
shape = shape + (subj.t1.shape[0],)
n_inv = len(subj.scan_times)

# Create normal distribution
sd = 0.005
print(subj.pairs)

# Define a function to accumulate sums into the shared counts matrix for a batch of trials
def accumulate_sums(iteration_range):
    counts = np.zeros(shape)
    
    for trial in range(*iteration_range):
        s = np.random.default_rng(trial)
        GRE_noisy = GRE + s.normal(scale=sd, size=GRE.shape) + 1j * s.normal(scale=sd, size=GRE.shape)
        mp2rage_noisy = [mp2rage_t1w(GRE_noisy[i[0], :], GRE_noisy[i[1], :]) for i in subj.pairs]

        for c in zip(*mp2rage_noisy, subj.t1):
            coord = tuple([round((i + 0.5) / subj.delta_m) - 1 for i in c[:-1]]) + (round(c[-1] / subj.delta_t1) - 1,)
            counts[coord] += 1

    return counts

if __name__ == '__main__':
    num_trials = 100_000_000
    num_processes = 19
    iter_per_process = num_trials // num_processes
    
    print(f'Simulating {len(subj.pairs)} MP2RAGE images for {num_trials} trials using {num_processes} processes')
    ranges = [(i, i + iter_per_process) for i in range(0, num_trials, iter_per_process)]
    counts = np.zeros(shape)
    with Pool(processes=num_processes) as p:
        for x in tqdm(p.imap(accumulate_sums, ranges), total=num_processes):
            counts += x
    
    # Save PDFs to file for later use
    with open(os.path.join(t1_mapping.definitions.SIMULATION_DATA, f'counts_{int(num_trials // 1e6)}M.npy'), 'wb') as f:
        np.save(f, counts)
