import numpy as np
import matplotlib.pyplot as plt
from nibabel.affines import apply_affine

def gre_signal(T1, inversion_times, TR, MP2RAGE_TR, flip_angles, n, eff):
    """
    Returns the values for the gradient echo blocks GRE1 and GRE2.

    Parameters
    ---------
    T1 : arraylike
        T1 relaxation time in s
    inversion_times : arraylike
        Time in s from inversion pulse to middle of each inversion block.
        Note that len(inversion_times) must be the same as the number of GRE readouts.
    TR : arraylike
        Time from one gradient echo to next in s.
    MP2RAGE_TR : arraylike
        Time from one pulse to another in s.
    flip_angles : arraylike
        Flip angles in deg for each inversion block. 
        Note: len(flip_angles) must be the same as the number of GRE readouts.
    n : list of int
        Number of pulses in gradient echo block. If n is a list of 2 values,
        then n is the number of pulses before and after the center of k-space.
    eff : arraylike, optional, default=0.96
        Inversion pulse efficiency

    Returns
    -------
    GRE : ndarray
        n by m array containing gradient echo blocks, where n is the number
        of GRE readouts and m is the number of samples of T1.
    """
    # Convert to Numpy arrays
    params = [T1, inversion_times, TR, MP2RAGE_TR, flip_angles, n]
    for i, p in enumerate(params):
        params[i] = np.asarray([p]) if np.isscalar(p) else np.asarray(p)
    (T1, inversion_times, TR, MP2RAGE_TR, flip_angles, n) = tuple(params)

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
        raise ValueError("Timing parameters are invalid. Make sure the sum of the readout times and recovery times is equal to MP2RAGE_TR.")

    # Calculate exponential terms
    E1 = np.exp(-TR/T1)
    # EA = np.exp(-TA/T1)
    ED = np.exp(-TD[:,np.newaxis]/T1)

    # Calculate steady-state magnetization
    denom = 1 + eff*np.float_power(np.prod(np.cos(flip_angles)*E1), n)*(np.prod(ED))
    num = 1 - ED[0]
    for k in range(0, n_readouts):
        num = num*np.float_power(np.cos(flip_angles[k])*E1, n) + \
            (1-E1)*(1-np.float_power(np.cos(flip_angles[k])*E1, n))/(1-np.cos(flip_angles[k])*E1)
        num = num*ED[k+1] + (1-ED[k+1])

    mz_ss = num/denom

    # Calculate GRE signal
    
    GRE = np.zeros((n_readouts, len(T1)))
    return GRE


