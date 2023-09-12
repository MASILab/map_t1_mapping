import numpy as np
import matplotlib.pyplot as plt
from t1_mapping.utils import gre_signal, gre_signal_two

T1 = np.linspace(0.5, 5, 1000)

# Plot 3 GREs
input_params3 = {
    "T1": T1, 
    "inversion_times": [1.010, 3.310, 5.610],
    "TR": 6e-3, 
    "MP2RAGE_TR": 8.25, 
    "flip_angles": [4, 4, 4],
    "n": [225],
    "eff": 0.84
}

GRE_3 = gre_signal(**input_params3)
fig, ax = plt.subplots()
ax.plot(T1, GRE_3[0,:], c='r', label='GRE1')
ax.plot(T1, GRE_3[1,:], c='g', label='GRE2')
ax.plot(T1, GRE_3[2,:], c='b', label='GRE3')
ax.set_xlabel('T1 (s)')
ax.set_ylabel('Signal value')
ax.set_title('GRE values from 3 GRE blocks')
ax.legend()

# Compare old equations
input_params = {
    "TA": 0.335,
    "TB": 0.95,
    "TR": 6e-3,
    "alpha_1": 4,
    "alpha_2": 4,
    "n": 225,
    "MP2RAGE_TR": 8.25,
    "eff": 0.84
}

GRE1_orig, GRE2_orig = gre_signal_two(T1=T1, **input_params, method='code')

input_params2 = {
    "T1": T1, 
    "inversion_times": [1.010, 3.310],
    "TR": 6e-3, 
    "MP2RAGE_TR": 8.25, 
    "flip_angles": [4, 4],
    "n": [225],
    "eff": 0.84
}

GRE_2 = gre_signal(**input_params2)

fig, ax = plt.subplots()
ax.plot(T1, GRE1_orig, c='r', ls=':', label='Original GRE1')
ax.plot(T1, GRE2_orig, c='g', ls=':', label='Original GRE2')
ax.plot(T1, GRE_2[0,:], c='r', ls='-', label='New GRE1')
ax.plot(T1, GRE_2[1,:], c='g', ls='-', label='New GRE2')
ax.set_xlabel('T1 (s)')
ax.set_ylabel('Signal value')
ax.set_title('Comparison of GRE equations')
ax.legend()
plt.show()