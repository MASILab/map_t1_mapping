# Example of mode changing when we add noise to transformation
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm

# Generating a deterministic distribution where all values are 5
deterministic_values = np.full(10000, 5)

# Transformation function (adding 3 to each value)
def transformation(values):
    return 0.1*np.exp(values)

# Applying a transformation to the deterministic values
transformed_deterministic_values = transformation(deterministic_values)

# Adding Gaussian noise to deterministic values
gaussian_noise = np.random.normal(0, 1, 10000)
noisy_values = deterministic_values + gaussian_noise

# Applying the same transformation to the noisy values
transformed_noisy_values = transformation(noisy_values)

# Plotting PDFs
plt.figure(figsize=(12, 8))
bins = np.arange(0,30)

# Deterministic Distribution PDFs
plt.subplot(2, 2, 1)
plt.hist(deterministic_values, bins=bins, density=True, color='blue', alpha=0.7)
plt.title('Deterministic Distribution (Before Transformation)')
plt.xlabel('Values')
plt.ylabel('Density')

plt.subplot(2, 2, 2)
plt.hist(transformed_deterministic_values, bins=bins, density=True, color='orange', alpha=0.7)
plt.title('Deterministic Distribution (After Transformation)')
plt.xlabel('Values')
plt.ylabel('Density')

# Noisy Distribution PDFs
plt.subplot(2, 2, 3)
plt.hist(noisy_values, bins=bins, density=True, color='green', alpha=0.7)
plt.title('Noisy Distribution (Before Transformation)')
plt.xlabel('Values')
plt.ylabel('Density')

plt.subplot(2, 2, 4)
plt.hist(transformed_noisy_values, bins=bins, density=True, color='red', alpha=0.7)
plt.title('Noisy Distribution (After Transformation)')
plt.xlabel('Values')
plt.ylabel('Density')

plt.tight_layout()
plt.show()
