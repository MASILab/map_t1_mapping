# Run skull-stripped SLANT on BLSA data
for subject in BLSA_4622_01-0_10 BLSA_1099_19-0_10 BLSA_5706_09-0_10 BLSA_7690_02-0_10 BLSA_4684_01-0_10 BLSA_1012_19-0_10; do
    output_folder="/home/saundam1/temp_data/slant_test_blsa_v4/$subject"
    
    mkdir -p $output_folder/in/{pre,post} $output_folder/out/{pre,post,dl}

    cp /nfs/masi/BLSA/$subject/SCANS/MPRAGE/NIFTI/*.nii.gz $output_folder/${subject}_MPRAGE.nii.gz
    
    # Strip skulls to create mask
    ~/Documents/synthstrip/synthstrip-singularity -i $output_folder/${subject}_MPRAGE.nii.gz -o $output_folder/in/pre/mprage_ss.nii.gz -m $output_folder/in/pre/mprage_ss_label.nii.gz
done
