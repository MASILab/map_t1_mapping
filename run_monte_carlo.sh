output_dir="/nfs/masi/saundam1/outputs/t1_mapping/distr"
basename="${output_dir}/counts_100M_s1_2"

# Run simulation for 2D and 3D
#python mp2rage_simulation.py --output_path $three_path --num_trials 100000000 --num_process 19 --all_inv_combos
#python mp2rage_simulation.py --output_path $two_path --num_trials 100000000 --num_process 19

for i in 0.001 0.005 0.01 0.015 0.02 0.025 0.05; do
    name="${basename}_${i}.npy"
    python mp2rage_simulation.py --output_path $name --num_trial 100000000 --num_process 15 --noise_std $i
done
