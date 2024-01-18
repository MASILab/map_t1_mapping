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
        GRE_noisy = GRE + s.normal(scale=sd, size=GRE.shape) + 1j * s.normal(scale=sd, size=GRE.shape)
        mp2rage_noisy = [mp2rage_t1w(GRE_noisy[i[0], :], GRE_noisy[i[1], :]) for i in subj.pairs]

        for c in zip(*mp2rage_noisy, subj.t1):
            coord = tuple([find_nearest(subj.m[idx], i) for idx, i in enumerate(c[:-1])]) + (find_nearest(subj.t1, c[-1]),)
            counts[coord] += 1

    return counts 

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Run Monte Carlo simulation to get MP2RAGE distribution")

    parser.add_argument("--params_path", type=str, help="Path to the parameters YAML file")
    parser.add_argument("--sim_output_path", type=str, help="Path to the simulation output file (ending in .npy)")
    parser.add_argument("--num_trials", type=int, help="Number of trials")
    parser.add_argument("--num_process", type=int, help="Number of processes to use")
    parser.add_argument("--noise_std", type=float, default=0.005, help="Noise standard deviation")

    args = parser.parse_args()

    # Load subject
    subj = t1_mapping.mp2rage.MP2RAGESubject(
        params_path=args.params_path
    )

    # Calculate what values would be produced using these parameters
    GRE = t1_mapping.utils.gre_signal(T1=subj.t1, **subj.eqn_params)

    # Now simulate with noise
    shape = tuple([m.shape[0] for m in subj.m])
    shape = shape + (subj.t1.shape[0],)
    n_inv = len(subj.params['inversion_times'])

    # Create normal distribution
    sd = subj.params['noise_std']

    num_trials = args.num_trials
    num_processes = args.num_process
    iter_per_process = num_trials // num_processes

    iterable_func = partial(accumulate_sums, m_ranges=subj.m_ranges)
    
    print(f'Simulating {len(subj.params["inversion_times"])} MP2RAGE images for {num_trials} trials using {num_processes} processes and {sd} noise STD')
    ranges = [(i, i + iter_per_process) for i in range(0, num_trials, iter_per_process)]
    counts = np.zeros(shape)
    with Pool(processes=num_processes) as p:
        for x in tqdm(p.imap_unordered(iterable_func, ranges), total=num_processes):
            counts += x
    
    # Save PDFs to file for later use
    output_folder = os.path.dirname(args.sim_output_path)
    os.makedirs(output_folder, exist_ok=True)
    with open(args.sim_output_path, 'wb') as f:
        np.save(f, counts)
