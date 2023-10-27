# Plot L(T1 | M1, M2) and sweep over T1
import t1_mapping
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Load subject
subj = t1_mapping.mp2rage.MP2RAGESubject(
    subject_id='334264',
    scan='401-x-WIPMP2RAGE_0p7mm_1sTI_best_oneSENSE-x-WIPMP2RAGE_0p7mm_1sTI_best_oneSENSE',
    scan_times=['1010', '3310', '5610']
)

# Load NumPy array for counts
counts = np.load(os.path.join(t1_mapping.definitions.SIMULATION_DATA, 'counts_1M.npy'))

# Calculate likelihoods
L_gauss = counts / np.sum(counts *subj.delta_m**2, axis=(0,1))
L_gauss = np.nan_to_num(L_gauss, nan=0)

uni_value = 1/(len(subj.m[0])*len(subj.m[1])*subj.delta_m**2)
L_uni = np.full((len(subj.m[0]), len(subj.m[1])), uni_value)

# Plot likelihood from Gaussian
fig = plt.figure()
ax1 = fig.add_subplot(1, 3, 1, projection='3d')
ax2 = fig.add_subplot(1, 3, 2, projection='3d')
ax3 = fig.add_subplot(1, 3, 3, projection='3d')
X,Y = np.meshgrid(subj.m[0], subj.m[1])

ax2.plot_surface(X, Y, L_uni)
ax2.set_xlabel('MP2RAGE_1')
ax2.set_ylabel('MP2RAGE_2')
ax2.set_zlabel(r'$\mathcal{L}$')
ax2.set_title(r'$\mathcal{L}$ from Uniform')
ax2.set_zlim([0, 100])

max_L_gauss = np.max(L_gauss, axis=2)
ax3.plot_surface(X, Y, np.max(L_gauss, axis=2))
ax3.set_xlabel('MP2RAGE_1')
ax3.set_ylabel('MP2RAGE_2')
ax3.set_zlabel(r'$\mathcal{L}$')
ax3.set_title(r'Max $\mathcal{L}$ from Gaussian')
ax3.set_zlim([0, 100])

def update(frame):
    ax1.clear()
    ax1.plot_surface(X, Y, L_gauss[:,:,frame])
    ax1.set_xlabel('MP2RAGE_1')
    ax1.set_ylabel('MP2RAGE_2')
    ax1.set_zlabel(fr'$\mathcal{{L}}$')
    ax1.set_title(fr'$\mathcal{{L}}(T_1 = {subj.t1[frame]:.2f})$ from Gaussian')
    ax1.set_zlim([0, 100])

# Create animation
num_frames = 100
ani = FuncAnimation(fig, update, frames=num_frames, blit=False)

# Save
# ani.save('examples/outputs/likelihood.mp4')

# Plot alpha using max likelihood
alpha = max_L_gauss / (max_L_gauss + L_uni)
fig3 = plt.figure()
ax4 = fig3.add_subplot(projection='3d')
ax4.plot_surface(X, Y, alpha)
ax4.set_xlabel('MP2RAGE_1')
ax4.set_ylabel('MP2RAGE_2')
ax4.set_zlabel(r'$\alpha$')
ax4.set_title(r'$\alpha$ using max likelihood')
ax4.set_zlim([0, 1])

plt.show()