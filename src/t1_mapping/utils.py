import numpy as np
import os
import nibabel as nib
from typing import TypedDict
from scipy.interpolate import RegularGridInterpolator
import re

def gre_signal(T1, TD, TR, flip_angles, n, eff):
    """
    Returns the values for the gradient echo blocks GRE1 and GRE2.

    Parameters
    ---------
    T1 : arraylike
        T1 relaxation time in s
    TD : arraylike
        Array containing time between gradient echo readout blocks
    TR : arraylike
        Repitition time of the gradient echo readout in s
    flip_angles : arraylike
        Flip angles of gradient echo pulses in rad
    n : arraylike
        Number of pulses within each gradient echo readout. Contains 2
        ints for number before and after center of k-space.
    eff : arraylike
        Inversion efficiency of scanner

    Returns
    -------
    GRE : ndarray
        n by m array containing gradient echo blocks, where n is the number
        of GRE readouts and m is the number of samples of T1.
    """
    n_readouts = len(flip_angles)
    n_bef = n[0]
    n_aft = n[1]
    n_tot = n_bef + n_aft

    # Calculate exponential terms
    E1 = np.exp(-TR/T1)
    ED = np.exp(-TD[:,np.newaxis]/T1)

    # Calculate steady-state magnetization
    num = 1 - ED[0]
    denom = 1 + eff*np.float_power(np.prod(np.cos(flip_angles))*E1**n_readouts, n_tot)*np.prod(ED, axis=0)
    for k in range(0, n_readouts):
        num = num*np.float_power(np.cos(flip_angles[k])*E1, n_tot) + \
            (1-E1)*(1-np.float_power(np.cos(flip_angles[k])*E1, n_tot))/(1-np.cos(flip_angles[k])*E1)
        num = num*ED[k+1] + (1-ED[k+1])

    mz_ss = num/denom

    # Calculate GRE signal
    GRE = np.zeros((n_readouts, len(T1)))

    temp = (-eff*mz_ss*ED[0] + (1-ED[0]))*np.float_power((np.cos(flip_angles[0])*E1), n_bef) + (1-E1)*(1-np.float_power(np.cos(flip_angles[0])*E1, n_bef))/(1-np.cos(flip_angles[0])*E1)
    GRE[0,:] = temp*np.sin(flip_angles[0])

    for m in range(1, n_readouts):
        temp = temp*np.float_power(np.cos(flip_angles[m-1])*E1, n_aft) + (1-E1)*(1-np.float_power(np.cos(flip_angles[m-1])*E1, n_aft))/(1-np.cos(flip_angles[m-1])*E1)
        temp = (temp*ED[m] + (1-ED[m]))*np.float_power(np.cos(flip_angles[m])*E1, n_bef) + (1-E1)*(1-np.float_power(np.cos(flip_angles[m])*E1, n_bef))/(1-np.cos(flip_angles[m])*E1)
        GRE[m,:]= temp*np.sin(flip_angles[m])
        
    return GRE


class MP2RAGEParameters(TypedDict):
    """
    TypedDict containing MP2RAGE acquisition parameters.

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
    n : list of int
        Number of pulses within each gradient echo readout. List containing
        1 int or 2 ints for number before and after center of k-space.
    eff : float
        Inversion efficiency of scanner
    """
    TR: float
    MP2RAGE_TR: float
    flip_angles: list
    inversion_times: list
    n: list
    eff: float

class EquationParameters(TypedDict):
    """
    TypedDict containing equation parameters.

    Parameters
    ----------
    TD : numpy.ndarray
        Array containing time between gradient echo readout blocks
    TR : numpy.ndarray
        Repitition time of the gradient echo readout in s
    flip_angles : numpy.ndarray
        Flip angles of gradient echo pulses in rad
    n : numpy.ndarray
        Number of pulses within each gradient echo readout. Contains 2
        ints for number before and after center of k-space.
    eff : np.ndarray
        Inversion efficiency of scanner
    """
    TD: np.ndarray
    TR: np.ndarray
    flip_angles: np.ndarray
    n: np.ndarray
    eff: np.ndarray

