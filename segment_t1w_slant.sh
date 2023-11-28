# Segment T1w images using SLANT

# Loop over subjects
for input_folder in /nfs/masi/saundam1/outputs/t1_mapping/mp2rage_t1w/*; do
    subj_id=`basename $input_folder`
    output_folder="/nfs/masi/saundam1/outputs/t1_mapping/mp2rage_t1w_slant/$subj_id"
    
    mkdir -p $output_folder

    # Run singularity
    singularity exec --nv -B $input_folder:/INPUTS/ -B $output_folder:/OUTPUTS/ /home/saundam1/singularity/slant_gpu_v1.1.0.simg /extra/run_deep_brain_seg.sh

done
