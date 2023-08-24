import t1_mapping.utils

class MP2RAGEFitter():
    def __init__(self):
        """
        Fitter for calculations using an MP2RAGE sequence

        Parameters
        ----------
        inv1 : str
            Filename of first gradient echo readout
        inv2 : str
            Filename of second gradient echo readout
        acq_params : Dict
            Dictionary containing acquisition parameters

        Attributes
        ----------
        t1_w : nibabel.nifti2.Nifti2Image
            T1-weighted MP2RAGE image
        t1_map : nibabel.nifti2.Nifti2Image
            Quantitative T1 map
        """
