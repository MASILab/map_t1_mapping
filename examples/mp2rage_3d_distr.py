# Create 3D probability distribution for T1
import t1_mapping
import nibabel as nib
from nilearn.plotting import plot_img
import numpy as np
import matplotlib.pyplot as plt

# Load subject
subj = t1_mapping.mp2rage.MP2RAGESubject(
    subject='334264',
    scan='401-x-WIPMP2RAGE_0p7mm_1sTI_best_oneSENSE-x-WIPMP2RAGE_0p7mm_1sTI_best_oneSENSE',
    scan_times=['1010', '3310', '5610']
    )

# Plot T1w image
# fig, ax = plt.subplots()
# plot_img(subj.t1w, cut_coords=(15, 5, 30), cmap='gray', axes=ax, colorbar=True)
# ax.set_title('T1-Weighted Image')
# plt.show()

# Range of values for T1
t1_estimate = np.arange(0.05, 5.01, 0.05)
num_points = len(t1_estimate)

# Calculate what values would be produced using these parameters
GRE = t1_mapping.utils.gre_signal(T1=t1_estimate, **subj.eqn_params)

# Calculate what MP2RAGE image would have been
mp2rage1 = t1_mapping.utils.mp2rage_t1w(GRE[0,:], GRE[1,:])
mp2rage2 = t1_mapping.utils.mp2rage_t1w(GRE[0,:], GRE[2,:])

fig = plt.figure()
ax = fig.add_subplot(projection='3d')

# Plot curve of known values
ax.plot(mp2rage1, mp2rage2, t1_estimate, label='Calculated values', color='darkblue')

# Set up plot
ax.set_xlabel('MP2RAGE_1*')
ax.set_ylabel('MP2RAGE_2*')
ax.set_zlabel('T1 (s)')
ax.set(xlim=(-0.5, 0.5), ylim=(-0.5, 0.5), zlim=(0,5))

# Plot values we want to calculate
indx = np.arange(0, len(subj.mp2rage[0].flatten()), 50000)
ax.scatter(subj.mp2rage[0].flatten()[indx], subj.mp2rage[1].flatten()[indx], zs=0, zdir='z', color=[0,1,0,0.2], label='Unknown values')

# Plot projections
ax.plot(mp2rage1, mp2rage2, zs=0, zdir='z', color=[1,0,0,0.2])
ax.plot(mp2rage1, t1_estimate, zs=-0.5, zdir='x', color=[1,0,0,0.2])
ax.plot(mp2rage2, t1_estimate, zs=0.5, zdir='y', color=[1,0,0,0.2])


for trial in range(1, 100):
    # Now, simulate with some noise
    sd = 0.004

    # Calculate what values would be produced using these parameters
    GRE = t1_mapping.utils.gre_signal(T1=t1_estimate, **subj.eqn_params)

    # Calculate what MP2RAGE image would have been
    mp2rage1_noisy = t1_mapping.utils.mp2rage_t1w(GRE[0,:] + np.random.normal(scale=sd, size=GRE.shape[1]) + 1j*(np.random.normal(scale=sd, size=GRE.shape[1])), 
        GRE[1,:] + np.random.normal(scale=sd, size=GRE.shape[1]) + 1j*(np.random.normal(scale=sd, size=GRE.shape[1])))
    mp2rage2_noisy = t1_mapping.utils.mp2rage_t1w(GRE[0,:] + np.random.normal(scale=sd, size=GRE.shape[1]) + 1j*(np.random.normal(scale=sd, size=GRE.shape[1])),
        GRE[2,:] + np.random.normal(scale=sd, size=GRE.shape[1]) + 1j*(np.random.normal(scale=sd, size=GRE.shape[1])))


    # Plot
    if trial == 1:
        ax.scatter(0, 0, 0, color=[1,0,0,0.2], label='Noisy values')
    ax.scatter(mp2rage1_noisy.flatten(), mp2rage2_noisy.flatten(), t1_estimate, color=[1,0,0,0.02])

ax.legend()

plt.show()
