# Generate figure 4: quantitative results (group)
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

matplotlib.rcParams['grid.linewidth'] = 1
matplotlib.rcParams['axes.linewidth'] = 1
matplotlib.rcParams['font.size'] = 12
sns.set_style('ticks')
sns.set_context('paper')
save_fig = True

df = pd.read_csv('~/Documents/t1_mapping/results/quant_results.csv')

# Create violin plot (with stripplot for points)
fig, ax = plt.subplots(figsize=(6,4))
sns.stripplot(data=df, x='Method', y='RMSE', color='black', jitter=0, size=3, order=['lut', 's1_2', 's1_3', 'both'])
sns.violinplot(
    data=df, 
    x='Method', 
    y='RMSE', 
    inner='quartile', 
    cut=0, 
    order=['lut', 's1_2', 's1_3', 'both'], 
)

# Customize labels
ax.set_xticklabels(['Original point\nestimate T1', 'MAP T1 using\n$S_{1,2}$ only', 'MAP T1 using\n$S_{1,3}$ only', 'MAP T1 using\n$S_{1,2}$ and $S_{1,3}$'])
ax.set_xlabel('Method')
ax.set_ylabel('RMSE (s)')

# Add significance annotations
pairs = [('lut', 's1_2'), ('lut', 's1_3'), ('lut', 'both')]
annotator = Annotator(ax, pairs=pairs, data=df, x='Method', y='RMSE')
annotator.configure(test='Wilcoxon')
annotator.apply_and_annotate()

plt.show()

if save_fig:
    fig.savefig('/home/local/VANDERBILT/saundam1/Pictures/t1_mapping/mrm_figures/quant_results.pdf', dpi=1200, bbox_inches='tight', transparent=True)