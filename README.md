# MAP T1 Mapping
Maximum a posteriori (MAP) quantitative T1 mapping

To use this repository as a Python package called "t1_mapping", do `pip install -e .` in this folder. Alternatively, see below for instructions for using the Singularity container.

## Preparing your data 
You must create an input folder with the following structure:
```
input_folder/
    subject1/
        scan1/
            ..._real_tXXXX.nii.gz
            ..._imaginary_tXXXX.nii.gz
            ..._real_tYYYY.nii.gz
            ..._imaginary_tYYYY.nii.gz
        scan2/
            ...
    subject2/
        scan1/
            ...
        scan2/
            ...
        scan3/
            ...
```

The names of the folders can vary, but the structure must be the same. XXXX and YYYY are the inversion times in ms and are used to order the images correctly. You should also create a YAML file that contains the acquisition parameters:

```YAML
TR: 0.006  # Repitition time of the gradient echo readout in s
MP2RAGE_TR: 8.25 # Time between inversion pulses in s
flip_angles: # Flip angles of gradient echo pulses in deg
  - 4
  - 4
  - 4
inversion_times: # Time from inversion pulse to middle of each gradient echo readout
  - 1.010
  - 3.310  
  - 5.610
n: # Number of pulses within each gradient echo readout. List containing 1 int or 2 ints for number before and after center of k-space.
  - 225
eff: 0.84 # Inversion pulse efficiency of scanner
noise_std: 0.005 # Standard deviation of noise for Monte Carlo simulation
num_trials: 100000000 # Number of trials for Monte Carlo simulation
likelihood_threshold: 0.5 # Threshold for relative likelihood for likelihood method of T1 mapping
```

Note you must have the same number of flip angles and inversion times - it should be the same as the number of inversions.

## Running the Monte Carlo simulation
To create T1 maps with method likelihood or map, or to create expected value, standard deviation or variance maps, you need to first run a Monte Carlo simulation. See `python run_mp2rage_simulation.py --help`.

```bash
python run_mp2rage_simulation.py --params_path params.yml --sim_output_path sim_outputs/counts_1M_0.005.npy --num_trials 1000000 --num_process 15 --noise_std 0.005
```

## Creating the images
See `python create_image.py --help`. The image type can be any of the following:
- point (original point estimate MP2RAGE T1 map)
- likelihood* (MAP T1 with relative likelihood threshold) 
- map* (MAP T1 without threshold)
- t1w (MP2RAGE T1-weighted image)
- robust_t1w (MP2RAGE T1-weighted image with noise suppression)
- ev* (expected value of MAP T1)
- std* (standard deviation of MAP T1)
- var* (variance of MAP T1)

Note: * requires you to run a Monte Carlo simulation first.

```bash
python create_image.py --params_path params.yml --input_folder inputs/ --num_process 1 --image_type map --monte_carlo_path sim_outputs/counts_1M_0.005.npy --output_folder outputs/
```

## Singularity container
As an alternative to the repository, you can use the Singularity image: [https://www.dropbox.com/scl/fi/shxienqokb4ud661fwf40/map_t1_mapping.sif?rlkey=x2lcyp0wlxe0fvfvo2rm02gwl&dl=0](https://www.dropbox.com/scl/fi/shxienqokb4ud661fwf40/map_t1_mapping.sif?rlkey=x2lcyp0wlxe0fvfvo2rm02gwl&dl=0). You must bind the /inputs, /outputs, and /sim_outputs when using the container. The code to run is located in /code. For example:

```bash
# Test Monte Carlo simulation
singularity exec \
    -B /home/.../inputs:/inputs \
    -B /home/.../outputs:/outputs \
    -B /home/.../sim_outputs:/sim_outputs \
    map_t1_mapping.sif \
    python /code/run_mp2rage_simulation.py \
    --params_path /inputs/params.yml \
    --sim_output_path /sim_outputs/monte_carlo_test.npy \
    --num_trials 1000000 \
    --num_process 15 \
    --noise_std 0.005

# Test image creation using Monte Carlo
singularity exec \
    -B /home/.../inputs:/inputs \
    -B /home/.../outputs:/outputs \
    -B /home/.../sim_outputs:/sim_outputs \
    map_t1_mapping.sif \
    python /code/create_image.py \
    --params_path /inputs/params.yml \
    --input_folder /inputs \
    --output_folder /outputs \
    --num_process 15 \
    --image_type likelihood \
    --monte_carlo_path /sim_outputs/monte_carlo_test.npy```

