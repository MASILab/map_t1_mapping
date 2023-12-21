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
from scipy.spatial.distance import cdist

# Seaborn and matplotlib defaults
matplotlib.rcParams['grid.linewidth'] = 1
matplotlib.rcParams['axes.linewidth'] = 1
matplotlib.rcParams['font.size'] = 12
sns.set_style('ticks')
sns.set_context('paper')
save_fig = True

# Display T1 versus S1,2
subj = t1_mapping.mp2rage.MP2RAGESubject(
    subject_id='334264',
    scan='401-x-WIPMP2RAGE_0p7mm_1sTI_best_oneSENSE-x-WIPMP2RAGE_0p7mm_1sTI_best_oneSENSE',
    scan_times=['1010', '3310'],
    monte_carlo=os.path.join(t1_mapping.definitions.SIMULATION_DATA, 'counts_100M_s1_2_0.0006.npy'), 
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
fig, ax = plt.subplots(figsize=(3.25, 4))
sns.lineplot(data=subj_data, x='S1_2', y='T1', ax=ax, color='k')
ax.set_xlabel('$S_{1,2}$')
ax.set_ylabel('$T_1$ (s)')
ax.set_title('Single MP2RAGE signal')
ax.grid(linewidth=1)

# Add dashed lines and point at -0.2
x = -0.15
y = np.interp(x, subj_data['S1_2'].values[::-1], subj_data['T1'].values[::-1])
xlims = ax.get_xlim()
ylims = ax.get_ylim()
ax.vlines(x, ylims[0], y, linestyle='dashed', color='b')
ax.hlines(y, xlims[0], x, linestyle='dashed', color='b')
ax.set_xlim(xlims)
ax.set_ylim(ylims)
ax.plot(x, y, 'b.', markersize=10)


if save_fig:
    fig.savefig('/home/local/VANDERBILT/saundam1/Pictures/t1_mapping/mrm_figures/problem_1.pdf', dpi=1200, bbox_inches='tight')

# Display T1 versus S1,2 and S1,3
subj = t1_mapping.mp2rage.MP2RAGESubject(
    subject_id='334264',
    scan='401-x-WIPMP2RAGE_0p7mm_1sTI_best_oneSENSE-x-WIPMP2RAGE_0p7mm_1sTI_best_oneSENSE',
    scan_times=['1010', '3310', '5610'],
    monte_carlo=os.path.join(t1_mapping.definitions.SIMULATION_DATA, 'counts_100M_all_0.0006.npy'), 
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
fig = plt.figure(figsize=(3.25, 4), layout='constrained')
ax = fig.add_subplot(projection='3d')
ax.plot(m1, m2, subj.t1, color='k')
ax.set_xlabel('$S_{1,2}$')
ax.set_ylabel('$S_{1,3}$')
ax.set_zlabel('$T_1$ (s)')

t1w1 = subj.mp2rage[0].get_fdata()
t1w2 = subj.mp2rage[1].get_fdata()
indx = np.arange(0, len(t1w1.flatten()), 50000)
ax.scatter(t1w1.flatten()[indx], t1w2.flatten()[indx], zdir='z', color=[0,1,0,0.2], label='Sample unknown values')
ax.legend()
ax.set_title('Multiple MP2RAGE signals')

# Add dashed lines and point 
pt = np.array([-0.15, -0.2])[:,np.newaxis]
nodes = np.array([t1w1.flatten()[indx], t1w2.flatten()[indx]])
print(pt.shape, nodes.shape)
closest_ind = cdist(pt.T, nodes.T).argmin()
x = t1w1.flatten()[indx][closest_ind]
y = t1w2.flatten()[indx][closest_ind]
z = 1
xlims = ax.get_xlim()
ylims = ax.get_ylim()
zlims = ax.get_zlim()
ax.text(x,y,z, '?', fontsize=14)
ax.plot([x, xlims[1]], [y,y], [zlims[0],zlims[0]], 'b--', linewidth=1)
ax.plot([x,x], [ylims[0],y], [zlims[0],zlims[0]], 'b--', linewidth=1)
ax.plot([x,x], [y,y], [zlims[0],z], 'b--', linewidth=1)
ax.set_xlim(xlims)
ax.set_ylim(ylims)
ax.set_zlim(zlims)

if save_fig:
    fig.savefig('/home/local/VANDERBILT/saundam1/Pictures/t1_mapping/mrm_figures/problem_2.pdf', dpi=1200, bbox_inches='tight')


plt.show()