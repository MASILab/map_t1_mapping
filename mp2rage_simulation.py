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
import argparse
from functools import partial

# Define a function to accumulate sums into the shared counts matrix for a batch of trials
def accumulate_sums(iteration_range, m_ranges):
    counts = np.zeros(shape)
    
    for trial in range(*iteration_range):
        s = np.random.default_rng(trial)
        GRE_noisy = GRE + s.normal(scale=sd, size=GRE.shape) + 1j * s.normal(scale=sd, size=GRE.shape)
        mp2rage_noisy = [mp2rage_t1w(GRE_noisy[i[0], :], GRE_noisy[i[1], :]) for i in subj.pairs]

        for c in zip(*mp2rage_noisy, subj.t1):
            coord = tuple([round((i - m_ranges[idx][0]) / subj.delta_m[idx]) for idx, i in enumerate(c[:-1])]) + (round(c[-1] / subj.delta_t1) - 1,)
            coord_clip = tuple(max(0, value) for value in coord)
            counts[coord_clip] += 1

    return counts 

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Run Monte Carlo simulation to get MP2RAGE distribution")

    parser.add_argument("--output_path", type=str, help="Path to the output file")
    parser.add_argument("--num_trials", type=int, help="Number of trials")
    parser.add_argument("--num_process", type=int, help="Number of CPUs to use")
    parser.add_argument("--noise_std", type=float, default=0.005, help="Noise standard deviation")
    parser.add_argument("--all_inv_combos", action="store_true", help="Include all inversion combinations instead of just pairwise")

    args = parser.parse_args()

    # Load subject
    subj = t1_mapping.mp2rage.MP2RAGESubject(
        subject_id='334264',
        scan='401-x-WIPMP2RAGE_0p7mm_1sTI_best_oneSENSE-x-WIPMP2RAGE_0p7mm_1sTI_best_oneSENSE',
        scan_times=['1010', '5610'], #5610
        all_inv_combos=args.all_inv_combos
    )

    # Calculate what values would be produced using these parameters
    GRE = t1_mapping.utils.gre_signal(T1=subj.t1, **subj.eqn_params)

    # Now simulate with noise
    shape = tuple([m.shape[0] for m in subj.m])
    shape = shape + (subj.t1.shape[0],)
    n_inv = len(subj.scan_times)

    # Create normal distribution
    sd = args.noise_std
    print(subj.pairs)

    num_trials = args.num_trials
    num_processes = args.num_process
    iter_per_process = num_trials // num_processes

    iterable_func = partial(accumulate_sums, m_ranges=subj.m_ranges)
    
    print(f'Simulating {len(subj.pairs)} MP2RAGE images for {num_trials} trials using {num_processes} processes')
    ranges = [(i, i + iter_per_process) for i in range(0, num_trials, iter_per_process)]
    counts = np.zeros(shape)
    with Pool(processes=num_processes) as p:
        for x in tqdm(p.imap(iterable_func, ranges), total=num_processes):
            counts += x
    
    # Save PDFs to file for later use
    with open(args.output_path, 'wb') as f:
        np.save(f, counts)
