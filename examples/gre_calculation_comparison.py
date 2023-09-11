import numpy as np
import matplotlib.pyplot as plt
from t1_mapping.utils import gre_signal

T1 = np.linspace(0.5, 5, 1000)

input_params = {
    "T1": 2.5, 
    "inversion_times": [1.010, 3.310, 5.610],
    "TR": 6e-3, 
    "MP2RAGE_TR": 8.25, 
    "flip_angles": [4, 4, 4],
    "n": [225],
    "eff": 0.84
}

GRE = gre_signal(**input_params)
fig, ax = plt.subplots()
ax.plot(T1, GRE[0,:], c='r', label='GRE1')
ax.plot(T1, GRE[1,:], c='g', label='GRE2')
ax.plot(T1, GRE[2,:], c='b', label='GRE3')
ax.set_xlabel('T1 (s)')
ax.set_ylabel('Signal value')
ax.set_title('GRE values from 3 GRE blocks')
ax.legend()
plt.show()

# input_params = {
#     "TA": 0.335,
#     "TB": 0.95,
#     "TR": 6e-3,
#     "alpha_1": 4,
#     "alpha_2": 4,
#     "n": 225,
#     "MP2RAGE_TR": 8.25,
#     "eff": 0.84
# }

# GRE1_orig, GRE2_orig = gre_signal(T1=T1, **input_params, method='code')
# GRE1_paper, GRE2_paper = gre_signal(T1=T1, **input_params, method='paper')

# fig, ax = plt.subplots()
# ax.plot(T1, GRE1_orig, c='r', ls=':', label='Marques code GRE1')
# ax.plot(T1, GRE1_paper, c='r', ls='-', label='Marques paper GRE1')
# ax.plot(T1, GRE2_orig, c='g', ls=':', label='Marques code GRE2')
# ax.plot(T1, GRE2_paper, c='g', ls='-', label='Marques paper GRE2')
# ax.set_xlabel('T1 (s)')
# ax.set_ylabel('Signal value')
# ax.set_title('Comparison of GRE equations')
# ax.legend()
# plt.show()

# # Should be true if paper matches code
# print(np.all(GRE1_paper == GRE1_orig))
# print(np.all(GRE2_paper == GRE2_orig))