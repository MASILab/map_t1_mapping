# Create 3D probability distribution for T1
import os
import t1_mapping
import nibabel as nib
from nilearn.plotting import plot_img
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import RegularGridInterpolator
from math import floor

# Load subject
subj = t1_mapping.mp2rage.MP2RAGESubject(
    subject='334264',
    scan='401-x-WIPMP2RAGE_0p7mm_1sTI_best_oneSENSE-x-WIPMP2RAGE_0p7mm_1sTI_best_oneSENSE',
    scan_times=['1010', '3310', '5610']
    )

# Range of values for T1
delta_t1 = 0.05
t1_estimate = np.arange(delta_t1, 5 + delta_t1, delta_t1)
num_points = len(t1_estimate)

# Calculate what values would be produced using these parameters
GRE = t1_mapping.utils.gre_signal(T1=t1_estimate, **subj.eqn_params)

# Calculate what MP2RAGE image would have been
mp2rage1 = t1_mapping.utils.mp2rage_t1w(GRE[0,:], GRE[1,:])
mp2rage2 = t1_mapping.utils.mp2rage_t1w(GRE[0,:], GRE[2,:])

# Plot curve of known values
fig = plt.figure()
ax = fig.add_subplot(projection='3d')
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

# Now simulate with noise
distr = np.zeros((mp2rage1.shape[0], mp2rage2.shape[0], t1_estimate.shape[0]))
delta_m = (0.5-(-0.5))/mp2rage1.shape[0]

# Create normal distribution
sd = 0.005
s = np.random.default_rng()

num_trials = 50_000_000
for trial in range(num_trials):
    if trial % 10_000 == 0:
        print(f'Trial {trial:>12,}/{num_trials:<12,} [{100*trial/num_trials:.1f}%]')

    # Calculate MP2RAGE images with noisy GRE
    GRE_noisy = GRE + s.normal(scale=sd, size=GRE.shape) + 1j*s.normal(scale=sd, size=GRE.shape)

    mp2rage1_noisy = t1_mapping.utils.mp2rage_t1w(GRE_noisy[0,:], GRE_noisy[1,:])
    mp2rage2_noisy = t1_mapping.utils.mp2rage_t1w(GRE_noisy[0,:], GRE_noisy[2,:])

    # Plot first 100 trials
    if trial == 1:
        ax.scatter(0, 0, 0, color=[1,0,0,0.2], label='Noisy values')
    if trial < 100:
        ax.scatter(mp2rage1_noisy, mp2rage2_noisy, t1_estimate, color=[1,0,0,0.02])

    # Sum the number of occurrences in each voxel
    for m1, m2, t1 in zip(mp2rage1_noisy, mp2rage2_noisy, t1_estimate):
        coord = (round((m1+0.5)/delta_m)-1, round((m2+0.5)/delta_m)-1, round(t1/delta_t1)-1)
        distr[coord] += 1

ax.legend()

# Create pdf for each voxel
for i in range(distr.shape[0]):
    for j in range(distr.shape[1]):
        # Need to normalize and flip (since indices went high to low)
        distr[i,j,:] = distr[i,j,:]/(delta_t1*np.sum(distr[i,j,:]))
        distr[i,j,:] = distr[i,j,::-1]

# Plot PDF of example points
fig, ax = plt.subplots()
pts = [(50, 50), (20, 20), (5, 95)]
for i, j in pts:
    ax.stairs(distr[i,j,:], np.append(t1_estimate, 5 + delta_t1), label=f'MP2RAGE_1={mp2rage1[i]:.2f}, MP2RAGE_2={mp2rage2[j]:.2f}')
ax.set_xlabel('T1 (s)')
ax.set_ylabel('P(T1)')
ax.set_title('PDF for several values of MP2RAGE_1 and MP2RAGE_2')
ax.legend()

# Save PDFs to file for later use
with open(f'examples/outputs/distr_{num_trials}.npy', 'wb') as f:
    np.save(f, distr)

## Create LUT with largest probability of T1 value
#LUT = t1_estimate[np.argmax(distr, axis=2)]
#
## Plot this
#fig = plt.figure()
#ax = fig.add_subplot(projection='3d')
#X,Y = np.meshgrid(mp2rage1, mp2rage2)
#ax.plot_surface(X, Y, LUT)
#ax.set_xlabel('MP2RAGE_1')
#ax.set_ylabel('MP2RAGE_2')
#ax.set_zlabel('T1 = argmax(P(T1)) (s)')
#ax.set_title('PDF Mode Lookup Table')


# # Calculate T1 map
# interp = RegularGridInterpolator((X,Y), LUT)
# pts = (subj.mp2rage[0].flatten(), subj.mp2rage[1].flatten())
# t1_map = interp(pts).reshape(subj.mp2rage[0].shape)
# t1_map_nifti = nib.nifti1.Nifti1Image(t1_map, subj.mp2rage[0].affine)

# # Plot T1w image
# fig, ax = plt.subplots()
# plotting.plot_img(t1_map_nifti, cut_coords=(15, 5, 30), cmap='gray', axes=ax, colorbar=True)
# ax.set_title('T1 Map Image')

#plt.show()
