# Creates a quantitative T1 map from MP2RAGE sequence
# Uses data from the CEREBRUM-7T dataset
# See https://github.com/Gilles86/pymp2rage/blob/master/notebooks/MP2RAGE%20and%20T1%20fitting.ipynb
import os
import json
import nibabel as nib
import pymp2rage


# Load dataset paths
dataset_path = '/home/saundam1/Datasets/ds003642'
subject_path = os.path.join(dataset_path, 'sub-025', 'ses-003', 'anat')

# Load JSON
inv1_json_path = os.path.join(subject_path, 'sub-025_ses-003_INV1.json')
inv2_json_path = os.path.join(subject_path, 'sub-025_ses-003_INV2.json')
with open(inv1_json_path, 'r') as f1, open(inv2_json_path, 'r') as f2:
    inv1_json = json.load(f1)
    inv2_json = json.load(f2)

# Load NIFTI files
inv1_path = os.path.join(subject_path, 'sub-025_ses-003_INV1.nii.gz')
inv2_path = os.path.join(subject_path, 'sub-025_ses-003_INV2.nii.gz')
inv1 = nib.load(inv1_path)
inv2 = nib.load(inv2_path)

# Load acquisition parameters
MPRAGE_tr = inv1_json['RepetitionTime']
invtimesAB = [inv1_json['InversionTime'], inv2_json['InversionTime']]
flipangleABdegree =[inv1_json['FlipAngle'], inv2_json['FlipAngle']]
nZslices = 150
FLASH_tr=[0.0062, 0.03]
sequence = 'normal'
inversion_efficiency = 0.63
B0 = 7

# Create MP2RAGE fitter
fitter = pymp2rage.MP2RAGE(MPRAGE_tr = MPRAGE_tr,
                           invtimesAB = invtimesAB,
                           flipangleABdegree = flipangleABdegree,
                           nZslices = nZslices,
                           FLASH_tr = FLASH_tr,
                           sequence = sequence,
                           inversion_efficiency = inversion_efficiency,
                           B0 = B0,
                           inv1_combined = inv1,
                           inv2_combined = inv2)