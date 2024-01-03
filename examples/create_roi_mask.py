import numpy as np
from scipy.spatial import ConvexHull
from skimage.draw import polygon

# Example list of 3D points defining the boundary
points = [
    [10, 20, 0],
    [10, 40, 0],
    [30, 40, 0],
    [30, 20, 0],
    # Repeat the first point to close the polygon
    [10, 20, 0],
]

# Convert the boundary points to 2D by ignoring the third dimension
boundary_2d = np.array(points)[:, :2]

# Calculate the convex hull of the boundary points
hull = ConvexHull(boundary_2d)

# Get the vertices of the convex hull
vertices = hull.vertices

# Create a mask array with zeros
mask_shape = np.max(boundary_2d, axis=0) + 1
mask = np.zeros(mask_shape, dtype=bool)

# Generate a filled polygon inside the convex hull
rr, cc = polygon(boundary_2d[vertices, 1], boundary_2d[vertices, 0], mask_shape)
mask[rr, cc] = 1

# Now 'mask' is a binary array mask with the area enclosed by the boundary points filled with ones (True)
