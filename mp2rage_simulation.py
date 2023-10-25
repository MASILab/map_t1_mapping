# Create 3D probability distribution for T1
import os
import t1_mapping
import nibabel as nib
import numpy as np
from math import floor
from tqdm import tqdm
import itertools

# Load subject
subj = t1_mapping.mp2rage.MP2RAGESubject(
    subject_id='334264',
    scan='401-x-WIPMP2RAGE_0p7mm_1sTI_best_oneSENSE-x-WIPMP2RAGE_0p7mm_1sTI_best_oneSENSE',
    scan_times=['1010', '3310', '5610']
)

# Calculate what values would be produced using these parameters
GRE = t1_mapping.utils.gre_signal(T1=subj.t1, **subj.eqn_params)

# Now simulate with noise
shape = tuple([m.shape[0] for m in subj.m])
shape = shape + (subj.t1.shape[0],)
counts = np.zeros(shape)
n_inv = len(subj.scan_times)

# Create normal distribution
sd = 0.005

# Get pairs that need to be simulated
pairs = list(itertools.combinations(range(n_inv), 2))
if len(pairs) > 1:
    pairs = pairs[:-1]

num_trials = 1_000
print(f'Simulating {len(pairs)} dimensions for {num_trials} trials')

for trial in tqdm(range(num_trials), desc='Running simulation'):

    s = np.random.default_rng(trial)

    # Calculate MP2RAGE images with noisy GRE
    GRE_noisy = GRE + s.normal(scale=sd, size=GRE.shape) + 1j*s.normal(scale=sd, size=GRE.shape)


    mp2rage_noisy = [t1_mapping.utils.mp2rage_t1w(GRE_noisy[i[0],:], GRE_noisy[i[1],:]) for i in pairs]

    # Sum the number of occurrences in each voxel
    for c in zip(*mp2rage_noisy, subj.t1):
        coord = tuple([round((i+0.5)/subj.delta_m)-1 for i in c[:-1]]) + (round(c[-1]/subj.delta_t1)-1,)
        counts[coord] += 1

# Flip counts since T1 should be ascending
counts = counts[..., ::-1]

# Save PDFs to file for later use
with open(os.path.join(t1_mapping.definitions.SIMULATION_DATA, f'counts_{int(num_trials//1e6)}M_test.npy'), 'wb') as f:
    np.save(f, counts)
