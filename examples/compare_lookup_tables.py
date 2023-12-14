# Example to get max points on pcolormesh
import numpy as np
import matplotlib.pyplot as plt
import os
import t1_mapping

# Generating some sample data
# x = np.linspace(-2*np.pi, 2*np.pi, 100)
# y = np.linspace(-2*np.pi, 2*np.pi, 100)
# X, Y = np.meshgrid(x, y)
# Z = np.sin(0.5*Y + 0.1*X**2)
subj = t1_mapping.mp2rage.MP2RAGESubject(
    subject_id='334264',
    scan='401-x-WIPMP2RAGE_0p7mm_1sTI_best_oneSENSE-x-WIPMP2RAGE_0p7mm_1sTI_best_oneSENSE',
    scan_times=['1010', '3310'], #5610
    all_inv_combos=False
)
y = subj.t1
x = subj.m 
X,Y = np.meshgrid(x,y)
Z = np.load(os.path.join(t1_mapping.definitions.SIMULATION_DATA, 'counts_100M_s1_2.npy'))

# Calculate posterior distribution
Z = Z / np.sum(Z * np.prod(subj.delta_m), axis=tuple(range(len(subj.pairs)+1)))
print(np.sum(Z[0,:] * np.prod(subj.delta_m), axis=tuple(range(len(subj.pairs)))))
Z[Z == 0] = 1e-8

# Creating a pcolormesh plot
plt.figure(figsize=(8, 6))
# pcm = plt.pcolormesh(X, Y, Z, cmap='viridis')
pcm = plt.pcolormesh(x,y,Z, cmap='viridis', norm='log')
plt.colorbar(pcm, label='Z value')
plt.xlabel('X axis')
plt.ylabel('Y axis')
plt.title('Pcolormesh plot with Maximum Values along Vertical Grids')

# Find the indices of the maximum values along the columns
max_inds = np.argmax(Z, axis=0)

# Find the maximum values along the columns
max_vals = np.max(Z, axis=0)

# Get the x and y coordinates of the maximum values
x_coords = X[max_inds, np.arange(Z.shape[1])]
y_coords = Y[max_inds, np.arange(Z.shape[1])]

# Print the maximum values and their indices
print(max_vals, max_inds)

# Plot the maximum values
plt.plot(x_coords, y_coords, 'r.-')

# Plot counts for a couple values of m
counts = np.load(os.path.join(t1_mapping.definitions.SIMULATION_DATA, 'counts_100M_s1_2.npy'))
t1 = subj.t1
m = subj.m
fig, ax = plt.subplots()
for i in range(0, len(t1), 10):
    ax.plot(t1, counts[:,i])
    print(np.sum(counts[:,i] * subj.delta_t1))
ax.set_xlabel('T1')
ax.set_ylabel('Counts')
ax.set_title('Counts for different values of m')

# Now normalize to make PDF
fig, ax = plt.subplots()
for i in range(0, len(t1), 10):
    prob = counts[:,i] / np.sum(counts[:,i] * subj.delta_t1)
    print(np.sum(prob * subj.delta_t1))
    ax.plot(t1, prob)
ax.set_xlabel('T1')
ax.set_ylabel('Probability')
ax.set_title('Probability for different values of m')

prob = counts / np.sum(counts*subj.delta_t1, axis=0)
fig, ax = plt.subplots()
for i in range(0, len(t1), 10):
    print(np.sum(prob[:,i] * subj.delta_t1))
    ax.plot(t1, prob[:,i])
ax.set_xlabel('T1')
ax.set_ylabel('Probability')
ax.set_title('Probability for different values of m')

# Find the indices of the maximum values along the columns
max_inds = np.argmax(prob, axis=0)

# Find the maximum values along the columns
max_vals = np.max(prob, axis=0)

# Get the x and y coordinates of the maximum values
x_coords = X[max_inds, np.arange(prob.shape[1])]
y_coords = Y[max_inds, np.arange(prob.shape[1])]

# Print the maximum values and their indices
plt.figure(figsize=(8, 6))
prob[prob == 0] = 1e-8
# pcm = plt.pcolormesh(X, Y, Z, cmap='viridis')
pcm = plt.pcolormesh(x,y,prob, cmap='viridis', norm='log')
plt.colorbar(pcm, label='P(T1 | S_1,2) (log scale)')
ax.set_xlabel('$S_{1,2}$')
ax.set_ylabel('$T_1$ (s)')
print(max_vals, max_inds)

# Plot the maximum values
plt.plot(x_coords, y_coords, 'g.-', label='MAP using $S_{1,2}$ alone')


# Add LUT
# Get original point estimate LUT
GRE = t1_mapping.utils.gre_signal(
    T1=t1,
    **subj.eqn_params
)
m = t1_mapping.utils.mp2rage_t1w(GRE[0,:], GRE[1,:])

# Sort arrays
sorted_idx = np.argsort(m)
m = m[sorted_idx]
t1 = t1[sorted_idx]

# Pad LUT
m[0] = -0.5
m[-1] = 0.5

# Plot
plt.plot(m, t1, 'w.-', label='Original point estimate')
plt.xlabel('$S_{1,2}$')
plt.ylabel('$T_1$ (s)')
plt.legend()
plt.show()
