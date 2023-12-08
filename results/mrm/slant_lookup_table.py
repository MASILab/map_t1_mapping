import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
from adam_utils.nifti import load_slice
import nibabel as nib

lut_path = '/home/local/VANDERBILT/saundam1/Documents/slant/slant.lut'
df = pd.read_table(lut_path, delimiter='\s+', engine='python')


max_val = 209
# Loop through values in first column of df
colors_list = []
for i in range(max_val):
    
    # If i is in the first column of df, get the corresponding color
    if i in df.iloc[:,0].values:
        row_with_i = df[df.iloc[:, 0] == i]

        R = row_with_i.iloc[0, 1]  # Second column
        G = row_with_i.iloc[0, 2]   # Third column
        B = row_with_i.iloc[0, 3]  # Fourth column

        colors_list.append((R, G, B, 1.))
    else:
        colors_list.append((0, 0, 0, 1.))

# Create colormap
slant_cmap = matplotlib.colors.ListedColormap(colors_list, name='slant')

# Test on image
test_slant = nib.load('/nfs/masi/saundam1/outputs/t1_mapping/slant_test_mp2rage_nss_xnat_mask/334264/mp2rage_seg.nii.gz')
test_slant_slice = load_slice(test_slant, view=2)

fig, ax = plt.subplots()
ax.imshow(test_slant_slice, cmap=slant_cmap, vmin=0, vmax=209, interpolation='nearest')
plt.show()