# Plot MP2RAGE signaling equation as a function of each of its parameters

import numpy as np
import matplotlib.pyplot as plt

# Define the GRE1 function
print(MP2RAGE(M0=[2, 3, 4]))

# Parameter ranges for the sweep
param_ranges = {
    "M0": np.linspace(0, 1, 100),
    "T1": np.linspace(0, 10, 100),
    "TA": np.linspace(0, 2, 100),
    "TB": np.linspace(1, 5, 100),
    "TC": np.linspace(0, 0.5, 100)
}

# Create subplots
num_params = len(param_ranges)
num_cols = 2
num_rows = (num_params + 1) // num_cols

fig, axes = plt.subplots(num_rows, num_cols, figsize=(12, 10))
axes = axes.flatten()

for i, (param_name, param_values) in enumerate(param_ranges.items()):
    ax = axes[i]
    GRE1_values = GRE1(param_values, param_ranges["T1"][0], param_ranges["TA"][0], param_ranges["TB"][0], param_ranges["TC"][0])
    ax.plot(param_values, GRE1_values)
    ax.set_title(f"GRE1 vs. {param_name}")
    ax.set_xlabel(param_name)
    ax.set_ylabel("GRE1")

# Adjust layout
plt.tight_layout()

# Show the plots
plt.show()
