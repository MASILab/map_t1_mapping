output_dir="/nfs/masi/saundam1/outputs/t1_mapping/distr"
basename="${output_dir}/counts_100M"

# Run simulation for 2D and 3D
python mp2rage_simulation_fix.py --output_path ${basename}_s1_2_fix.npy --num_trials 100000000 --num_process 19 --times 1 2
python mp2rage_simulation_fix.py --output_path ${basename}_s1_3_fix.npy --num_trials 100000000 --num_process 19 --times 1 3
python mp2rage_simulation_fix.py --output_path ${basename}_all_fix.npy --num_trials 100000000 --num_process 19 --times 1 2 3
#python mp2rage_simulation.py --output_path $two_path --num_trials 100000000 --num_process 19

# for i in 0.005; do
#     name="${basename}_${i}.npy"
#     python mp2rage_simulation_fix.py --output_path $name --num_trial 1000000 --num_process 19 --noise_std $i --times 1 2
# done
