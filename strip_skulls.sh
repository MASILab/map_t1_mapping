# Register the ground truth T1 maps to the generated T1 maps
dataDir="/nfs/masi/saundam1/outputs/t1_mapping"
inputDir="$dataDir/mp2rage_t1w"
stripDir="$dataDir/t1w_strip"
outputDir="$dataDir/t1w_strip_rigid"
fixedDir="$dataDir/ground_truth_masks"

#for subj_path in "$fixedDir"/*/; do
for subj_path in "$fixedDir"/*/; do
    subj_id=`basename $subj_path`
    echo $subj_id

    # Make appropriate folders
    mkdir -p $outputDir/$subj_id
    mkdir -p $stripDir/$subj_id

    # Perform skull stripping
    ../synthstrip/synthstrip-singularity -i $inputDir/$subj_id/t1w.nii -o $stripDir/$subj_id/t1w.nii -m $stripDir/$subj_id/mask.nii 

done | tee /dev/tty | tqdm --total `ls -d $fixedDir/*/ | wc -l` >/dev/null
