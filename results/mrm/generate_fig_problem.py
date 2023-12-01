# Generate figure 1: problem
import os
import t1_mapping
import nibabel as nib
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib
import pandas as pd
from adam_utils.nifti import load_slice

# Seaborn and matplotlib defaults
matplotlib.rcParams['grid.linewidth'] = 1
matplotlib.rcParams['axes.linewidth'] = 1
sns.set_style('ticks')
sns.set_context('paper')
save_fig = True

# Display T1 versus S1,2
subj = t1_mapping.mp2rage.MP2RAGESubject(
    subject_id='334264',
    scan='401-x-WIPMP2RAGE_0p7mm_1sTI_best_oneSENSE-x-WIPMP2RAGE_0p7mm_1sTI_best_oneSENSE',
    scan_times=['1010', '3310'],
    monte_carlo=os.path.join(t1_mapping.definitions.SIMULATION_DATA, 'counts_100M_s1_2.npy'), 
    all_inv_combos=False,
)

GRE = t1_mapping.utils.gre_signal(
    T1=subj.t1,
    **subj.eqn_params
)

subj_data = pd.DataFrame({
    'T1': subj.t1,
    'S1_2': t1_mapping.utils.mp2rage_t1w(GRE[0,:], GRE[1,:])
})

# Plot T1 versus S1,2
fig, ax = plt.subplots(figsize=(3.5, 4.2))
sns.lineplot(data=subj_data, x='S1_2', y='T1', ax=ax)
ax.set_xlabel('$S_{1,2}$')
ax.set_ylabel('$T_1$ (s)')
ax.set_title('MP2RAGE signal equation')
ax.grid(linewidth=1)

if save_fig:
    fig.savefig('/home/saundam1/VM/shared_folder/mp2rage/MRM_figures/fig1_part1.png', dpi=600)

# Plot axial slice of T1 map
t1_map = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 't1_maps_lut', subj.subject_id, 't1_map.nii'))
t1_slice = load_slice(t1_map, view=2)
fig, ax = plt.subplots(figsize=(3, 4))
im = ax.imshow(t1_slice, cmap='gray', vmin=0, vmax=5)
ax.set_title('$T_1$ map')
cbar = fig.colorbar(im, ax=ax)
ax.set_axis_off()
cbar.ax.set_xlabel('s')

if save_fig:
    fig.savefig('/home/saundam1/VM/shared_folder/mp2rage/MRM_figures/fig1_part2.png', dpi=600)

# Display T1 versus S1,2 and S1,3
subj = t1_mapping.mp2rage.MP2RAGESubject(
    subject_id='334264',
    scan='401-x-WIPMP2RAGE_0p7mm_1sTI_best_oneSENSE-x-WIPMP2RAGE_0p7mm_1sTI_best_oneSENSE',
    scan_times=['1010', '3310', '5610'],
    monte_carlo=os.path.join(t1_mapping.definitions.SIMULATION_DATA, 'counts_100M_spacing.npy'), 
    all_inv_combos=False,
)

GRE = t1_mapping.utils.gre_signal(
    T1=subj.t1,
    **subj.eqn_params
)

subj_data = pd.DataFrame({
    'T1': subj.t1,
    'S1_2': t1_mapping.utils.mp2rage_t1w(GRE[0,:], GRE[1,:]),
    'S1_3': t1_mapping.utils.mp2rage_t1w(GRE[0,:], GRE[2,:])
})

# Plot T1 versus S1,2 and S1,3
m1 = subj_data['S1_2'].values
m2 = subj_data['S1_3'].values
fig = plt.figure(figsize=(5, 4), layout='constrained')
ax = fig.add_subplot(projection='3d')
ax.plot(m1, m2, subj.t1, color='b')
ax.set_xlabel('$S_{1,2}$')
ax.set_ylabel('$S_{1,3}$')
ax.set_zlabel('$T_1$ (s)')

t1w1 = subj.mp2rage[0].get_fdata()
t1w2 = subj.mp2rage[1].get_fdata()
indx = np.arange(0, len(t1w1.flatten()), 50000)
ax.scatter(t1w1.flatten()[indx], t1w2.flatten()[indx], zdir='z', color=[0,1,0,0.2], label='Sample unknown values')
ax.legend()
ax.set_title('Multiple MP2RAGE signals')

if save_fig:
    fig.savefig('/home/saundam1/VM/shared_folder/mp2rage/MRM_figures/fig1_part3.png', dpi=600)


plt.show()