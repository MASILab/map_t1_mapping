# Register the ground truth T1 maps to the generated T1 maps
dataDir="/nfs/masi/saundam1/outputs/t1_mapping"
regDir="$dataDir/t1w_strip_rigid"
maskDir="$dataDir/ground_truth_masks"

inputDir="$dataDir/sensitivity/t1_maps_s1_2_0.1"
outputDir="${inputDir}_mask"

tempDir="/nfs/masi/saundam1/temp"

filename="t1_map.nii.gz"
#for subj_path in "$inputDir"/*/; do
for subj_path in "$inputDir"/*/; do
    subj_id=`basename $subj_path`
    echo $subj_id

    # Make appropriate folders
    mkdir -p $outputDir/$subj_id $tempDir/$subj_id

    # Apply trasformation
    antsApplyTransforms -d 3 -i $inputDir/$subj_id/$filename -r $regDir/$subj_id/reg_t1_map.nii.gz -t $regDir/$subj_id/0GenericAffine.mat -n Linear -o $tempDir/$subj_id/$filename

    # Apply mask
    fslmaths $tempDir/$subj_id/$filename -mas $maskDir/$subj_id/mask.nii $outputDir/$subj_id/$filename

done | tee /dev/tty | tqdm --total `ls -d $inputDir/*/ | wc -l` >/dev/null

# Delete empty folders in output
rm -r $tempDir
find $outputDir -type d -empty -delete