def acq_to_eqn_params(acq_params):
    """
    Returns the equation parameters (TA, TB, TC, ...) given the acquisition parameters
    (inversion times, flip angles, ...)
    
    Parameters
    _________
    acq_params : MP2RAGEParameters
        TypedDict with acquisition parameters TR, MP2RAGE_TR, flip_angles, 
        inversion_times, n and eff

    Returns
    -------
    eqn_params : EquationParameters
        TypedDict with equation parameters TD, TR, flip_angles, n, and eff
    """
    # Convert to Numpy arrays
    acq_params_arr = acq_params.copy()
    for k, v  in acq_params.items():
        acq_params_arr[k] = np.asarray([v]) if np.isscalar(v) else np.asarray(v)
    TR = acq_params_arr["TR"]
    MP2RAGE_TR = acq_params_arr["MP2RAGE_TR"]
    flip_angles = acq_params_arr["flip_angles"]
    inversion_times = acq_params_arr["inversion_times"]
    n = acq_params_arr["n"]
    eff = acq_params_arr["eff"]

    # Convert to radians
    flip_angles = flip_angles*np.pi/180

    # Calculate number of GRE blocks
    n_readouts = len(inversion_times)

    # Calculate number of slices
    if len(n) == 1:
        n_bef = n/2
        n_aft = n/2
        n_tot = n
    elif len(n) == 2:
        n_bef = n[0]
        n_aft = n[1]
        n_tot = np.sum(n)
    else:
        raise ValueError('n should be a list of either 1 or 2 values')

    # Calculate timing parameters
    T_GRE = n_tot*TR
    T_GRE_bef = n_bef*TR
    T_GRE_aft = n_aft*TR

    TD = np.zeros((n_readouts+1,))
    TD[0] = inversion_times[0] - T_GRE_bef 
    TD[-1] = MP2RAGE_TR - inversion_times[-1] - T_GRE_aft 
    for k in range(1, n_readouts):
        TD[k] = inversion_times[k] - inversion_times[k-1] - T_GRE
        
    # Check timing variables make sense
    if sum(TD) + n_readouts*n*TR != MP2RAGE_TR:
        print(f'Sum: {sum(TD) + n_readouts*n*TR}')
        raise ValueError("Timing parameters are invalid. Make sure the sum of the readout times and recovery times is equal to MP2RAGE_TR.")

    eqn_params = {
        "TD": TD,
        "TR": TR,
        "flip_angles" : flip_angles,
        "n": np.array([n_bef, n_aft]),
        "eff": eff
    }
    return eqn_params

def mp2rage_t1w(GRE1, GRE2, robust=False, beta=10):
    """
    Returns the MP2RAGE image formed by two gradient echo blocks.

    Parameters
    ---------
    GRE1 : arraylike
        The first gradient echo block
    GRE2 : arraylike
        The second gradient echo block
    robust : Boolean, optional, default=False
        Uses robust MP2RAGE calculation (see https://doi.org/10.1371/journal.pone.0099676)
    beta : float, optional, default=0.01
        Offset parameter for robust MP2RAGE calculation

    Returns
    -------
    MP2RAGE : ndarray
        T1-weighted MP2RAGE image
    """
    
    # Calculate MP2RAGE 
    if robust: 
        MP2RAGE = np.real((np.conj(GRE1)*GRE2) - beta)/(np.abs(GRE1)**2 + np.abs(GRE2)**2 + 2*beta)
    else:
        MP2RAGE = np.real((np.conj(GRE1)*GRE2))/(np.abs(GRE1)**2 + np.abs(GRE2)**2)

    # Replace NaN with 0
    MP2RAGE = np.nan_to_num(MP2RAGE)

    return MP2RAGE

