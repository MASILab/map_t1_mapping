# Normalize images to [0,1] and set background to 0

# Loop over subjects
for input_folder in /home/saundam1/temp_data/mp2rage_t1w_mask/*; do
    subj_id=`basename $input_folder`
    output_folder="/home/saundam1/temp_data/mp2rage_t1w_norm_ss/$subj_id"
    
    mkdir -p $output_folder

    cp /home/saundam1/temp_data/mp2rage_t1w_norm/$subj_id/t1w.nii.gz $output_folder/t1w.nii.gz
    
    gzip -c /nfs/masi/saundam1/outputs/t1_mapping/t1w_strip/$subj_id/mask.nii > $output_folder/t1w_label.nii.gz

done
