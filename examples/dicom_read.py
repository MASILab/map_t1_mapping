# Reads an example DICOM file to extract header information
import os
import glob
from pydicom import dcmread

# Load data 
dataset_path = "/nfs/masi/saundam1/Datasets/MP2RAGE/336195/336195/1101-x-WIPMP2RAGE_0p8mm_1sTI_autoshimSENSE-x-WIPMP2RAGE_0p8mm_1sTI_autoshimSENSE/"
dicom_path = os.path.join(dataset_path, 'DICOM', '*.dcm')
dicom_file = glob.glob(dicom_path)
ds = dcmread(dicom_file[0])

# Print info to file
output_path = os.path.join(os.path.dirname('.'), 'outputs', 'dicom_info.txt')
with open(output_path, 'w') as f:
    f.write(str(ds))