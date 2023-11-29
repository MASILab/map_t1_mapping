# Segment T1w images using SLANT

# Loop over subjects
for input_folder in /home/saundam1/temp_data/mp2rage_t1w_mask/*; do
    subj_id=`basename $input_folder`
    output_folder="/home/saundam1/temp_data/mp2rage_t1w_mask_slant/$subj_id"
    
    mkdir -p $output_folder

    # fslmaths /nfs/masi/saundam1/outputs/t1_mapping/mp2rage_t1w/$subj_id/t1w.nii.gz -mas /nfs/masi/saundam1/outputs/t1_mapping/t1w_strip/$subj_id/mask.nii $output_folder/t1w.nii.gz

    # Run singularity
    singularity exec --nv -B $input_folder:/INPUTS/ -B $output_folder:/OUTPUTS/ /home/saundam1/singularity/slant_gpu_v1.1.0.simg /extra/run_deep_brain_seg.sh

done