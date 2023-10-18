# Visualize distribution in Vedo
import numpy as np
import vedo 
import os
import t1_mapping

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

# Generate point cloud used to calculate density
pts = vedo.Points(points, r=10)

# Scale axes to be equal (will need to modify tick labels)
pts.scale((1,1,0.2))

# Generate density
vol = pts.density().c('jet').alpha([0,1])

# Generate colorbar
vol.add_scalarbar(title='Density', c='k', nlabels=2, pos=(0.8, 0.3), size=(None,500))

# Specify maximum intensity projection
vol.mode(1)

# Customize axes and tick labels
z_vals = np.linspace(0, 1, 5)
z_labels = np.linspace(0, np.max(Z), 5)
axes = vedo.Axes(
    vol,
    z_values_and_labels=list(zip(z_vals, z_labels)),
    xtitle='MP2RAGE_1',
    ytitle='MP2RAGE_2',
    ztitle='T1 (s)'
)

# Set up plotter
plt = vedo.Plotter(interactive=False)

# Add volume to plotter
plt += vol

# Show current axes
plt.show(axes=axes, viewup='z')

# Change camera angle
for i in range(360):
    plt.camera.Azimuth(1)
    plt.render()

# After spinning, turn to interactive mode
plt.interactive().close()