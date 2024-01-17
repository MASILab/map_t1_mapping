import t1_mapping.utils
from functools import cached_property
import itertools
import nibabel as nib
import numpy as np
import os
import json
import yaml

class MP2RAGESubject():
    def __init__(self, params_path, scan_paths=None, monte_carlo=None):
        """
        Class to store MP2RAGE subject data

        Parameters
        ---------
        params_path : str
            Path to parameter YAML fileW
        scan_paths : list of str
            List of scan paths to load (real #1, imaginary #1, real #2, imaginary #2, etc.)
        monte_carlo : str
            Monte Carlo simulation counts used for likelihood method

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
        self.scan_paths = scan_paths
        self.monte_carlo = monte_carlo

        # Load parameters
        with open(params_path, 'r') as f:
            self.params = yaml.safe_load(f)

        # Create potential T1 values
        self.delta_t1 = 0.05
        self.t1 = np.arange(self.delta_t1, 5 + self.delta_t1, self.delta_t1)

        # Create range of potential MP2RAGE values
        num_points = self.t1.shape[0]
        self.m_ranges = [(-0.5, 0.5) for i in self.pairs]

        self.m = [np.linspace(m[0], m[1], 100) for m in self.m_ranges]
        self.delta_m = [(m[1]-m[0])/(num_points-1) for m in self.m_ranges]

    @cached_property
    def inv(self):
        inv = []
        for i in range(len(self.scan_paths)):
            # Real if even, imaginary if odd
import itertools
            if i % 2 == 0:
                # Load NIFTI
                inv_real = nib.load(self.scan_paths[i])
                inv_imag = nib.load(self.scan_paths[i+1])

                # Get data from NIFTI
                inv_real_data = inv_real.get_fdata()
                inv_imag_data = inv_imag.get_fdata()

                # Create combined complex data
                inv_data = inv_real_data + 1j*inv_imag_data

                # Create NIFTI
                inv.append(nib.nifti1.Nifti1Image(inv_data, inv_real.affine))
        return inv

    @property
    def affine(self):
        return self.inv[0].affine

    @property
    def acq_params(self):
        # Load acquisition parameters from YAML
        params = self.params.copy()
        params.pop('noise_std')
        params.pop('num_trials')
        params.pop('likelihood_threshold')
        acq_params = t1_mapping.utils.MP2RAGEParameters(**params)
        return acq_params

    @property
    def eqn_params(self):
        return t1_mapping.utils.acq_to_eqn_params(self.acq_params)

    @cached_property
    def t1w(self):
        t1w_array = t1_mapping.utils.mp2rage_t1w(self.inv[0].get_fdata(dtype=np.complex64), self.inv[1].get_fdata(dtype=np.complex64))
        return nib.nifti1.Nifti1Image(t1w_array, self.affine)
    
    def t1_map(self, method):
        thresh = self.params['likelihood_threshold']
        if method == 'point':
            t1_map = t1_mapping.utils.mp2rage_t1_map(
                t1=self.t1, 
                delta_t1=self.delta_t1,
                m=self.m,
                m_ranges=self.m_ranges,
                delta_m=self.delta_m,
                inv=[inv.get_fdata(dtype=np.complex64) for inv in self.inv],
                **self.eqn_params,
                method='point')
        elif method == 'likelihood':
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
                likelihood_thresh=thresh
            )
        elif method == 'map':
            t1_map = t1_mapping.utils.mp2rage_t1_map(
                t1=self.t1,
                delta_t1=self.delta_t1,
                m=self.m,
                m_ranges=self.m_ranges,
                delta_m=self.delta_m,
                inv=[inv.get_fdata(dtype=np.complex64) for inv in self.inv],
                **self.eqn_params,
                method='map',
                monte_carlo=self.monte_carlo,
                pairs=self.pairs,
                likelihood_thresh=thresh
            )
        return nib.nifti1.Nifti1Image(t1_map, self.affine)

    @cached_property
    def mp2rage(self):
        mp2rage = []
        for (i, j) in self.pairs:
            mp2rage_data = t1_mapping.utils.mp2rage_t1w(self.inv[i].get_fdata(dtype=np.complex64), self.inv[j].get_fdata(dtype=np.complex64))
            mp2rage.append(nib.Nifti1Image(mp2rage_data, self.affine))
        return mp2rage
    
    @cached_property
    def t1_ev(self):
        t1_ev = t1_mapping.utils.mp2rage_t1_exp_val(
                t1=self.t1,
                delta_t1=self.delta_t1,
                m=self.m,
                m_ranges=self.m_ranges,
                delta_m=self.delta_m,
                inv=[inv.get_fdata(dtype=np.complex64) for inv in self.inv],
                **self.eqn_params,
                monte_carlo=self.monte_carlo,
                pairs=self.pairs,
        )
        return nib.Nifti1Image(t1_ev, self.affine)

    @cached_property
    def t1_var(self):
        t1_var = t1_mapping.utils.mp2rage_t1_var(
                t1=self.t1,
                delta_t1=self.delta_t1,
                m=self.m,
                m_ranges=self.m_ranges,
                delta_m=self.delta_m,
                inv=[inv.get_fdata(dtype=np.complex64) for inv in self.inv],
                **self.eqn_params,
                monte_carlo=self.monte_carlo,
                pairs=self.pairs,
        )
        return nib.Nifti1Image(t1_var, self.affine)
    
    @property
    def t1_std(self):
        t1_var_data = self.t1_var.get_fdata()
        t1_std_data = np.sqrt(t1_var_data)
        return nib.Nifti1Image(t1_std_data, self.affine)