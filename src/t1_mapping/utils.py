import numpy as np
from scipy.interpolate import CubicSpline

def gre_signal(T1=1, TA=1, TB=1, TC=1, TR=6e-3, alpha_1=4, alpha_2=4, n=36, MP2RAGE_TR=6, eff=0.96):
    """
    Returns the values for the gradient echo blocks GRE1 and GRE2.

    Parameters
    ---------
    T1 : arraylike, optional, default=1.0
        T1 relaxation time in s
    TA : arraylike, optional, default=1.0
        Time from initial pulse to beginning of first GRE block in s
    TB : arraylike, optional, default=1.0
        Time from end of first GRE block to beginning of second block in s
    TC : arraylike, optional, default=1.0
        Time from end of second GRE block to next pulse in s
    TR : arraylike, optional, default=6e-3
        Time from one gradient echo to next in s
    alpha_1 : arraylike, optional, default=4
        Flip angle for first block in deg
    alpha_2 : arraylike, optional, default=4
        Flip angle for second block in deg
    n : arraylike, optional, default=36
        Number of pulses in gradient echo block
    MP2RAGE_TR : arraylike, optional, default=6
        Time from one pulse to another in s
    eff : arraylike, optional, default=0.96
        Inversion pulse efficiency

    Returns
    -------
    GRE1: ndarray
        First gradient echo block
    GRE2: ndarray
        Second gradient echo block
    """
    # Convert alpha_1 and alpha_2 to radians
    alpha_1 = alpha_1*np.pi/180
    alpha_2 = alpha_2*np.pi/180
    
    params = [T1, TA, TB, TC, TR, alpha_1, alpha_2, n, MP2RAGE_TR, eff]

    # Convert to Numpy arrays
    for i, p in enumerate(params):
        params[i] = np.asarray([p]) if np.isscalar(p) else np.asarray(p)
    (T1, TA, TB, TC, TR, alpha_1, alpha_2, n, MP2RAGE_TR, eff) = tuple(params)

    # Calculate exponential terms
    E1 = np.exp(-TR/T1)
    EA = np.exp(-TA/T1)
    EB = np.exp(-TB/T1)
    EC = np.exp(-TC/T1)
    
    # Calculate steady-state magnetization
    mz_ss = (((((1-EA)*np.float_power(np.cos(alpha_1)*E1, n) + (1-E1)*(1-np.float_power(np.cos(alpha_1)*E1, n))/(1-np.cos(alpha_1)*E1))*EB + (1-EB))*np.float_power(np.cos(alpha_2)*E1, n) + (1-E1)*(1-np.float_power(np.cos(alpha_2)*E1, n))/(1-np.cos(alpha_2)*E1))*EC + (1-EC))/(1 + eff*np.float_power(np.cos(alpha_1)*np.cos(alpha_2), n)*np.exp(-MP2RAGE_TR/T1))
    
    # Calculate gradient echo blocks
    GRE1 = np.sin(alpha_1)*((-eff*mz_ss*EA + (1-EA))*np.float_power(np.cos(alpha_1)*E1, n/2-1) + (1-E1)*(1-np.float_power(np.cos(alpha_1)*E1, n/2-1))/(1-np.cos(alpha_1)*E1))
    GRE2 = np.sin(alpha_2)*((mz_ss - (1-EC))/(EC*np.float_power(np.cos(alpha_2)*E1, n/2)) - (1-E1)*((np.float_power(np.cos(alpha_2)*E1, -n/2)-1)/(1 - np.cos(alpha_2)*E1)))
    
    return GRE1, GRE2

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

    Returns
    -------
    T1 : ndarray
        Quantitative T1 map calculated from MP2RAGE sequence
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