# Generate figure on segmented quantitative results
import numpy as np
import os
import t1_mapping
import nibabel as nib 
import matplotlib.pyplot as plt
import matplotlib
import pandas as pd
from scipy.stats import wilcoxon
import seaborn as sns
from statannotations.Annotator import Annotator
import statannotations as annot

matplotlib.rcParams['grid.linewidth'] = 1
matplotlib.rcParams['axes.linewidth'] = 1
matplotlib.rcParams['font.size'] = 12
sns.set_style('ticks')
sns.set_context('paper')
save_fig = True

df = pd.read_csv('~/Documents/t1_mapping/results/slant_seg_results.csv')

# Create boxplot
print(df)

fig, ax = plt.subplots(figsize=(6,4), layout='constrained')
ax = sns.boxplot(
    data=df, 
    x='Tissue Type', 
    y='RMSE', 
    hue='Method',    
    hue_order=['lut', 's1_2', 's1_3', 'both'], 
    ax=ax
)

# Add significance annotations
pairs = [(
    ('WM', 'lut'), ('WM', 's1_2')), (('WM', 'lut'), ('WM', 's1_3')), (('WM', 'lut'), ('WM', 'both')),
    (('GM', 'lut'), ('GM', 's1_2')), (('GM', 'lut'), ('GM', 's1_3')), (('GM', 'lut'), ('GM', 'both')),
    (('Other', 'lut'), ('Other', 's1_2')), (('Other', 'lut'), ('Other', 's1_3')), (('Other', 'lut'), ('Other', 'both')),
    (('All', 'lut'), ('All', 's1_2')), (('All', 'lut'), ('All', 's1_3')), (('All', 'lut'), ('All', 'both'))
]
annotator = Annotator(ax, pairs, data=df, x='Tissue Type', y='RMSE', hue='Method', hue_order=['lut', 's1_2', 's1_3', 'both'])
annotator.configure(test='Wilcoxon')
annotator.apply_and_annotate()

# Change legend and y-axis labels
new_labels = ['Original point estimate T1', 'MAP T1 using $S_{1,2}$ only', 'MAP T1 using $S_{1,3}$ only', 'MAP T1 using $S_{1,2}$ and $S_{1,3}$']
handles, prev_labels = ax.get_legend_handles_labels()
ax.legend(
    handles=handles, 
    labels=new_labels,
)
ax.set_ylabel('RMSE (s)')

plt.show()

if save_fig:
    fig.savefig('/home/local/VANDERBILT/saundam1/Pictures/t1_mapping/mrm_figures/quant_results_seg.pdf', dpi=1200, bbox_inches='tight', transparent=True)