# Compare MI of MP2RAGE images
import numpy as np
import os
import t1_mapping
import nibabel as nib 
import matplotlib.pyplot as plt

m1 = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 't1_maps_likelihood_rigid', '334264', 'mp2rage_1.nii.gz'))
m2 = nib.load(os.path.join(t1_mapping.definitions.OUTPUTS, 't1_maps_likelihood_rigid', '334264', 'mp2rage_2.nii.gz'))

ground_truth = nib.load(os.path.join(t1_mapping.definitions.GROUND_TRUTH_DATA, '334264', 'filtered_t1_map.nii'))
ground_truth_data = ground_truth.get_fdata()
ground_truth_data[ground_truth_data == np.inf] = 0
mask = ground_truth_data > 0

m1_data = m1.get_fdata()[mask]
m2_data = m2.get_fdata()[mask]

# Calculate MI
bins = 256
hist_2d, x_edges, y_edges = np.histogram2d(m1_data, m2_data, bins=bins)

# Normalize the histograms
pdf = hist_2d / np.sum(hist_2d)

fig, ax = plt.subplots()
ax.imshow(pdf)
ax.set_xlabel('$S_{1,2}$')
ax.set_ylabel('$S_{1,3}$')
ax.set_title('$P(S_{1,2}, S_{1,3})$')

# Calculate marginal histograms
hist_x = np.sum(pdf, axis=1)
hist_y = np.sum(pdf, axis=0)

pdf_x = hist_x / np.sum(hist_x)
pdf_y = hist_y / np.sum(hist_y)

# Calculate mutual information
eps = np.finfo(float).eps  # small epsilon value to avoid log(0)
mutual_info = 0.0
entropy1 = 0.0
entropy2 = 0.0
joint_entropy = 0.0
for i in range(bins):
    for j in range(bins):
        if pdf[i, j] > 0:
            mutual_info += pdf[i, j] * np.log((pdf[i, j] + eps) /
                (pdf_x[i] * pdf_y[j] + eps))
            joint_entropy += -pdf[i,j]*np.log(pdf[i,j] + eps)

for i in range(bins):
    entropy1 += -pdf_x[i]*np.log(pdf_x[i] + eps)
    entropy2 += -pdf_y[i]*np.log(pdf_y[i] + eps)

normalized_mi = mutual_info/np.sqrt(entropy1*entropy2)

print(f"The mutual information between the images is {mutual_info:.4f}")
print(f"The normalized mutual information between the images is {normalized_mi:.4f}")

corr = np.corrcoef(m1_data, m2_data)
print(f'The correlation coefficient is {corr[0,1]:.4f}')

plt.show()