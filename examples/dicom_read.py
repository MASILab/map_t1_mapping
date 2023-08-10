# Reads an example DICOM file to extract header information
import os
import glob
from pydicom import dcmread

# Load folder
subject = '334264'
scan = '401-x-WIPMP2RAGE_0p7mm_1sTI_best_oneSENSE-x-WIPMP2RAGE_0p7mm_1sTI_best_oneSENSE'
scan_num = '401'
dataset_path = '/nfs/masi/saundam1/Datasets/MP2RAGE/'
subject_path = os.path.join(dataset_path, subject, subject, scan, 'DICOM')

# Load DICOM 
dicom_path = os.path.join(subject_path, '*.dcm')
dicom_file = glob.glob(dicom_path)
ds = dcmread(dicom_file[0])

# Print info to file
output_path = os.path.join(os.path.dirname('.'), 'outputs', f'{subject}_{scan_num}_dicom_info.txt')
with open(output_path, 'w') as f:
    f.write(str(ds))