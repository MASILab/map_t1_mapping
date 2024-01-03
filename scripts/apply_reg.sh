# Register the generated T1 maps to ground truth
dataDir="/nfs/masi/saundam1/outputs/t1_mapping"
regDir="$dataDir/robust_t1w_0.25_synthstrip_reg"
maskDir="$dataDir/ground_truth_masks"

inputDir="$dataDir/slant_mp2rage_nss_0.25"
outputDir="${inputDir}_mask"

tempDir="/nfs/masi/saundam1/temp"

filename="t1w_seg.nii.gz"
#for subj_path in "$inputDir"/*/; do
for subj_path in "$inputDir"/*/; do
    subj_id=`basename $subj_path`
    echo $subj_id

    # Make appropriate folders
    mkdir -p $outputDir/$subj_id $tempDir/$subj_id

    # Apply trasformation
    antsApplyTransforms -d 3 -i $inputDir/$subj_id/$filename -r $regDir/$subj_id/t1w.nii.gz -t $regDir/$subj_id/0GenericAffine.mat -n NearestNeighbor -o $tempDir/$subj_id/$filename

    # Apply mask
    fslmaths $tempDir/$subj_id/$filename -mas $maskDir/$subj_id/mask.nii.gz $outputDir/$subj_id/$filename

    # If you want no mask
    # cp $tempDir/$subj_id/$filename $outputDir/$subj_id/$filename

done | tee /dev/tty | tqdm --total `ls -d $inputDir/*/ | wc -l` >/dev/null

# Delete empty folders in output
rm -r $tempDir
find $outputDir -type d -empty -delete
