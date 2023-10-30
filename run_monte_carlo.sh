output_dir="/nfs/masi/saundam1/outputs/t1_mapping/distr"
two_path="${output_dir}/counts_100M_spacing.npy"
three_path="${output_dir}/counts_100M_spacing_full.npy"

# Run simulation for 2D and 3D
python mp2rage_simulation.py --output_path $three_path --num_trials 100000000 --num_process 19 --all_inv_combos
python mp2rage_simulation.py --output_path $two_path --num_trials 100000000 --num_process 19
