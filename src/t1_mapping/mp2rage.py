import t1_mapping.utils
from functools import cached_property
import nibabel as nib
import numpy as np
from typing import TypedDict

class MP2RAGEParameters(TypedDict):
    """
    TypedDict containing acquisition parameters.

    Parameters
    ----------
    TR : float
        Repitition time of the gradient echo readout in s
    MP2RAGE_TR : float
        Time between inversion pulses in s
    flip_angles : list of floats
        Flip angles of gradient echo pulses in deg
    inversion_times : list of floats
        Time from inversion pulse to middle of each gradient echo readout
    n : int
        Number of pulses within each gradient echo readout
    eff : float
        Inversion efficiency of scanner
    """
    TR: float
    MP2RAGE_TR: float
    flip_angles: list
    inversion_times: list
    n: int
    eff: float

class MP2RAGEFitter():
    def __init__(self, inv1, inv2, acq_params: MP2RAGEParameters):
        """
        Fitter for calculations using an MP2RAGE sequence

        Parameters
        ----------
        inv1 : nibabel.nifti1.Nifti1Image or nibabel.nifti2.Nifti2Image
            First gradient echo readout, stored as a NIFTI image
        inv2 : nibabel.nifti1.Nifti1Image or nibabel.nifti2.Nifti2Image
            Second gradient echo readout, stored as a NIFTI image
        acq_params : MP2RAGEParameters
            TypedDict containing acquisition parameters

        Attributes
        ----------
        t1w : nibabel.nifti2.Nifti2Image
            T1-weighted MP2RAGE image
        t1_map : nibabel.nifti2.Nifti2Image
            Quantitative T1 map
        """
        self.inv1 = inv1
        self.inv2 = inv2
        self.acq_params = acq_params

        # Use acquisition parameters to calculate equation parameters
        self.eqn_params = {
            "TA": self.acq_params["inversion_times"][0] - self.acq_params["n"]/2*self.acq_params["TR"],
            "TR": self.acq_params["TR"],
            "alpha_1": self.acq_params["flip_angles"][0],
            "alpha_2": self.acq_params["flip_angles"][1],
            "n": self.acq_params["n"],
            "MP2RAGE_TR": self.acq_params["MP2RAGE_TR"],
            "eff": self.acq_params["eff"]
        }
        self.eqn_params["TB"] = self.acq_params["inversion_times"][1] - self.acq_params["inversion_times"][0] - self.eqn_params["TA"]
        self.eqn_params["TC"] = self.acq_params["MP2RAGE_TR"] - self.acq_params["inversion_times"][1] - self.eqn_params["TA"]/2

    @cached_property
    def _inv1_data(self):
        return np.asanyarray(self.inv1.dataobj)
    
    @cached_property
    def _inv2_data(self):
        return np.asanyarray(self.inv2.dataobj)

    @cached_property
    def t1w(self):
        t1w_array = t1_mapping.utils.mp2rage_t1w(self._inv1_data, self._inv2_data)
        return nib.nifti1.Nifti1Image(t1w_array, self.inv1.affine)
    
    @cached_property
    def t1_map(self):
        t1_map = t1_mapping.utils.mp2rage_t1_map(self._inv1_data, self._inv2_data, **self.eqn_params)
        return nib.nifti1.Nifti1Image(t1_map, self.inv1.affine)

# class MP2RAGEDataset():
#     def __init__(self):
#         """
#         Provides an interface between MP2RAGE dataset and calculation of T1-weighted image and T1 map.

#         Assumes a file structure of [subject]/[scan_name]/[scan_num]/[scan]

#         Parameters
#         ----------
#         dataset_path : str
#             Path to directory containing the subjects
#         subjects_df : pandas.DataFrame
#             DataFrame containing 'subject', 'scan_name', 'scan_num' to use
#         output_path : str
#             Path to directory to place output T1 maps
#         """
#         self.inv1 = inv1
#         self.inv2 = inv2
#         self.acq_params = acq_params