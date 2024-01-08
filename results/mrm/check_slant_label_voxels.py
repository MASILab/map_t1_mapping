import pandas as pd
import os
import numpy as np

# Load dataframe
df = pd.read_csv('/home/local/VANDERBILT/saundam1/Documents/t1_mapping/results/slant_results.csv')
lut_df = df[df['Method'] == 'lut']

# Get labels and label names
label = lut_df['Tissue Label'].unique()
label_name = lut_df['Label Name'].unique()

# Get mean number of voxels for each label
mean_voxels = lut_df.groupby('Tissue Label')['Number of Voxels'].mean()

# Get number of subjects for each label
num_subjects = lut_df.groupby('Tissue Label')['Subject'].nunique()

# Create dataframe
label_df = pd.DataFrame({
    'Label': label,
    'Label Name': label_name,
    'Mean Number of Voxels': mean_voxels.values,
    'Number of Subjects': num_subjects.values,
})

print(label_df)
label_df.to_csv('/home/local/VANDERBILT/saundam1/Documents/t1_mapping/results/slant_num_voxels.csv')