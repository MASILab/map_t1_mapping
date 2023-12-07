# Segment T1w images using SLANT

# Loop over subjects

for subject in BLSA_4622_01-0_10 BLSA_1099_19-0_10 BLSA_5706_09-0_10 BLSA_7690_02-0_10 BLSA_4684_01-0_10 BLSA_1012_19-0_10; do

    input_folder=/home/saundam1/temp_data/slant_test_blsa_v4/$subject
    export cmd="/home/local/VANDERBILT/caily/Apps/singularity/singularity-ce-3.8.0/bin/singularity exec -B $input_folder/in/pre:/opt/slant/matlab/input_pre -B $input_folder/in/post:/opt/slant/matlab/input_post -B $input_folder/out/pre:/opt/slant/matlab/output_pre -B $input_folder/out/dl:/opt/slant/dl/working_dir -B $input_folder/out/post:/opt/slant/matlab/output_post -e /home/saundam1/singularity/ssSLANT_v4.0.sif /opt/slant/run.sh"
    echo $cmd
    $cmd

done
