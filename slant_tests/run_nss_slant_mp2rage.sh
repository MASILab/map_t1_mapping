# Segment T1w images using SLANT-TICV (nss)
for input_folder in /home/saundam1/temp_data/slant_mp2rage_nss/*; do
    echo $input_folder
    export cmd="singularity exec -B $input_folder/in:/opt/slant/matlab/input_pre -B $input_folder/in:/opt/slant/matlab/input_post -B $input_folder/out/pre:/opt/slant/matlab/output_pre -B $input_folder/out/dl:/opt/slant/dl/working_dir -B $input_folder/out/post:/opt/slant/matlab/output_post -e /home/saundam1/singularity/nssSLANT_v1.2.simg /opt/slant/run.sh"
    echo $cmd
    $cmd
done
