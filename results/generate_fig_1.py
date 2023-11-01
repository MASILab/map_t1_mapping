# Create T1 map using MP2RAGE data (3 GREs)
import os
import t1_mapping
import nibabel as nib
import numpy as np
import matplotlib.pyplot as plt
from adam_utils.nifti import plot_nifti

# Load subject
subj = t1_mapping.mp2rage.MP2RAGESubject(
    subject_id='334264',
    scan='401-x-WIPMP2RAGE_0p7mm_1sTI_best_oneSENSE-x-WIPMP2RAGE_0p7mm_1sTI_best_oneSENSE',
    scan_times=['1010', '3310', '5610'],
    monte_carlo=os.path.join(t1_mapping.definitions.SIMULATION_DATA, 'counts_100M_spacing.npy'), 
    all_inv_combos=False,
)

# Calculate T1-weighted image
t1w = t1_mapping.utils.mp2rage_t1w(subj.inv[0].get_fdata(dtype=np.complex64), subj.inv[1].get_fdata(dtype=np.complex64))

GRE = t1_mapping.utils.gre_signal(
    T1=subj.t1,
    TD=subj.eqn_params['TD'],
    TR=subj.eqn_params['TR'],
    flip_angles=subj.eqn_params['flip_angles'],
    n=subj.eqn_params['n'],
    eff=subj.eqn_params['eff']
)

m = t1_mapping.utils.mp2rage_t1w(GRE[0,:], GRE[1,:])

# Plot
fig = plt.figure()
ax1 = fig.add_subplot(1,3,1)
ax1.plot(m, subj.t1)
ax1.set_xlabel('$S_{1,2}$')
ax1.set_ylabel('$T_1$ (s)')
ax1.grid(True)

m1 = t1_mapping.utils.mp2rage_t1w(GRE[0,:], GRE[1,:])
m2 = t1_mapping.utils.mp2rage_t1w(GRE[0,:], GRE[2,:])

ax2 = fig.add_subplot(1,3,2, projection='3d')
ax2.view_init(27, -116, 0)
ax2.plot(m1, m2, subj.t1)
ax2.set_xlabel('$S_{1,2}$')
ax2.set_ylabel('$S_{2,3}$')
ax2.set_zlabel('$T_1$ (s)')
ax2.plot(m1, m2, zs=0, zdir='z', color=[1,0,0,0.2])
ax2.plot(m1, subj.t1, zs=0.5, zdir='x', color=[1,0,0,0.2])
ax2.plot(m2, subj.t1, zs=0.5, zdir='y', color=[1,0,0,0.2])

plt.show()