# Plot MP2RAGE signaling equation as a function of each of its parameters
# Some code generated using ChatGPT

import numpy as np
import matplotlib.pyplot as plt
from math import ceil
import t1_mapping
import itertools

# Parameter ranges for the sweep
acq_params : t1_mapping.utils.MP2RAGEParameters = {
            "MP2RAGE_TR": 8.25,
            "TR": 0.006,
            "flip_angles": [4, 4, 4],
            "inversion_times": [1.010, 3.310, 5.610],
            "n": [225],
            "eff": 0.84,
        }
t1 = np.arange(0.05, 5, 0.05)
eqn_params = t1_mapping.utils.acq_to_eqn_params(acq_params)

GRE = t1_mapping.utils.gre_signal(T1=t1, **eqn_params)
pairs = itertools.combinations(range(len(GRE)), 2)
MP2RAGE = [t1_mapping.utils.mp2rage_t1w(GRE[i[0],:], GRE[i[1],:]) for i in pairs]
print('Range of MP2RAGE calculations: ', [(np.min(m), np.max(m)) for m in MP2RAGE])
