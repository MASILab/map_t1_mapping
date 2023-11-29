# Compare dicom headers of subjects 334264 and 336547
import os
import pydicom

# Get dicom headers
dcm_normal = pydicom.dcmread('/nfs/masi/saundam1/datasets/MP2RAGE/334264/334264/401-x-WIPMP2RAGE_0p7mm_1sTI_best_oneSENSE-x-WIPMP2RAGE_0p7mm_1sTI_best_oneSENSE/DICOM/1.3.46.670589.11.9904.5.0.6620.2018041810422588000-401-1-zrtqjq.dcm', stop_before_pixels=True)
dcm_odd = pydicom.dcmread('/nfs/masi/saundam1/datasets/MP2RAGE/336547/336547/1101-x-MP2RAGE_0p8mm_1sTI_autoshim-x-MP2RAGE_0p8mm_1sTI_autoshim/DICOM/1.3.46.670589.11.9904.5.0.9528.2019021314591912000-1101-1-9s5np1.dcm', stop_before_pixels=True)

# Loop through tags and print different ones
for elem in dcm_normal: #.iterall():
    if elem.is_empty or elem.is_private:
        continue
    if dcm_normal[elem.tag] != dcm_odd[elem.tag]:
        print(f'>{elem.tag}: {dcm_normal[elem.tag]}')
        print(f'<{elem.tag}: {dcm_odd[elem.tag]}')

# Also loop through first frame sequence
for elem in dcm_normal[0x5200,0x9230][0]:
    if elem.is_empty or elem.is_private:
        continue
    if dcm_normal[0x5200,0x9230][0][elem.tag] != dcm_odd[0x5200,0x9230][0][elem.tag]:
        print(f'>{elem.tag}: {dcm_normal[0x5200,0x9230][0][elem.tag].value}')
        print(f'<{elem.tag}: {dcm_odd[0x5200,0x9230][0][elem.tag].value}')