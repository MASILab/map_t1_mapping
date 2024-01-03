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

# Calculate standard error
# for j, points in enumerate(ax.collections):
#     for i, (x, y) in enumerate(points.get_offsets()):
#         print(i,j)
#         label = df['Tissue Label'].unique()[i]
#         method = df['Method'].unique()[i % 4 + j]

#         # Calculate standard error
#         rmse_values = df[(df['Tissue Label'] == label) & (df['Method'] == method)]['RMSE']

#         # Calculate number of subjects with this label
#         num_subjects = df[(df['Tissue Label'] == label) & (df['Method'] == method)]['Subject'].unique().shape[0]

#         se_val = np.std(rmse_values)/np.sqrt(num_subjects)
#         print(f'{label} {method} {num_subjects}')

#         # Choose color based on method
#         if method == 's1_2':
#             color = 'blue'
#         elif method == 's1_3':
#             color = 'orange'
#         elif method == 'both':
#             color = 'green'
#         elif method == 'lut':
#             color = 'red'

#         ax.errorbar(
#             x=x,
#             y=y,
#             yerr=se_val,
#             fmt='none',
#             ecolor=color,
#             capsize=5,
#             zorder=0,
#         )

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
        num_subjects = df[(df['Tissue Label'] == label) & (df['Method'] == method)]['Subject'].unique().shape[0]

        se_val = np.std(rmse_values)/np.sqrt(num_subjects)
        print(f'{label} {method} {num_subjects}')
        
        # Add error bars
        ax.errorbar(x, y, yerr=se_val, fmt='none', color=color, capsize=5, zorder=0)


ax.set_ylabel('Mean RMSE across subjects (s)')

# Change legend labels
handles, prev_labels = ax.get_legend_handles_labels()
ax.legend(
    handles=handles, 
    labels=['Original point estimate T1', 'MAP T1 using $S_{1,2}$', 'MAP T1 using $S_{1,3}$', 'MAP T1 using both $S_{1,2}$ and $S_{1,3}$'],
    )
plt.tight_layout()
plt.show()