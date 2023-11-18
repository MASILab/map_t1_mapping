# Register the ground truth T1 maps to the generated T1 maps
dataDir="/nfs/masi/saundam1/outputs/t1_mapping"
inputDir="$dataDir/t1_maps_likelihood_reg"
outputDir="$dataDir/t1_maps_likelihood_mask"
maskDir="$dataDir/ground_truth_masks"

#for subj_path in "$inputDir"/*/; do
for subj_path in "$inputDir"/*/; do
    subj_id=`basename $subj_path`
    echo $subj_id

    # Make appropriate folders
    mkdir -p $outputDir/$subj_id

    # Apply mask
    fslmaths $inputDir/$subj_id/t1_map.nii -mas $maskDir/$subj_id/mask.nii $outputDir/$subj_id/t1_map.nii

done | tee /dev/tty | tqdm --total `ls -d $inputDir/*/ | wc -l` >/dev/null
