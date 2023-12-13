import os

GROUND_TRUTH_MAT = '/nfs/masi/saundam1/datasets/MP2RAGE_SIR_qMT/7T_SIRqMT_R1maps'
GROUND_TRUTH = '/nfs/masi/saundam1/datasets/MP2RAGE_SIR_qMT/'

OUTPUTS = '/nfs/masi/saundam1/outputs/t1_mapping'
DATA = os.path.join(OUTPUTS, 'mp2rage_converted_v2023')
SIMULATION_DATA = os.path.join(OUTPUTS, 'distr')
GROUND_TRUTH_DATA = os.path.join(OUTPUTS, 'mp2rage_sir_qmt')
T1_MAPS_LUT = os.path.join(OUTPUTS, 't1_maps_lut')
T1_MAPS_LIKELIHOOD = os.path.join(OUTPUTS, 't1_maps_likelihood')