def mp2rage_t1_map(t1, delta_t1, m, m_ranges, delta_m, inv, TD, TR, flip_angles, n, eff, method='point', monte_carlo=None, likelihood_thresh=0.5, pairs=None):
    """
    Returns the values for the T1 map calculated from an MP2RAGE sequence.

    Parameters
    ---------
    t1 : arraylike
        Potential T1 values (e.g. an array from 0.05 to 5)
    m : arraylike
        Potential MP2RAGE values
    m_ranges : array of tuples
        Ranges of m
    inv : arraylike
        Array containing the gradient echo readouts
    TD : arraylike
        Array containing time between gradient echo readout blocks
    TR : arraylike
        Repitition time of the gradient echo readout in s
    flip_angles : arraylike
        Flip angles of gradient echo pulses in rad
    n : arraylike
        Number of pulses within each gradient echo readout. Contains 2
        ints for number before and after center of k-space.
    eff : arraylike
        Inversion efficiency of scanner
    method : str, default='point'
        Method for calculating T1 map. Can be 'point', 'map', or 'likelihood'.
    monte_carlo : str
        If method is 'likelihood', path to counts from Monte Carlo simulation
    likelihood_thresh : float, default=0.5
        If method is 'likelihood', the threshold for the acceptable relative likelihood
    pairs : list of tuples
        If method is 'likelihood', list of pairs used to calculate mp2rage images

    Returns
    --------
    t1_calc : numpy.ndarray
        T1 map calculated from inputs
    """
    if method == 'point':
        # Calculate T1-weighted image
        t1w = mp2rage_t1w(inv[0], inv[1])

        # Range of values for T1
        num_points = len(t1)

        GRE = gre_signal(
            T1=t1,
            TD=TD,
            TR=TR,
            flip_angles=flip_angles,
            n=n,
            eff=eff
        )
        m = mp2rage_t1w(GRE[0,:], GRE[1,:])

        # Sort arrays
        sorted_idx = np.argsort(m)
        m = m[sorted_idx]
        t1 = t1[sorted_idx]

        # Pad LUT
        m[0] = -0.5
        m[-1] = 0.5

        # Calculate for desired values
        t1_calc = np.interp(t1w.flatten(), m, t1, right=0.)
        t1_calc = t1_calc.reshape(t1w.shape)

    elif method == 'likelihood':
        # Load Monte Carlo simulation file
        if monte_carlo is None:
            raise TypeError("Argument monte_carlo must be provided if method for T1 map calculation is 'likelihood'.")
        else:
            counts = np.load(monte_carlo)

        n_pairs = len(pairs)
        n_readouts = len(inv)

        # Calculate likelihoods
        with np.errstate(divide='ignore', invalid='ignore'):
            L_gauss = counts / np.sum(counts * np.prod(delta_m), axis=tuple(range(n_pairs)))
        L_gauss = np.nan_to_num(L_gauss, nan=0)

        # Maximum likelihood of gaussian
        max_L_gauss = np.max(L_gauss, axis=-1)

        # Uniform likelihood
        total_vol = np.prod(m[1]-m[0] for m in m_ranges)
        m_squares = np.array([len(mp2rage) for mp2rage in m])
        total_squares = np.prod(m_squares)
        uni_value = 1/(total_squares*np.prod(delta_m))
        L_uni = np.full(tuple(m_squares), uni_value)

        # Relative likelihood
        alpha = max_L_gauss / (max_L_gauss + L_uni)

        # Create LUT
        max_L_gauss_ind = np.argmax(L_gauss, axis=-1)
        t1_lut = t1[max_L_gauss_ind]
        t1_lut[alpha < likelihood_thresh] = 0

        # Create grid
        interp = RegularGridInterpolator(tuple(m), values=t1_lut,
            bounds_error=False, fill_value=0, method='linear')

        # Calculate MP2RAGE images to get values at
        t1w = [mp2rage_t1w(inv[i[0]], inv[i[1]]) for i in pairs]

        # Clip to [-0.5, 0.5] to accounting for floating-point errors
        t1w = [np.clip(t, -0.5, 0.5) for t in t1w]

        # Interpolate along new values
        pts = tuple([t.flatten() for t in t1w])
        t1_calc = interp(pts).reshape(t1w[0].shape)

    elif method == 'map':
        # Load Monte Carlo simulation file
        counts = np.load(monte_carlo)
        with np.errstate(divide='ignore', invalid='ignore'):
            posterior = counts / np.sum(counts*delta_t1, axis=-1)[...,np.newaxis]

        # For each M, find the T1 with the highest probability
        max_inds = np.argmax(posterior, axis=-1)

        # Create LUT
        t1_lut = t1[max_inds]

        # Create grid
        interp = RegularGridInterpolator(tuple(m), values=t1_lut,
            bounds_error=False, fill_value=0, method='linear')

        # Calculate MP2RAGE images to get values at
        t1w = [mp2rage_t1w(inv[i[0]], inv[i[1]]) for i in pairs]

        # Clip to [-0.5, 0.5] to accounting for floating-point errors
        t1w = [np.clip(t, -0.5, 0.5) for t in t1w]

        # Interpolate along new values
        pts = tuple([t.flatten() for t in t1w])
        t1_calc = interp(pts).reshape(t1w[0].shape)

    else:
        raise ValueError("Invalid value for 'method'. Valid values are 'point', 'map', or 'likelihood'.")

    return t1_calc

