import t1_mapping
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Load subject
subj = t1_mapping.mp2rage.MP2RAGESubject(
    subject_id='334264',
    scan='401-x-WIPMP2RAGE_0p7mm_1sTI_best_oneSENSE-x-WIPMP2RAGE_0p7mm_1sTI_best_oneSENSE',
    scan_times=['1010', '3310', '5610']
    )
counts = np.load(os.path.join(t1_mapping.definitions.SIMULATION_DATA, 'counts_100M_spacing.npy'))

# Range of values for T1
delta_t1 = subj.delta_t1
t1 = subj.t1

# Calculate what values would be produced using these parameters
GRE = t1_mapping.utils.gre_signal(T1=t1, **subj.eqn_params)

# Calculate what MP2RAGE image would have been
mp2rage1 = t1_mapping.utils.mp2rage_t1w(GRE[0,:], GRE[1,:])
mp2rage2 = t1_mapping.utils.mp2rage_t1w(GRE[0,:], GRE[2,:])

# Calculate likelihoods
delta_m = subj.delta_m
n_pairs = len(delta_m)
m_ranges = subj.m_ranges
m = subj.m

# Calculate likelihood
likelihood = counts / np.sum(counts * np.prod(delta_m), axis=tuple(range(n_pairs)))
likelihood = np.nan_to_num(likelihood, nan=0)
print(np.sum(likelihood[:,:,50]*delta_m[0]*delta_m[1])) # Should integrate to 1

# Calculate posterior
posterior = likelihood / np.sum(delta_t1*likelihood, axis=-1)[:,:,np.newaxis]
posterior = np.nan_to_num(posterior, nan=0)
print(np.sum(posterior[50,50,:]*delta_t1)) # Should integrate to 1

# Expected value
exp_val = np.sum(t1*posterior*delta_t1,axis=-1)
exp_val = np.nan_to_num(exp_val, nan=0)
print(f'Expected value: {exp_val[50,50]}')

# Variance
variance = np.sum((t1 - exp_val[:,:,np.newaxis])**2*posterior*delta_t1, axis=-1)
print(f'Variance: {variance[50,50]}')

fig, ax = plt.subplots()
ax.plot(t1, posterior[50,50,:])
plt.show()
