# Determine scaling of MP2RAGE function inputs using non-linear least squares
import os
import scipy as sp
import numpy as np
import nibabel as nib

def f(X, a, b, c, d, e, f):
    # Simple scaling function
    GRE1, GRE2 = X
    GRE1_scaled = a*GRE1 + b
    GRE2_scaled = c*GRE2 + d
    S = GRE1_scaled*GRE2_scaled/(GRE1_scaled**2 + GRE2_scaled**2)
    return e*S+f

# Load example files from original MP2RAGE repo
folder = '/home/local/VANDERBILT/saundam1/Documents/MP2RAGE-related-scripts/data'
inv1 = nib.load(os.path.join(folder, 'MP2RAGE_INV1.nii'))
inv2 = nib.load(os.path.join(folder, 'MP2RAGE_INV2.nii'))
uni = nib.load(os.path.join(folder, 'MP2RAGE_UNI.nii'))

inv1_data = inv1.get_fdata()
inv2_data = inv2.get_fdata()
uni_data = uni.get_fdata()

print(inv1_data.dtype)

inv1_data = inv1_data.flatten()
inv2_data = inv2_data.flatten()
uni_data = uni_data.flatten()

xdata = [inv1_data, inv2_data]
ydata = uni_data
p0 = [1/4096, -1/2, 1/4096, -1/2, 4096, 2048]
popt, pcov = sp.optimize.curve_fit(f, xdata, ydata, p0)
print(popt)
print(np.diag(pcov))