def mp2rage_t1_exp_val(t1, delta_t1, m, m_ranges, delta_m, inv, TD, TR, flip_angles, n, eff, monte_carlo=None, pairs=None):
    """
    Returns the expected value of T1 given M1, M2

    Parameters
    ---------
    t1 : arraylike
        Potential T1 values (e.g. an array from 0.05 to 5)
    delta_t1 : float
        T1 spacing
    m : arraylike
        Potential MP2RAGE values
    m_ranges : array of tuples
        Ranges of m
    delta_m : float
        m spacing
    inv : arraylike
        Array containing the gradient echo readouts
    TD : arraylike
        Array containing time between gradient echo readout blocks
    TR : arraylike
        Repitition time of the gradient echo readout in s
    flip_angles : arraylike
        Flip angles of gradient echo pulses in rad
    n : arraylike
        Number of pulses within each gradient echo readout. Contains 2
        ints for number before and after center of k-space.
    eff : arraylike
        Inversion efficiency of scanner
    monte_carlo : str
        Path to counts from Monte Carlo simulation
    pairs : list of tuples
        List of pairs used to calculate mp2rage images

    Returns
    --------
    t1_ev : numpy.ndarray
        Expected value map calculated from inputs
    """
    # Load Monte Carlo simulation file
    counts = np.load(monte_carlo)

    n_pairs = len(pairs)
    n_readouts = len(inv)

    # Calculate likelihood
    with np.errstate(divide='ignore', invalid='ignore'):
        likelihood = counts / np.sum(counts * np.prod(delta_m), axis=tuple(range(n_pairs)))
    likelihood = np.nan_to_num(likelihood, nan=0)

    # Calculate posterior
    with np.errstate(divide='ignore', invalid='ignore'):
        posterior = likelihood / np.sum(delta_t1*likelihood, axis=-1)[...,np.newaxis]
    posterior = np.nan_to_num(posterior, nan=0)

    # Expected value
    exp_val = np.sum(t1*posterior*delta_t1,axis=-1)
    exp_val = np.nan_to_num(exp_val, nan=0)

    # Create grid
    interp = RegularGridInterpolator(tuple(m), values=exp_val,
        bounds_error=False, fill_value=0, method='linear')

    # Calculate MP2RAGE images to get values at
    t1w = [mp2rage_t1w(inv[i[0]], inv[i[1]]) for i in pairs]

    # Clip to [-0.5, 0.5] to accounting for floating-point errors
    t1w = [np.clip(t, -0.5, 0.5) for t in t1w]

    # Interpolate along new values
    pts = tuple([t.flatten() for t in t1w])
    t1_ev = interp(pts).reshape(t1w[0].shape)

    return t1_ev

def mp2rage_t1_var(t1, delta_t1, m, m_ranges, delta_m, inv, TD, TR, flip_angles, n, eff, monte_carlo=None, pairs=None):
    """
    Returns the variance of T1 given M1 and M2

    Parameters
    ---------
    t1 : arraylike
        Potential T1 values (e.g. an array from 0.05 to 5)
    delta_t1 : float
        T1 spacing
    m : arraylike
        Potential MP2RAGE values
    m_ranges : array of tuples
        Ranges of m
    delta_m : float
        m spacing
    inv : arraylike
        Array containing the gradient echo readouts
    TD : arraylike
        Array containing time between gradient echo readout blocks
    TR : arraylike
        Repitition time of the gradient echo readout in s
    flip_angles : arraylike
        Flip angles of gradient echo pulses in rad
    n : arraylike
        Number of pulses within each gradient echo readout. Contains 2
        ints for number before and after center of k-space.
    eff : arraylike
        Inversion efficiency of scanner
    monte_carlo : str
        Path to counts from Monte Carlo simulation
    pairs : list of tuples
        List of pairs used to calculate mp2rage images

    Returns
    --------
    t1_var : numpy.ndarray
        Variance map calculated from inputs
    """
    # Load Monte Carlo simulation file
    counts = np.load(monte_carlo)

    n_pairs = len(pairs)
    n_readouts = len(inv)

    # Calculate likelihood
    with np.errstate(divide='ignore', invalid='ignore'):
        likelihood = counts / np.sum(counts * np.prod(delta_m), axis=tuple(range(n_pairs)))
    likelihood = np.nan_to_num(likelihood, nan=0)

    # Calculate posterior
    with np.errstate(divide='ignore', invalid='ignore'):
        posterior = likelihood / np.sum(delta_t1*likelihood, axis=-1)[...,np.newaxis]
    posterior = np.nan_to_num(posterior, nan=0)

    # Expected value
    exp_val = np.sum(t1*posterior*delta_t1,axis=-1)
    exp_val = np.nan_to_num(exp_val, nan=0)

    # Variance
    variance = np.sum((t1 - exp_val[...,np.newaxis])**2*posterior*delta_t1, axis=-1)

    # Create grid
    interp = RegularGridInterpolator(tuple(m), values=variance,
        bounds_error=False, fill_value=0, method='linear')

    # Calculate MP2RAGE images to get values at
    t1w = [mp2rage_t1w(inv[i[0]], inv[i[1]]) for i in pairs]

    # Clip to [-0.5, 0.5] to accounting for floating-point errors
    t1w = [np.clip(t, -0.5, 0.5) for t in t1w]

    # Interpolate along new values
    pts = tuple([t.flatten() for t in t1w])
    t1_var = interp(pts).reshape(t1w[0].shape)

    return t1_var

# Custom sorting function
def sort_key(file_name):
    match = re.search(r't(\d+)\.nii(\.gz)?', file_name)
    if match:
        return int(match.group(1))
    return 0