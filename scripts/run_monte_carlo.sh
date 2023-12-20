output_dir="/nfs/masi/saundam1/outputs/t1_mapping/distr"
#output_dir="/home/saundam1/temp_data/distr"
basename="${output_dir}/counts_100M"

# Run simulation for 2D and 3D
num_trials=100000000 
#num_trials=100000
for noise_std in 0.0025; do
    python mp2rage_simulation.py --output_path ${basename}_all_$noise_std.npy --num_trials $num_trials --num_process 19 --times 1 2 3 --noise_std $noise_std
    python mp2rage_simulation.py --output_path ${basename}_s1_3_$noise_std.npy --num_trials $num_trials --num_process 19 --times 1 3 --noise_std $noise_std
#    python mp2rage_simulation.py --output_path ${basename}_s1_2_$noise_std.npy --num_trials $num_trials --num_process 19 --times 1 2 --noise_std $noise_std
#python mp2rage_simulation.py --output_path $two_path --num_trials 100000000 --num_process 19
done
# for i in 0.005; do
#     name="${basename}_${i}.npy"
#     python mp2rage_simulation_fix.py --output_path $name --num_trial 1000000 --num_process 19 --noise_std $i --times 1 2
# done
