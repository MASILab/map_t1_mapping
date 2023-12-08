# Register the ground truth T1 maps to the generated T1 maps
#dataDir="/nfs/masi/saundam1/outputs/t1_mapping"
dataDir="/home/saundam1/temp_data"
regDir="/nfs/masi/saundam1/outputs/t1_mapping/t1w_strip_rigid"
maskDir="/nfs/masi/saundam1/outputs/t1_mapping/ground_truth_masks"
saveDir="/nfs/masi/saundam1/outputs/t1_mapping"

inputDir="$dataDir/slant_test_mp2rage_nss_xnat/out/post/FinalResult"
outputDir="${saveDir}/slant_test_mp2rage_nss_xnat_mask"

tempDir="/home/saundam1/tmp"

filename="mp2rage_seg.nii.gz"
#for subj_path in "$inputDir"/*/; do
# Make appropriate folders
subj_id="334264"
mkdir -p $outputDir/$subj_id $tempDir/$subj_id

# Apply trasformation
antsApplyTransforms -d 3 -i $inputDir/$filename -r $regDir/$subj_id/reg_t1_map.nii.gz -t $regDir/$subj_id/0GenericAffine.mat -n NearestNeighbor -o $tempDir/$subj_id/$filename

# Apply mask
fslmaths $tempDir/$subj_id/$filename -mas $maskDir/$subj_id/mask.nii $outputDir/$subj_id/$filename

# Delete empty folders in output
rm -r $tempDir
find $outputDir -type d -empty -delete
