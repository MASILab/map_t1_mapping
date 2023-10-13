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
points = np.load(os.path.join(t1_mapping.definitions.SIMULATION_DATA, 'points_1K.npy'))

# Make data to plot
X,Y,Z = np.meshgrid(mp2rage1, mp2rage2, t1_estimate)

# Plotter
plotter = vedo.Plotter(
    size=[500, 500],
    title='Distribution'
)

# Generate point cloud
pts = vedo.Points(points, r=10)
pts.scale((1,1,0.2))

# Generate density
vol = pts.density().c('jet').alpha([0,1])
r = vedo.precision(vol.info['radius'], 2)
vol.add_scalarbar(title='Density', c='k', nlabels=2, pos=(0.7, 0.3))
vol.mode(1)

# Customize axes
z_vals = np.linspace(0, 1, 5)
z_labels = np.linspace(0, np.max(Z), 5)
axes = vedo.Axes(
    pts,
    z_values_and_labels=list(zip(z_vals, z_labels)),
    xtitle='MP2RAGE_1',
    ytitle='MP2RAGE_2',
    ztitle='T1 (s)'
)

vedo.show(vol, axes=axes).close()
