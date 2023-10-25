# Plot relative likelihood from multiple angles
import t1_mapping
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Load subject
subj = t1_mapping.mp2rage.MP2RAGESubject(
    subject_id='334264',
    scan='401-x-WIPMP2RAGE_0p7mm_1sTI_best_oneSENSE-x-WIPMP2RAGE_0p7mm_1sTI_best_oneSENSE',
    scan_times=['1010', '3310', '5610'], 
    all_inv_combos=True
)

# Load NumPy array for counts
counts = np.load(os.path.join(t1_mapping.definitions.SIMULATION_DATA, 'counts_1M_full.npy'))

n_pairs = len(subj.scan_times)
n_readouts = len(subj.inv_json)

# Calculate likelihoods
L_gauss = counts / np.sum(counts *subj.delta_m**(n_pairs-1), axis=tuple(range(n_pairs)))
L_gauss = np.nan_to_num(L_gauss, nan=0)

# Maximum likelihood of gaussian
max_L_gauss = np.max(L_gauss, axis=-1)

# Uniform likelihood
m_squares = np.array([len(mp2rage) for mp2rage in subj.m])
total_squares = np.prod(m_squares)
uni_value = 1/(total_squares*subj.delta_m**n_pairs)
L_uni = np.full(tuple(m_squares), uni_value)

# Relative likelihood
alpha = max_L_gauss / (max_L_gauss + L_uni)

print(alpha.shape)

fig = plt.figure()
for i, pair in enumerate(subj.pairs):
    print(i, pair)
    ax = fig.add_subplot(1, 3, i+1, projection='3d')
    X, Y = np.meshgrid(subj.m[pair[0]], subj.m[pair[1]])
    alpha_view = alpha.take(indices=50, axis=2-i)
    ax.plot_surface(X, Y, alpha_view)
    ax.set_zlim([0, 1])
    ax.set_xlabel(f'M{pair[0]}')
    ax.set_ylabel(f'M{pair[1]}')
    ax.set_zlabel(r'$\alpha$')

# fig3 = plt.figure()
# ax4 = fig3.add_subplot(projection='3d')
# ax4.plot_surface(X, Y, alpha)
# ax4.set_xlabel('MP2RAGE_1')
# ax4.set_ylabel('MP2RAGE_2')
# ax4.set_zlabel(r'$\alpha$')
# ax4.set_title(r'$\alpha$ using max likelihood')
# ax4.set_zlim([0, 1])

plt.show()