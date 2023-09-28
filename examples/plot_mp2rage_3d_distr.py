# Plot from saved distr*.npy
import os
import t1_mapping
import nibabel as nib
from nilearn.plotting import plot_img
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import RegularGridInterpolator

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

# Plot histograms of MP2RAGE
fig, ax = plt.subplots()
ax.hist(mp2rage1, label='MP2RAGE1', bins=40)
ax.hist(mp2rage2, label='MP2RAGE2', bins=40)
ax.legend()

# Load data
distr = np.load(os.path.join('examples', 'outputs', 'distr_50000000.npy'))

# Plot PDF of example points
fig, ax = plt.subplots()
pts = [(50, 50), (20, 20), (30, 20), (5, 95)]
for idx, (i, j) in enumerate(pts):
    print(sum(distr[i,j,:]*delta_t1))
    ax.plot(t1_estimate, distr[i,j,:], label=f'MP2RAGE_1={mp2rage1[i]:.2f}, MP2RAGE_2={mp2rage2[j]:.2f}')
ax.set_xlabel('T1 (s)')
ax.set_ylabel('P(T1)')
ax.set_title('PDF for several values of MP2RAGE_1 and MP2RAGE_2')
ax.legend()

# Create LUT with largest probability of T1 value
# mean = np.mean(distr, axis=2)
# abs_diff = np.abs(distr - mean[:,:,np.newaxis])
# mean_idx = np.argmin(abs_diff, axis=2)
mode_idx = np.argmax(distr, axis=2)
LUT = t1_estimate[mode_idx]

# Plot this
fig = plt.figure()
ax = fig.add_subplot(projection='3d')
X,Y = np.meshgrid(mp2rage1, mp2rage2)
ax.plot_surface(X, Y, LUT)
ax.set_xlabel('MP2RAGE_1')
ax.set_ylabel('MP2RAGE_2')
ax.set_zlabel('T1 = argmax(P(T1)) (s)')
ax.set_title('PDF Mode Lookup Table')

plt.show()