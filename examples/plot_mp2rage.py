# Plot MP2RAGE signaling equation as a function of each of its parameters
# Some code generated using ChatGPT

import numpy as np
import matplotlib.pyplot as plt
from math import ceil
from t1_mapping.utils import GRE

# Parameter ranges for the sweep
param_ranges = {
    "T1": np.linspace(0.5, 5, 100),
    "TA": np.linspace(0.2, 1, 100),
    "TB": np.linspace(0.2, 1, 100),
    "TC": np.linspace(0.2, 1, 100),
    "TR": np.linspace(3e-3, 9e-3, 100),
    "alpha_1": np.linspace(3, 7, 100),
    "alpha_2": np.linspace(3, 7, 100),
    "n": np.arange(20, 60, 2),
    "MP2RAGE_TR": np.linspace(3, 6, 100),
    "eff": np.linspace(0.8, 1, 100)
}

# Defaults for parameters not swept
param_defaults = {
    "T1": 0.5,
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

# Create subplots
num_params = len(param_ranges)
num_cols = 5
num_rows = 2

fig, axes = plt.subplots(num_rows, num_cols, figsize=(18, 4))
axes = axes.flatten()

for i, param in enumerate(param_ranges):
    input_params = param_defaults.copy()
    input_params[param] = param_ranges[param]

    ax = axes[i]
    GRE1_values, GRE2_values = GRE(**input_params)
    ax.plot(param_ranges[param], GRE1_values)
    ax.plot(param_ranges[param], GRE2_values)
    ax.set_title(f"GRE vs. {param}")
    ax.set_xlabel(param)
    ax.set_ylabel("GRE value")
    fig.suptitle("GRE1 (blue) and GRE2 (orange) for varying parameters")

# Adjust layout
plt.tight_layout()

# Show the plots
plt.show()
