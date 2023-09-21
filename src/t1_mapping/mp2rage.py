import t1_mapping.utils
from functools import cached_property
import nibabel as nib
import numpy as np

class MP2RAGEFitter():
    def __init__(self, inv, acq_params: t1_mapping.utils.MP2RAGEParameters):
        """
        Fitter for calculations using an MP2RAGE sequence

        Parameters
        ----------
        inv : list of nibabel.nifti1.Nifti1Image or nibabel.nifti2.Nifti2Image
            List of gradient echo readouts, stored as NIFTI images
        acq_params : MP2RAGEParameters
            TypedDict containing acquisition parameters

        Attributes
        ----------
        t1w : nibabel.nifti2.Nifti2Image
            T1-weighted MP2RAGE image
        t1_map : nibabel.nifti2.Nifti2Image
            Quantitative T1 map
        """
        self.inv = inv
        self.acq_params = acq_params
        self.eqn_params = t1_mapping.utils.acq_to_eqn_params(acq_params)
        
        # Affine for later use
        self._affine = inv[0].affine

        # Initialize cached list of data so we don't have to recalculate
        self._inv_data = [None] * len(self.inv)

    def get_inv_data(self, index):
        if self._inv_data[index] is None:
            self._inv_data[index] = np.asanyarray(self.inv[index].get_fdata(dtype=np.complex64))
        return self._inv_data[index]


    @cached_property
    def t1w(self):
        t1w_array = t1_mapping.utils.mp2rage_t1w(self.get_inv_data(0), self.get_inv_data(1))
        return nib.nifti1.Nifti1Image(t1w_array, self._affine)
    
    @cached_property
    def t1_map(self):
        if len(self.inv) == 2:
            t1_map = t1_mapping.utils.mp2rage_t1_map([self.get_inv_data(0), self.get_inv_data(1)], **self.eqn_params)
        else:
            t1_map = np.zeros(self.get_inv_data(0).shape)
        return nib.nifti1.Nifti1Image(t1_map, self._affine)

# class MP2RAGEDataset():
#     def __init__(self):
#         """
#         Provides an interface between MP2RAGE dataset and calculation of T1-weighted image and T1 map.

#         Assumes a file structure of [subject]/[scan_name]/[scan_num]/[scan]

#         Parameters
#         ----------
#         dataset_path : t1w_niftistr
#             Path to directory containing the subjects
#         subjects_df : pandas.DataFrame
#             DataFrame containing 'subject', 'scan_name', 'scan_num' to use
#         output_path : str
#             Path to directory to place output T1 maps
#         """
#         self.inv1 = inv1
#         self.inv2 = inv2
#         self.acq_params = acq_params