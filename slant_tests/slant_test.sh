# Segment T1w images using SLANT

# Loop over subjects
for input_folder in /home/saundam1/singularity_test//334264; do
    subj_id=`basename $input_folder`
    output_folder="/home/saundam1/singularity_test/mp2rage_t1w_norm_slant_ss/$subj_id"
    
    mkdir -p $output_folder $output_folder/dl $output_folder/pre $output_folder/post

    # fslmaths /nfs/masi/saundam1/outputs/t1_mapping/mp2rage_t1w/$subj_id/t1w.nii.gz -mas /nfs/masi/saundam1/outputs/t1_mapping/t1w_strip/$subj_id/mask.nii $output_folder/t1w.nii.gz

    # Run singularity
    #singularity exec --nv -B $input_folder:/INPUTS/ -B $output_folder:/OUTPUTS/ /home/saundam1/singularity/slant_gpu_v1.1.0.simg /extra/run_deep_brain_seg.sh
    echo $input_folder

    export cmd="/home/local/VANDERBILT/caily/Apps/singularity/singularity-ce-3.8.0/bin/singularity exec --nv -B $input_folder:/opt/slant/matlab/input_pre -B $input_folder:/opt/slant/matlab/input_post -B $output_folder/pre:/opt/slant/matlab/output_pre -B $output_folder/dl:/opt/slant/dl/working_dir -B $output_folder/post:/opt/slant/matlab/output_post -e /home/saundam1/singularity_test/ssSLANT_v2.0.simg /opt/slant/run.sh"

    echo $cmd
    $cmd

done
