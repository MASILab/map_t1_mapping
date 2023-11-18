# Register the ground truth T1 maps to the generated T1 maps
dataDir="/nfs/masi/saundam1/outputs/t1_mapping"
regDir="$dataDir/t1_maps_likelihood_strip_rigid"
maskDir="$dataDir/ground_truth_masks"
inputDir="$dataDir/t1_maps_likelihood_s1_2"
outputDir="$dataDir/t1_maps_likelihood_s1_2_mask"

tempDir="/nfs/masi/saundam1/temp"

#for subj_path in "$inputDir"/*/; do
for subj_path in "$inputDir"/*/; do
    subj_id=`basename $subj_path`
    echo $subj_id

    # Make appropriate folders
    mkdir -p $outputDir/$subj_id $tempDir/$subj_id

    # Apply trasformation
    antsApplyTransforms -d 3 -i $inputDir/$subj_id/t1_map.nii -r $regDir/$subj_id/reg_t1_map.nii.gz -t $regDir/$subj_id/0GenericAffine.mat -n Linear -o $tempDir/$subj_id/t1_map.nii

    # Apply mask
    fslmaths $tempDir/$subj_id/t1_map.nii -mas $maskDir/$subj_id/mask.nii $outputDir/$subj_id/t1_map.nii

    # Delete empty folders in output
    rm -r $tempDir
    find $outputDir -type d -empty -delete
    
done | tee /dev/tty | tqdm --total `ls -d $inputDir/*/ | wc -l` >/dev/null
