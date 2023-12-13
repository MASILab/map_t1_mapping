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

# # Define a function to accumulate sums into the shared counts matrix for a batch of trials
# def accumulate_sums(iteration_range, m_ranges):
#     counts = np.zeros(shape)
    
#     for trial in range(*iteration_range):
#         s = np.random.default_rng(trial)
#         GRE_noisy = GRE + s.normal(scale=sd, size=GRE.shape) + 1j * s.normal(scale=sd, size=GRE.shape)
#         mp2rage_noisy = [mp2rage_t1w(GRE_noisy[i[0], :], GRE_noisy[i[1], :]) for i in subj.pairs]

#         for c in zip(*mp2rage_noisy, subj.t1):
#             coord = tuple([round((i - m_ranges[idx][0]) / subj.delta_m[idx]) for idx, i in enumerate(c[:-1])]) + (round(c[-1] / subj.delta_t1) - 1,)
#             coord_clip = tuple(max(0, value) for value in coord)
#             counts[coord_clip] += 1

#     return counts 

if __name__ == '__main__':

    # Load subject
    subj = t1_mapping.mp2rage.MP2RAGESubject(
        subject_id='334264',
        scan='401-x-WIPMP2RAGE_0p7mm_1sTI_best_oneSENSE-x-WIPMP2RAGE_0p7mm_1sTI_best_oneSENSE',
        scan_times=['1010', '3310'], #5610
        all_inv_combos=False
    )

    sd = 0.005
    
    # Calculate what values would be produced using these parameters
    GRE = t1_mapping.utils.gre_signal(T1=subj.t1, **subj.eqn_params)
    print(f'GRE min: {GRE[1,:].min()}, GRE max: {GRE[1,:].max()}, GRE mean: {GRE[1,:].mean()}, GRE std: {GRE[1,:].std()}')
    print(f'STD/range: {GRE[1,:].std() / (GRE[1,:].max() - GRE[1,:].min())}')
    
    # # Get noisy version
    s = np.random.default_rng(2023)
    GRE_noisy = GRE + s.normal(scale=sd, size=GRE.shape) + 1j * s.normal(scale=sd, size=GRE.shape)
    MP2RAGE_noisy  = mp2rage_t1w(GRE_noisy[0,:], GRE_noisy[1,:]) + 0.5
    print(f'MP2RAGE mean: {MP2RAGE_noisy.mean()}, MP2RAGE std: {MP2RAGE_noisy.std()}')

    print(f'Real GRE min: {np.real(GRE_noisy[1,:]).min()}, Real GRE max: {np.real(GRE_noisy[1,:]).max()}, Real GRE mean: {np.real(GRE_noisy[1,:]).mean()}, Real GRE std: {np.real(GRE_noisy[1,:]).std()}')
    print(f'Real SNR: {np.real(GRE_noisy[1,:]).mean() / np.real(GRE_noisy[1,:]).std()}')