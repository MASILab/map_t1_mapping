antsRegistration --verbose 1 --dimensionality 3 --float 0 \
    --collapse-output-transforms 1 \
    --output [ t1_maps_truth_reg/,t1_maps_truth_reg/Warped.nii.gz,t1_maps_truth_reg/InverseWarped.nii.gz ] \
    --interpolation Linear \
    --use-histogram-matching 0 \
    --winsorize-image-intensities [ 0.005,0.995 ] \
    --initial-moving-transform [ t1_maps_lut/334264/t1_map.nii,mp2rage_sir_qmt/334264/filtered_t1_map.nii,0] \
    --transform Rigid[ 0.1 ] \
    --metric MI[ t1_maps_lut/334264/t1_map.nii,mp2rage_sir_qmt/334264/filtered_t1_map.nii,1,32,Regular,0.25 ]\
    --convergence [ 1000x500x250x100,1e-6,10 ] \
    --shrink-factors 12x8x4x2 \
    --smoothing-sigmas 4x3x2x1vox

