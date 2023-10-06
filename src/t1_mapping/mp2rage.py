import t1_mapping.utils
import t1_mapping.definitions
from functools import cached_property
import nibabel as nib
import numpy as np
import os
import json

class MP2RAGEFitter():
    def __init__(self, inv, acq_params: t1_mapping.utils.MP2RAGEParameters):
        """
        Fitter for calculations using an MP2RAGE sequence

        Parameters
        ----------
        inv : list of nibabel.nifti1.Nifti1Image
            List of gradient echo readouts, stored as NIFTI images
        acq_params : MP2RAGEParameters
            TypedDict containing acquisition parameters

        Attributes
        ----------
        t1w : nibabel.nifti1.Nifti1Image
            T1-weighted MP2RAGE image
        t1_map : nibabel.nifti1.Nifti1Image
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

class MP2RAGESubject():
    def __init__(self, subject, scan, scan_times):
        """
        Class to store MP2RAGE subject data

        Parameters
        ---------
        subject : str
            Subject number
        scan : str
            Full scan name
        scan_times : list of str
            List of scan times to load

        Attributes
        --------
        inv : list of nibabel.nifti1.Nifti1Image
            List of NIFTIs loaded from scan times
        inv_json : list of dictionaries
            JSON dictionaries from subject
        t1w : nibabel.nifti1.Nifti1Image
            T1-weighted MP2RAGE image
        t1_map : nibabel.nifti1.Nifti1Image
            Quantitative T1 map
        mp2rage : list of nibabel.nifti1.Nifti1Image
            List of pairwise MP2RAGE T1-weighted images (0,1), (0,2), ... (1,2), ...
        acq_params : list of acquisition parameters
        eqn_params : list of equation parameters
        """
        self.subject = subject
        self.scan = scan
        self.scan_times = scan_times

        # Load dataset paths
        self.scan_num = self.scan.split('-', 1)[0]
        self.subject_path = os.path.join(t1_mapping.definitions.DATA, self.subject, self.scan)

    @cached_property
    def inv(self):
        inv = []
        for t in self.scan_times:
            # Load NIFTI
            inv_real = nib.load(os.path.join(self.subject_path, f'{self.scan_num}_real_t{t}.nii'))
            inv_imag = nib.load(os.path.join(self.subject_path, f'{self.scan_num}_imaginary_t{t}.nii'))

            # Get data from NIFTI
            inv_real_data = inv_real.get_fdata()
            inv_imag_data = inv_imag.get_fdata()

            # Create combined complex data
            inv_data = inv_real_data + 1j*inv_imag_data

            # Create NIFTI
            inv.append(nib.nifti1.Nifti1Image(inv_data, inv_real.affine))
        return inv
    
    @cached_property
    def inv_json(self):
        inv_json = []
        # Load JSON
        for t in self.scan_times:
            with open(os.path.join(self.subject_path, f'{self.scan_num}_t{t}.json'), 'r') as f:
                inv_json.append(json.load(f))
        return inv_json

    @property
    def acq_params(self):
        # Load acquisition parameters
        params : t1_mapping.utils.MP2RAGEParameters = {
            "MP2RAGE_TR": 8.25,
            "TR": self.inv_json[0]["RepetitionTime"],
            "flip_angles": [i['FlipAngle'] for i in self.inv_json],
            "inversion_times": [i['TriggerDelayTime']/1000 for i in self.inv_json],
            "n": [225],
            "eff": 0.84,
        }
        return params

    @property
    def _fitter(self):
        fitter = MP2RAGEFitter(self.inv, self.acq_params)
        return fitter
    
    @property
    def eqn_params(self):
        return self._fitter.eqn_params

    @cached_property
    def t1w(self):
        return self._fitter.t1w
    
    @cached_property
    def t1_map(self):
        return self._fitter.t1_map

    @cached_property
    def mp2rage(self):
        mp2rage = []
        for i in range(len(self.inv)):
            for j in range(i+1, len(self.inv)):
                mp2rage.append(t1_mapping.utils.mp2rage_t1w(self.inv[i].get_fdata(dtype=np.complex64), self.inv[j].get_fdata(dtype=np.complex64)))
        return mp2rage

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