import numpy as np
from t1_mapping.utils import gre_signal

T1 = np.linspace(0.5, 5, 1000)

input_params = {
    "TA": 1,
    "TB": 1,
    "TC": 1,
    "TR": 6e-3,
    "alpha_1": 4,
    "alpha_2": 4,
    "n": 36,
    "MP2RAGE_TR": 6,
    "eff": 0.96
}

GRE1_orig, GRE2_orig = gre_signal(T1=T1, **input_params, method='marques_orig')
GRE1_single, GRE2_single = gre_signal(T1=T1, **input_params, method='marques_single')

print(GRE1_orig == GRE1_single)
print(GRE2_orig == GRE2_single)