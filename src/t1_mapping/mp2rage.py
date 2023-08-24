import t1_mapping.utils
from functools import cached_property
import nibabel as nib
import numpy as np

class MP2RAGEFitter():
    def __init__(self, inv1, inv2, acq_params):
        """
        Fitter for calculations using an MP2RAGE sequence

        Parameters
        ----------
        inv1 : nibabel.nifti1.Nifti1Image or nibabel.nifti2.Nifti2Image
            First gradient echo readout, stored as a NIFTI image
        inv2 : nibabel.nifti1.Nifti1Image or nibabel.nifti2.Nifti2Image
            Second gradient echo readout, stored as a NIFTI image
        acq_params : Dict
            Dictionary containing acquisition parameters

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

    @cached_property
    def _inv1_data(self):
        return np.asanyarray(self.inv1.dataobj)
    
    @cached_property
    def _inv2_data(self):
        return np.asanyarray(self.inv2.dataobj)

    @cached_property
    def t1w(self):
        t1w_array = t1_mapping.utils.mp2rage_t1w(self._inv1_data, self._inv2_data)
        return nib.nifti2.Nifti2Image(t1w_array, self.inv1.affine)