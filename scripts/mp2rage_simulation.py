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

def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx


# Define a function to accumulate sums into the shared counts matrix for a batch of trials
def accumulate_sums(iteration_range, m_ranges):
    counts = np.zeros(shape)
    
    for trial in range(*iteration_range):
        s = np.random.default_rng(trial)
        GRE_noisy = np.zeros(GRE.shape, dtype=np.complex64)
        if len(real_sd) == 1:
            GRE_noisy = GRE + s.normal(scale=real_sd[0], size=GRE.shape) + 1j * s.normal(scale=imag_sd[0], size=GRE.shape)
        else:
            for i in range(len(real_sd)):
                GRE_noisy[i,:] = GRE[i, :] + s.normal(scale=real_sd[i], size=GRE[i,:].shape) + 1j * s.normal(scale=imag_sd[i], size=GRE[i,:].shape)
                # mag_part = s.normal(scale=real_sd[i], size=GRE[i,:].shape)
                # ang_part = s.normal(scale=imag_sd[i], size=GRE[i,:].shape)
                # GRE_noisy[i,:] = GRE[i, :] + mag_part * np.cos(ang_part) + 1j * mag_part * np.sin(ang_part)
        mp2rage_noisy = [mp2rage_t1w(GRE_noisy[i[0], :], GRE_noisy[i[1], :]) for i in subj.pairs]

        for c in zip(*mp2rage_noisy, subj.t1):
            # coord = tuple([round((i - m_ranges[idx][0]) / subj.delta_m[idx]) for idx, i in enumerate(c[:-1])]) + (round(c[-1] / subj.delta_t1) - 1,)
            # coord_clip = tuple(max(0, value) for value in coord)
            coord = tuple([find_nearest(subj.m[idx], i) for idx, i in enumerate(c[:-1])]) + (find_nearest(subj.t1, c[-1]),)
            counts[coord] += 1

    return counts 

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Run Monte Carlo simulation to get MP2RAGE distribution")

    parser.add_argument("--output_path", type=str, help="Path to the output file")
    parser.add_argument("--num_trials", type=int, help="Number of trials")
    parser.add_argument("--num_process", type=int, help="Number of CPUs to use")
    # parser.add_argument("--noise_std", type=float, default=0.005, help="Noise standard deviation")
    parser.add_argument("--real_noise_std", nargs='+', type=float, help="Noise standard deviation for real component of inversions")
    parser.add_argument("--imag_noise_std", nargs='+', type=float, help="Noise standard deviation for imaginary component of inversions")
    parser.add_argument("--all_inv_combos", action="store_true", help="Include all inversion combinations instead of just pairwise")
    parser.add_argument("--times", nargs='+', type=int, help="List of inversion times to use (ex. --times 1 3, --times 1 2 3)")

    args = parser.parse_args()

    # Load subject
    scan_times = ['1010', '3310', '5610']
    times = [scan_times[t-1] for t in args.times]
    print(times)
    subj = t1_mapping.mp2rage.MP2RAGESubject(
        subject_id='334264',
        scan='401-x-WIPMP2RAGE_0p7mm_1sTI_best_oneSENSE-x-WIPMP2RAGE_0p7mm_1sTI_best_oneSENSE',
        scan_times=times,
        all_inv_combos=args.all_inv_combos
    )

    # Calculate what values would be produced using these parameters
    GRE = t1_mapping.utils.gre_signal(T1=subj.t1, **subj.eqn_params)

    # Now simulate with noise
    shape = tuple([m.shape[0] for m in subj.m])
    shape = shape + (subj.t1.shape[0],)
    n_inv = len(subj.scan_times)

    # Create normal distribution
    # sd = args.noise_std
    real_sd = args.real_noise_std
    imag_sd = args.imag_noise_std
    print(subj.pairs)

    num_trials = args.num_trials
    num_processes = args.num_process
    iter_per_process = num_trials // num_processes

    iterable_func = partial(accumulate_sums, m_ranges=subj.m_ranges)
    
    print(f'Simulating {len(subj.pairs)} MP2RAGE images for {num_trials} trials using {num_processes} processes and {real_sd, imag_sd} noise STD')
    ranges = [(i, i + iter_per_process) for i in range(0, num_trials, iter_per_process)]
    counts = np.zeros(shape)
    with Pool(processes=num_processes) as p:
        for x in tqdm(p.imap_unordered(iterable_func, ranges), total=num_processes):
            counts += x
    
    # Save PDFs to file for later use
    with open(args.output_path, 'wb') as f:
        np.save(f, counts)
