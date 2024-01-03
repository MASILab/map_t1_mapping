# Register the ground truth T1 maps to the generated T1 maps
dataDir="/nfs/masi/saundam1/outputs/t1_mapping"
inputDir="$dataDir/robust_t1w_0.25"
stripDir="$dataDir/robust_t1w_0.25_synthstrip"
# dataDir="/home/saundam1/temp_data/"
# inputDir="$dataDir/slant_mp2rage_nss"
# stripDir="$dataDir/mp2rage_t1w_strip"

#for subj_path in "$inputDir"/*/; do
for subj_path in "$inputDir"/*/; do
    subj_id=`basename $subj_path`
    echo $subj_id

    # Make appropriate folders
    mkdir -p $stripDir/$subj_id

    # Perform skull stripping
    ~/Documents/synthstrip/synthstrip-singularity -i $inputDir/$subj_id/robust_t1w.nii.gz -o $stripDir/$subj_id/t1w.nii.gz -m $stripDir/$subj_id/mask.nii.gz 

done | tee /dev/tty | tqdm --total `ls -d $fixedDir/*/ | wc -l` >/dev/null
