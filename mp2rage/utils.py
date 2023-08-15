import numpy as np

def GRE(T1=1, TA=1, TB=1, TC=1, TR=6e-3, alpha_1=4, alpha_2=4, n=36, MP2RAGE_TR=6, eff=0.96):
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
        Number of shots
    MPRAGE_TR : arraylike, optional, default=6
        Time from one pulse to another in s
    eff : arraylike, optional, default=0.96
        Pulse efficiency of scanner

    Returns
    -------
    GRE1: ndarray
        First gradient echo block
    GRE2: ndarray
        Second gradient echo block
    """
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

def MP2RAGE(GRE1, GRE2):
    """
    Returns the MP2RAGE image formed by two gradient echo blocks.

    Parameters
    ---------
    GRE1 : arraylike
        The first gradient echo block
    GRE2 : arraylike
        The second gradient echo block

    Returns
    -------
    MP2RAGE: ndarray
        First gradient echo block
    """

    # Check if data needs to be scaled to [-0.5, 0.5]
    # print(np.min(GRE1), np.max(GRE1))
    # print(np.min(GRE2), np.max(GRE2))
    # if ((np.max(np.abs(GRE1)) > 0.51 or np.max(np.abs(GRE2)) > 0.51) or (np.min(np.abs(GRE1) < 0.0))):
    #     # print('Scaling data')
    #     # GRE1 = (GRE1 - np.max(GRE1)/2) / np.max(GRE1)
    #     # GRE2 = (GRE2 - np.max(GRE2)/2) / np.max(GRE2)
    #     # print(np.min(GRE1), np.max(GRE1))
    #     # print(np.min(GRE2), np.max(GRE2))
    #     pass

    MP2RAGE = np.real((np.conj(GRE1)*GRE2))/(np.abs(GRE1)**2 + np.abs(GRE2)**2)
    # MP2RAGE = (GRE1*GRE2)/(GRE1**2 + GRE2**2)

    # Replace NaN with 0
    MP2RAGE = np.nan_to_num(MP2RAGE)

    # print(np.min(MP2RAGE), np.max(MP2RAGE))

    return MP2RAGE