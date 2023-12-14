# Run Monte Carlo simulation with fix
import numpy as np
import t1_mapping
import os
from tqdm import tqdm
import itertools
from multiprocessing import Pool
import argparse
from functools import partial

def accumulate_sums(iteration_range, subj, sd):
    counts = np.zeros(tuple(len(m) for m in subj.m) + (len(subj.t1),))
    m_new = [m[:,np.newaxis] for m in subj.m]
    for i in range(*iteration_range):
        # Get original point estimate LUT
        GRE = t1_mapping.utils.gre_signal(
            T1=subj.t1,
            **subj.eqn_params
        )
        # Add complex-valued Gaussian noise
        GRE = GRE.astype(np.complex64)
        GRE += np.random.normal(0, sd, GRE.shape) + 1j*np.random.normal(0, sd, GRE.shape)

        m_idx = []
        for idx, (i,j) in enumerate(subj.pairs):
            m_iter = t1_mapping.utils.mp2rage_t1w(GRE[i,:], GRE[j,:])

            dist = np.abs(m_new[idx] - m_iter)
            m_idx.append(np.argmin(dist, axis=1))

        t1_idx = np.arange(len(subj.t1))

        # Add to counts
        counts[*m_idx, t1_idx] += 1

    return counts 

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Run Monte Carlo simulation to get MP2RAGE distribution")

    parser.add_argument("--output_path", type=str, help="Path to the output file")
    parser.add_argument("--num_trials", type=int, help="Number of trials")
    parser.add_argument("--num_process", type=int, help="Number of CPUs to use")
    parser.add_argument("--noise_std", type=float, default=0.005, help="Noise standard deviation")
    parser.add_argument("--all_inv_combos", action="store_true", help="Include all inversion combinations instead of just pairwise")
    parser.add_argument("--times", nargs='+', type=int, help="List of inversion times to use (ex. --times 1 3, --times 1 2 3)")

    args = parser.parse_args()

    # Load subject
    scan_times = ['1010', '3310', '5610']
    times = [scan_times[t-1] for t in args.times]
    subj = t1_mapping.mp2rage.MP2RAGESubject(
        subject_id='334264',
        scan='401-x-WIPMP2RAGE_0p7mm_1sTI_best_oneSENSE-x-WIPMP2RAGE_0p7mm_1sTI_best_oneSENSE',
        scan_times=times,
        all_inv_combos=args.all_inv_combos
    )

    num_trials = args.num_trials
    num_processes = args.num_process
    iter_per_process = num_trials // num_processes

    iterable_func = partial(accumulate_sums, subj=subj, sd=args.noise_std)
    
    print(f'Simulating {len(subj.pairs)} MP2RAGE images for {num_trials} trials using {num_processes} processes and {args.noise_std} noise STD')
    ranges = [(i, i + iter_per_process) for i in range(0, num_trials, iter_per_process)]
    counts = np.zeros(tuple(len(m) for m in subj.m) + (len(subj.t1),))
    with Pool(processes=num_processes) as p:
        for x in tqdm(p.imap(iterable_func, ranges), total=num_processes):
            counts += x
    
    # Save PDFs to file for later use
    with open(args.output_path, 'wb') as f:
        np.save(f, counts)