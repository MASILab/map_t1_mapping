# Generate figure 4: quantitative results (group)
import numpy as np
import os
import t1_mapping
import nibabel as nib 
import matplotlib.pyplot as plt
import pandas as pd
from scipy.stats import wilcoxon
import seaborn as sns
from statannotations.Annotator import Annotator
import matplotlib

matplotlib.rcParams['grid.linewidth'] = 1
matplotlib.rcParams['axes.linewidth'] = 1
matplotlib.rcParams['font.size'] = 12
sns.set_style('ticks')
sns.set_context('paper')
save_fig = True

df = pd.read_csv('~/Documents/t1_mapping/results/slant_seg_sensitivity_results.csv')

# Create boxplot
print(df)

# fig, ax = plt.subplots(figsize=(6,4), layout='constrained')
# ax = sns.lineplot(
#     data=df, 
#     x='Noise Level',
#     y='RMSE', 
#     hue='Method',    
#     hue_order=['s1_2', 's1_3', 'both'],
#     ax=ax,
#     errorbar='se',
#     err_style='bars',
#     err_kws={
#         'capsize': 5,
#     },
#     marker='o',
#     markersize=6,
# )

ax = sns.relplot(
    data=df, 
    x='Noise Level',
    y='RMSE', 
    hue='Method',    
    hue_order=['s1_2', 's1_3', 'both'],
    kind='line',
    col='Tissue Type',
    col_order=['WM', 'GM', 'Other', 'All'],
    col_wrap=2,
    facet_kws={
        'sharey': False,
        'sharex': True,
    },
    errorbar='se',
    err_style='bars',
    err_kws={
        'capsize': 5,
    },
    marker='o',
    markersize=5,
    height=3,
    aspect=1,
)

plt.show()

if save_fig:
    ax.figure.savefig('/home/local/VANDERBILT/saundam1/Pictures/t1_mapping/mrm_figures/sensitivity_quant.pdf', dpi=1200, bbox_inches='tight', transparent=True)