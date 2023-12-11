# Register the ground truth T1 maps to the generated T1 maps
dataDir="/nfs/masi/saundam1/outputs/t1_mapping"
regDir="$dataDir/t1w_strip_rigid"
maskDir="$dataDir/ground_truth_masks"

inputDir="$dataDir/slant_mp2rage_nss"
outputDir="$dataDir/slant_mp2rage_nss_mask"

tempDir="/home/saundam1/tmp"

for subj_path in 335561; do
    subj_id=$(basename $subj_path)
    echo $subj_id
    filename="$subj_id/out/post/FinalResult/t1w_seg.nii.gz"

    # Make appropriate folders
    mkdir -p $outputDir/$subj_id $tempDir/$subj_id

    # Apply trasformation
    antsApplyTransforms -d 3 -i $inputDir/$filename -r $regDir/$subj_id/reg_t1_map.nii.gz -t $regDir/$subj_id/0GenericAffine.mat -n NearestNeighbor -o $tempDir/$subj_id/t1w_seg.nii.gz

    # Apply mask
    fslmaths $tempDir/$subj_id/t1w_seg.nii.gz -mas $maskDir/$subj_id/mask.nii $outputDir/$subj_id/t1w_seg.nii.gz

    # Delete empty folders in output
    rm -r $tempDir
    find $outputDir -type d -empty -delete
done