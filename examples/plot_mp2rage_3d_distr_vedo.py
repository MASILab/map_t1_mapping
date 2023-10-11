# Visualize distribution in Vedo
import numpy as np
import vedo 
import os
import t1_mapping

# Settings
vedo.settings.use_depth_peeling = True

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

# Load data
distr = np.load(os.path.join(t1_mapping.definitions.SIMULATION_DATA, 'distr_100M_no_nan.npy'))
counts = np.load(os.path.join(t1_mapping.definitions.SIMULATION_DATA, 'counts_100M_no_nan.npy'))

# Make data to plot
X,Y,Z = np.meshgrid(mp2rage1, mp2rage2, t1_estimate)
ind = np.stack((X, Y, Z), axis=-1).reshape(-1, 3)
values = distr.reshape(-1, 1)
ones = np.ones((values.shape[0], 3))
colors = np.hstack((ones, 255*values/np.max(values)))

# # Get points for density
# num_occurr = np.array([[i, j, k] for i in range(counts.shape[0])
#     for j in range(counts.shape[1])
#     for k in range(counts.shape[2])
#     for _ in range(int(counts[i,j,k]))])
# print(num_occurr.shape)

# Generate point cloud
pts = vedo.Points(ind, r=10, c=colors)
pts.scale((1,1,0.2))

# Generate density
# Not correct - this counts the number of points of a regular array
vol = pts.density().c('Dark2').alpha([0.1,1])
r = vedo.precision(vol.info['radius'], 1)
vol.add_scalarbar3d(title='Density (counts in r_s ='+r+')', c='k', italic=1)

# Customize axes
z_vals = np.linspace(0, 1, 5)
z_labels = np.linspace(0, np.max(Z), 5)
axes = vedo.Axes(
    pts,
    z_values_and_labels=list(zip(z_vals, z_labels))
)

vedo.show(pts, vol, axes=axes).close()
