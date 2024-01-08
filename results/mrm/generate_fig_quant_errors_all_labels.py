import numpy as np
import os
import t1_mapping
import nibabel as nib 
import matplotlib.pyplot as plt
import matplotlib
import pandas as pd
from adam_utils.nifti import load_slice
import seaborn as sns

# Create RMSE dataframe
df = pd.read_csv('/home/local/VANDERBILT/saundam1/Documents/t1_mapping/results/slant_results.csv')
df = df.sort_values(by=['Tissue Label'])
num_voxels_df = pd.read_csv('/home/local/VANDERBILT/saundam1/Documents/t1_mapping/results/slant_num_voxels.csv')
print(df)

# Plot RMSE and standard error using seaborn
fig, ax = plt.subplots(figsize=(14, 8))
hue_order = ['lut', 's1_2', 's1_3', 'both']
sns.pointplot(
    data=df,
    x='Label Name',
    y='RMSE',
    hue='Method',
    hue_order=hue_order,
    errorbar=None,
    join=False,
    ax=ax,
    scale=0.5
)
ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
ax.set_ylim([0, 2.5])

# Loop over each point to add custom error bars
for i, point in enumerate(ax.collections):
    # Get the coordinates of the point
    coords = point.get_offsets().data

    for x, y in coords:
        # Get the label and method
        label = df['Tissue Label'].unique()[int(x)]
        method = hue_order[i % 4]

        # Choose color based on method
        if method == 'lut':
            color = 'blue'
        elif method == 's1_2':
            color = 'orange'
        elif method == 's1_3':
            color = 'green'
        elif method == 'both':
            color = 'red'

        # Calculate the error value
        rmse_values = df[(df['Tissue Label'] == label) & (df['Method'] == method)]['RMSE']

        # Calculate number of subjects with this label
        num_subjects = num_voxels_df[num_voxels_df['Label'] == label]['Number of Subjects'].values[0]

        # Get average number of voxels
        num_voxels = num_voxels_df[num_voxels_df['Label'] == label]['Mean Number of Voxels'].values[0]

        se_val = np.std(rmse_values)/np.sqrt(num_subjects)
        print(f'{label=} {method=} {num_subjects=} ')
        
        # Add error bars
        ax.errorbar(x, y, yerr=se_val, fmt='none', color=color, capsize=5, zorder=0)

        # Add text annotation with average number of voxels (only once)
        if (label == 129 and method == 's1_2') or (label != 129 and method == 's1_3'):
            ax.text(x, y+se_val+0.08, f'{num_voxels:.2f}', color='k', ha='center', va='bottom', rotation=90)


ax.set_ylabel('Mean RMSE across subjects (s)')

# Change legend labels
handles, prev_labels = ax.get_legend_handles_labels()
ax.legend(
    loc='upper center',
    handles=handles, 
    labels=['Original point estimate T1', 'MAP T1 using $S_{1,2}$', 'MAP T1 using $S_{1,3}$', 'MAP T1 using both $S_{1,2}$ and $S_{1,3}$'],
    )
plt.tight_layout()
plt.show()