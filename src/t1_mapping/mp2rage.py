import t1_mapping.utils
import t1_mapping.definitions
from functools import cached_property
import itertools
import nibabel as nib
import numpy as np
import os
import json

class MP2RAGESubject():
    def __init__(self, subject_id, scan, scan_times, monte_carlo=None, all_inv_combos=False):
        """
        Class to store MP2RAGE subject data

        Parameters
        ---------
        subject_id : str
            Subject number
        scan : str
            Full scan name
        scan_times : list of str
            List of scan times to load
        monte_carlo : str
            Monte Carlo simulation counts used for likelihood method
        all_inv_combos : bool, by default False
            If True, use all combinations of inversion readouts for calculation 
            (n choose 2). Otherwise, use sequential pairs (n - 1).

        Attributes
        --------
        inv : list of nibabel.Nifti1Image
            List of NIFTIs loaded from scan times
        inv_json : list of dictionaries
            JSON dictionaries from subject
        affine : ndarray
            Affine transformation for subject position
        t1w : nibabel.Nifti1Image
            T1-weighted MP2RAGE image
        t1_map : nibabel.Nifti1Image
            Quantitative T1 map
        mp2rage : list of nibabel.Nifti1Image
            List of MP2RAGE T1-weighted images based on pairs
        acq_params : list 
            acquisition parameters, see t1_mapping.utils.MP2RAGEParameters
        eqn_params : list 
            equation parameters, see t1_mapping.utils.EquationParameters
        t1 : NumPy array
            list of possible T1 values
        m : list of NumPy arrays 
            MP2RAGE values in Monte Carlo simulation indices
        m_ranges : list of tuples
            List of ranges for each array in m
        delta_t1 : float 
            Spacing between values of t1
        delta_m : list of float
            Spacing between values of m
        pairs : list of tuples
            List of pairs of inversions used to calculated mp2rage and m
        """
        self.subject_id = subject_id
        self.scan = scan
        self.scan_times = scan_times
        self.monte_carlo = monte_carlo

        # Load dataset paths
        self.scan_num = self.scan.split('-', 1)[0]
        self.subject_path = os.path.join(t1_mapping.definitions.DATA, self.subject_id, self.scan)

        # Create potential T1 values
        self.delta_t1 = 0.05
        self.t1 = np.arange(self.delta_t1, 5 + self.delta_t1, self.delta_t1)

        # Create pairs for inversions
        if all_inv_combos:
            self.pairs = list(itertools.combinations(range(len(scan_times)), 2))
        else:
            self.pairs = [(0, i+1) for i in range(len(scan_times)-1)]

        # Create range of potential MP2RAGE values
        num_points = self.t1.shape[0]
        self.m_ranges = [(-0.5, 0.5) for i in self.pairs]
        if all_inv_combos:
            self.m_ranges[-1] = (0.25, 0.5)

        self.m = [np.linspace(m[0], m[1], 100) for m in self.m_ranges]
        self.delta_m = [(m[1]-m[0])/(num_points-1) for m in self.m_ranges]

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
    def affine(self):
        return self.inv[0].affine

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
    def eqn_params(self):
        return t1_mapping.utils.acq_to_eqn_params(self.acq_params)

    @cached_property
    def t1w(self):
        t1w_array = t1_mapping.utils.mp2rage_t1w(self.inv[0].get_fdata(dtype=np.complex64), self.inv[1].get_fdata(dtype=np.complex64))
        return nib.nifti1.Nifti1Image(t1w_array, self.affine)
    
    @cached_property
    def t1_map(self):
        if len(self.inv) == 2:
            t1_map = t1_mapping.utils.mp2rage_t1_map(
                t1=self.t1, 
                delta_t1=self.delta_t1,
                m=self.m,
                m_ranges=self.m_ranges,
                delta_m=self.delta_m,
                inv=[inv.get_fdata(dtype=np.complex64) for inv in self.inv],
                **self.eqn_params,
                method='linear')
        else:
            t1_map = t1_mapping.utils.mp2rage_t1_map(
                t1=self.t1,
                delta_t1=self.delta_t1,
                m=self.m,
                m_ranges=self.m_ranges,
                delta_m=self.delta_m,
                inv=[inv.get_fdata(dtype=np.complex64) for inv in self.inv],
                **self.eqn_params,
                method='likelihood',
                monte_carlo=self.monte_carlo,
                pairs=self.pairs,
                likelihood_thresh=0.5
            )
        return nib.nifti1.Nifti1Image(t1_map, self.affine)

    @cached_property
    def mp2rage(self):
        mp2rage = []
        for (i, j) in self.pairs:
            mp2rage_data = t1_mapping.utils.mp2rage_t1w(self.inv[i].get_fdata(dtype=np.complex64), self.inv[j].get_fdata(dtype=np.complex64))
            mp2rage.append(nib.Nifti1Image(mp2rage_data, self.affine))
        return mp2rage

    # @property
    # def m(self):
    #     m = [np.arange(r[0], r[1], self.delta_m[i]) for i, r in enumerate(self.m_ranges)]
    #     return m