# Register the ground truth T1 maps to the generated T1 maps
dataDir="/nfs/masi/saundam1/outputs/t1_mapping"
outputDir="$dataDir/t1_maps_lut_rigid"
movingDir="$dataDir/t1_maps_lut"
fixedDir="$dataDir/mp2rage_sir_qmt"

for subj_path in "$movingDir"/*/; do 
    subj_id=`basename $subj_path`
    echo $subj_id

    # Make appropriate folders
    mkdir -p $outputDir/$subj_id

    # Perform registration
    antsRegistration --verbose 0 --dimensionality 3 --float 0 \
        --collapse-output-transforms 1 \
        --output [ $outputDir/$subj_id/,$outputDir/$subj_id/Warped.nii.gz,$outputDir/$subj_id/InverseWarped.nii.gz ] \
        --interpolation Linear \
        --use-histogram-matching 0 \
        --winsorize-image-intensities [ 0.005,0.995 ] \
        --initial-moving-transform [ $fixedDir/$subj_id/filtered_t1_map.nii,$movingDir/$subj_id/t1_map.nii, 0] \
        --transform Rigid[ 0.1 ] \
        --metric MI[ $fixedDir/$subj_id/filtered_t1_map.nii,$movingDir/$subj_id/t1_map.nii,1,32,Regular,0.25 ]\
        --convergence [ 1000x500x250x100,1e-6,10 ] \
        --shrink-factors 12x8x4x2 \
        --smoothing-sigmas 4x3x2x1vox
done
