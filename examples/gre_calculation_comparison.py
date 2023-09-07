import numpy as np
import matplotlib.pyplot as plt
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

GRE1_orig, GRE2_orig = gre_signal(T1=T1, **input_params, method='code')
GRE1_paper, GRE2_paper = gre_signal(T1=T1, **input_params, method='paper')

fig, ax = plt.subplots()
ax.plot(T1, GRE1_orig, c='r', ls=':', label='Marques code GRE1')
ax.plot(T1, GRE1_paper, c='r', ls='-', label='Marques paper GRE1')
ax.plot(T1, GRE2_orig, c='g', ls=':', label='Marques code GRE2')
ax.plot(T1, GRE2_paper, c='g', ls='-', label='Marques paper GRE2')
ax.set_xlabel('T1 (s)')
ax.set_ylabel('Signal value')
ax.set_title('Comparison of GRE equations')
ax.legend()
plt.show()

# Should be true if paper matches code
print(np.all(GRE1_paper == GRE1_orig))
print(np.all(GRE2_paper == GRE2_orig))