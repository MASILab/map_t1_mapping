# Register the generated T1 maps to ground truth
dataDir="/nfs/masi/saundam1/outputs/t1_mapping"
regDir="$dataDir/robust_t1w_0.25_synthstrip_reg"
maskDir="$dataDir/ground_truth_masks"

tempDir="/nfs/masi/saundam1/temp"

inputDir="$dataDir/results/sensitivity/t1_maps_likelihood_s1_2_0.005"
filename="t1_map.nii.gz"

task() {
    inputDir="$dataDir/results/sensitivity/t1_maps_likelihood_$3_$2"
    outputDir="${inputDir}_mask"

    subj_id=`basename $1`
    echo $subj_id

    # Make appropriate folders
    mkdir -p $outputDir/$subj_id $tempDir/$subj_id

    # Apply trasformation
    antsApplyTransforms -d 3 -i $inputDir/$subj_id/$filename -r $regDir/$subj_id/t1w.nii.gz -t $regDir/$subj_id/0GenericAffine.mat -n NearestNeighbor -o $tempDir/$subj_id/$filename

    # Apply mask
    fslmaths $tempDir/$subj_id/$filename -mas $maskDir/$subj_id/mask.nii.gz $outputDir/$subj_id/$filename

    # If you want no mask
    # cp $tempDir/$subj_id/$filename $outputDir/$subj_id/$filename
}

#for subj_path in "$inputDir"/*/; do

for method in "s1_2" "s1_3" "all"; do
    for noise_level in 0.0005 0.001 0.005 0.01 0.015 0.02; do
    echo "Method: $method, noise level: $noise_level"
        for subj_path in "$inputDir"/*/; do
            task "$subj_path" "$noise_level" "$method" &
        done | tee /dev/tty | tqdm --total `ls -d $inputDir/*/ | wc -l` >/dev/null

        wait
    done
done 

# Delete empty folders in output
rm -r $tempDir
find $outputDir -type d -empty -delete
