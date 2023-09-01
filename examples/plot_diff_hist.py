import matplotlib.pyplot as plt
import numpy as np
import nibabel as nib

diff_nifti = nib.load('examples/outputs/example_t1_map_diff.nii')
diff = diff_nifti.get_fdata()


# Flatten the data to a 1D array for histogram calculation
flattened_data = diff.flatten()

# Calculate the histogram
hist, bins = np.histogram(flattened_data, bins=50)  # You can adjust the number of bins

# Create a figure and axis using Matplotlib's object-oriented interface
fig, ax = plt.subplots()

# Plot the histogram
ax.hist(flattened_data, bins=50, color='blue', alpha=0.7)
ax.set_title('Histogram of NIFTI Image Data')
ax.set_xlabel('Pixel Value')
ax.set_ylabel('Frequency')

# Show the plot
plt.show()