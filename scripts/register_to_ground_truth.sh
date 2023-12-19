# Register the ground truth T1 maps to the generated T1 maps
# dataDir="/nfs/masi/saundam1/outputs/t1_mapping"
# outputDir="$dataDir/t1w_strip_rigid"
# movingDir="$dataDir/t1w_strip"
# fixedDir="$dataDir/t1_maps_truth_mask"
dataDir="/home/saundam1/temp_data"
outputDir="$dataDir/mp2rage_t1w_strip_rigid"
movingDir="$dataDir/mp2rage_t1w_strip"
fixedDir="$dataDir/t1_maps_truth"

#for subj_path in "$fixedDir"/*/; do
for subj_path in $movingDir/*; do # $movingDir/*; do
    subj_id=`basename $subj_path`
    #subj_id=$subj_path
    echo $subj_id

    # Make appropriate folders
    mkdir -p $outputDir/$subj_id

    # Perform registrationc
    antsRegistration --verbose 0 --dimensionality 3 --float 0 \
        --collapse-output-transforms 1 \
        --output [ $outputDir/$subj_id/,$outputDir/$subj_id/t1w.nii.gz,$outputDir/$subj_id/InverseWarped.nii.gz ] \
        --interpolation Linear \
        --use-histogram-matching 0 \
        --winsorize-image-intensities [ 0.005,0.995 ] \
        --initial-moving-transform [ $fixedDir/$subj_id/filtered_t1_map.nii.gz,$movingDir/$subj_id/t1w.nii.gz, 0] \
        --transform Rigid[ 0.2 ] \
        --metric MI[ $fixedDir/$subj_id/filtered_t1_map.nii.gz,$movingDir/$subj_id/t1w.nii.gz,1,32,Regular,0.5 ]\
        --convergence [ 2000x1000x500x200,1e-8,10 ] \
        --shrink-factors 8x4x2x1 \
        --smoothing-sigmas 4x3x2x1vox \
        # --x $movingDir/$subj_id/mask.nii.gz

done | tee /dev/tty | tqdm --total `ls -d $movingDir/*/ | wc -l` >/dev/null 