# def gre_signal(T1, TA, TB, TR, alpha_1, alpha_2, n, MP2RAGE_TR, TC=None, eff=0.96, method='code'):
    # """
    # Returns the values for the gradient echo blocks GRE1 and GRE2.

    # Parameters
    # ---------
    # T1 : arraylike
    #     T1 relaxation time in s
    # TA : arraylike
    #     Time from initial pulse to beginning of first GRE block in s
    # TB : arraylike
    #     Time from end of first GRE block to beginning of second block in s
    # TR : arraylike
    #     Time from one gradient echo to next in s
    # alpha_1 : arraylike
    #     Flip angle for first block in deg
    # alpha_2 : arraylike
    #     Flip angle for second block in deg
    # n : arraylike
    #     Number of pulses in gradient echo block
    # MP2RAGE_TR : arraylike
    #     Time from one pulse to another in s
    # TC : arraylike, optional
    #     Time from end of second GRE block to next pulse in s. Calculated if not provided.
    # eff : arraylike, optional, default=0.96
    #     Inversion pulse efficiency
    # method : string, optional, default='code'
    #     Perform calculations using equations from 'code' (GitHub repository) 
    #     or 'paper' for equations presented in paper. Both provide same results.

    # Returns
    # -------
    # GRE1: ndarray
    #     First gradient echo block
    # GRE2: ndarray
    #     Second gradient echo block
    # """
    # # Assign TC if not given
    # if TC is None:
    #     TC = MP2RAGE_TR - (TA + TB + 2*n*TR)
    #     print(f'Setting TC to {TC}')

    # # Check timing variables make sense
    # if TA + TB + TC + 2*n*TR != MP2RAGE_TR:
    #     raise ValueError("Timing parameters are invalid. TA + TB + TC + 2*n*TR must equal MP2RAGE_TR.")

    # # Convert alpha_1 and alpha_2 to radians
    # alpha_1 = alpha_1*np.pi/180
    # alpha_2 = alpha_2*np.pi/180
    
    # params = [T1, TA, TB, TC, TR, alpha_1, alpha_2, n, MP2RAGE_TR, eff]

    # # Convert to Numpy arrays
    # for i, p in enumerate(params):
    #     params[i] = np.asarray([p]) if np.isscalar(p) else np.asarray(p)
    # (T1, TA, TB, TC, TR, alpha_1, alpha_2, n, MP2RAGE_TR, eff) = tuple(params)

    # # Calculate exponential terms
    # E1 = np.exp(-TR/T1)
    # EA = np.exp(-TA/T1)
    # EB = np.exp(-TB/T1)
    # EC = np.exp(-TC/T1)
    
    # # Calculate steady-state magnetization
    # mz_ss = (((((1-EA)*np.float_power(np.cos(alpha_1)*E1, n) + (1-E1)*(1-np.float_power(np.cos(alpha_1)*E1, n))/(1-np.cos(alpha_1)*E1))*EB + (1-EB))*np.float_power(np.cos(alpha_2)*E1, n) + (1-E1)*(1-np.float_power(np.cos(alpha_2)*E1, n))/(1-np.cos(alpha_2)*E1))*EC + (1-EC))/(1 + eff*np.float_power(np.cos(alpha_1)*np.cos(alpha_2), n)*np.exp(-MP2RAGE_TR/T1))
    
    # # Calculate gradient echo blocks
    # if method == 'code':
    #     # GRE1 = np.sin(alpha_1)*((-eff*mz_ss*EA + (1-EA))*np.float_power((np.cos(alpha_1)*E1), n/2) + (1-E1)*(1-np.float_power(np.cos(alpha_1)*E1, n/2))/(1-np.cos(alpha_1)*E1))
    #     # GRE2 = np.sin(alpha_2)*(((((-eff*mz_ss*EA + (1-EA))*np.float_power((np.cos(alpha_1)*E1), n/2) + (1-E1)*(1-np.float_power(np.cos(alpha_1)*E1, n/2))/(1-np.cos(alpha_1)*E1))*np.float_power(np.cos(alpha_1)*E1, n/2) + (1-E1)*(1-np.float_power(np.cos(alpha_1)*E1, n/2))/(1-np.cos(alpha_1)*E1))*EB + (1-EB))*np.float_power(np.cos(alpha_2)*E1, n/2) + (1-E1)*(1-np.float_power(np.cos(alpha_2)*E1, n/2))/(1-np.cos(alpha_2)*E1))
    #     term1 = (-eff*mz_ss*EA + (1-EA))*np.float_power((np.cos(alpha_1)*E1), n/2) + (1-E1)*(1-np.float_power(np.cos(alpha_1)*E1, n/2))/(1-np.cos(alpha_1)*E1)
    #     GRE1 = term1*np.sin(alpha_1)
    #     term2 = term1*np.float_power(n   except:
    #     raise ValueError('n should be a list of either 1 or 2 values')p.cos(alpha_1)*E1, n/2) + (1-E1)*(1-np.float_power(np.cos(alpha_1)*E1, n/2))/(1-np.cos(alpha_1)*E1)
    #     term3 = (term2*EB + (1-EB))*np.float_power(np.cos(alpha_2)*E1, n/2) + (1-E1)*(1-np.float_power(np.cos(alpha_2)*E1, n/2))/(1-np.cos(alpha_2)*E1)
    #     GRE2 = term3*np.sin(alpha_2)
    # elif method == 'paper':
    #     GRE1 = np.sin(alpha_1)*((-eff*mz_ss*EA + (1-EA))*np.float_power(np.cos(alpha_1)*E1, n/2-1) + (1-E1)*(1-np.float_power(np.cos(alpha_1)*E1, n/2-1))/(1-np.cos(alpha_1)*E1))
    #     GRE2 = np.sin(alpha_2)*((mz_ss - (1-EC))/(EC*np.float_power(np.cos(alpha_2)*E1, n/2)) - (1-E1)*((np.float_power(np.cos(alpha_2)*E1, -n/2)-1)/(1 - np.cos(alpha_2)*E1)))
        
    # return GRE1, GRE2

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

def mp2rage_t1_map(GRE1, GRE2, TA, TB, TC, TR, alpha_1, alpha_2, n, MP2RAGE_TR, eff):
    """
    Returns the values for the T1 map calculated from an MP2RAGE sequence.

    Parameters
    ---------
    GRE1 : arraylike
        The first gradient echo block
    GRE2 : arraylike
        The second gradient echo block
    TA : float
        Time from initial pulse to beginning of first GRE block in s
    TB : float
        Time from end of first GRE block to beginning of second block in s
    TC : float
        Time from end of second GRE block to next pulse in s
    TR : float
        Time from one gradient echo to next in s
    alpha_1 : float
        Flip angle for first block in deg
    alpha_2 : float
        Flip angle for second block in deg
    n : float
        Number of pulses in gradient echo block
    MP2RAGE_TR : float
        Time from one pulse to another in s
    eff : float
        Inversion pulse efficiency
    """
    # Calculate T1-weighted image
    t1w = mp2rage_t1w(GRE1, GRE2)

    # Range of values that T1 could take
    num_points = 1000
    t1_values = np.linspace(0.2, 5, num_points).reshape(num_points,1)

    # Calculate what values would be produced with the range for T1
    [GRE1_calc, GRE2_calc] = gre_signal(
        T1=t1_values,
        TA=TA,
        TB=TB,
        TC=TC,
        TR=TR,
        alpha_1=alpha_1,
        alpha_2=alpha_2,
        n=n,
        MP2RAGE_TR=MP2RAGE_TR,
        eff=eff
    )

    # Create estimated T1-weighted image
    t1w_calc = mp2rage_t1w(GRE1_calc, GRE2_calc).reshape(num_points, 1)

    # Create LUT
    LUT = np.hstack((t1w_calc, t1_values))

    # Sort LUT so values are in numerical order
    LUT = LUT[LUT[:, 0].argsort()]

    # Create cubic interpolation
    cs = CubicSpline(LUT[:, 0], LUT[:, 1])

    # Calculate for desired values
    t1_calc = cs(t1w.flatten())
    t1_calc = t1_calc.reshape(t1w.shape)

    return t1_calc
    
# def mp2rage_signal(nimages, MP2RAGE_TR, inv_times, n, FLASH_TR, flipangle, T1, eff=0.84)