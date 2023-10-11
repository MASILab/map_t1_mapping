import numpy as np

# Example data (replace with your actual data)
M = np.array([[1.0, 2.0],
              [3.0, 4.0],
              [5.0, 6.0],
              [7.0, 8.0]])

A = np.array([[1.5, 2.5],
              [3.8, 4.2]])

print(M.shape)
print(A.shape)
# Calculate the Euclidean distances between all points in A and M
distances = np.sqrt(np.sum((M[:, np.newaxis, :] - A) ** 2, axis=2))

# Find the indices of the closest points in M for each point in A
closest_indices = np.argmin(distances, axis=0)

# The array closest_indices now contains the indices of the closest points in M for each point in A
print(closest_indices)
print(M[closest_indices])