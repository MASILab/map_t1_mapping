# Visualize distribution in Vedo
import numpy as np
import vedo
import os
import t1_mapping
from adam_utils.vedo import equal_axes
import nibabel as nib

# Load subject
subj = t1_mapping.mp2rage.MP2RAGESubject(
    subject_id="334264",
    scan="401-x-WIPMP2RAGE_0p7mm_1sTI_best_oneSENSE-x-WIPMP2RAGE_0p7mm_1sTI_best_oneSENSE",
    scan_times=["1010", "3310", "5610"],
    monte_carlo=os.path.join(t1_mapping.definitions.SIMULATION_DATA, 'counts_100K.npy')
)

# Range of values for T1
delta_t1 = 0.05
t1_estimate = np.arange(delta_t1, 5 + delta_t1, delta_t1)
num_points = len(t1_estimate)

# Calculate what values would be produced using these parameters
GRE = t1_mapping.utils.gre_signal(T1=t1_estimate, **subj.eqn_params)

# Calculate what MP2RAGE image would have been
mp2rage1 = t1_mapping.utils.mp2rage_t1w(GRE[0, :], GRE[1, :])
mp2rage2 = t1_mapping.utils.mp2rage_t1w(GRE[0, :], GRE[2, :])

# Load data
points = np.load(os.path.join(t1_mapping.definitions.SIMULATION_DATA, "points_1K.npy"))
# t1_truth = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 't1_maps_truth_affine', subj.subject_id, 'Warped.nii.gz'))
# t1_truth_data = t1_truth.get_fdata()
# mask = t1_truth_data > 0
# m1 = subj.mp2rage[0].get_fdata()
# m2 = subj.mp2rage[1].get_fdata()
# t1_map = subj.t1_map.get_fdata()
# points2 = np.array(list(zip(m1[mask > 0], m2[mask > 0], t1_map[mask > 0])))

# Make data to plot
X, Y, Z = np.meshgrid(mp2rage1, mp2rage2, t1_estimate)

# Generate point cloud used to calculate density
pts = vedo.Points(points, r=10)

# Generate density
vol = pts.density().c("jet").alpha([0, 1])

# Generate colorbar
# vol.add_scalarbar(title="Density", c="k", nlabels=2, pos=(0.8, 0.3), size=(None, 500))

# Specify maximum intensity projection
vol.mode(1)

# Scale to have equal axes
scale, values_and_labels, ranges = equal_axes(xlim=[-0.5,0.5], ylim=[-0.5,0.5], zlim=[0, 5])
vol.scale(scale)

# Customize axes and tick labels
axes = vedo.Axes(
    vol,
    x_values_and_labels=values_and_labels['x'],
    y_values_and_labels=values_and_labels['y'],
    z_values_and_labels=values_and_labels['z'],
    xrange=ranges['x'],
    yrange=ranges['y'],
    zrange=ranges['z'],
    xtitle="MP2RAGE_1",
    ytitle="MP2RAGE_2",
    ztitle="T1 (s)",
)

# Set up plotter
plt = vedo.Plotter(interactive=False)

# Add volume to plotter
plt += vol

# Show current axes
plt.show(axes=axes, viewup="z")

# # Create video
# video = vedo.Video("examples/outputs/distribution.mp4", duration=3, backend='ffmpeg')

# # Change camera angle
# for i in np.arange(1,360,5):
#     angle = 0.5*np.cos(i/180*np.pi)
#     plt.camera.Azimuth(angle)
#     plt.render()

#     # Add video frame
#     video.add_frame()

# video.close()

# After spinning, turn to interactive mode
plt.interactive().close()
