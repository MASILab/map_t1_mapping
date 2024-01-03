# Copy robust T1-weighted files
inDir="/home/saundam1/temp_data/slant_mp2rage_nss"
outDir="/home/saundam1/temp_data/robust_t1w"

for subject_path in $inDir/*; do
    subj_id=`basename $subject_path`

    # Make appropriate folders
    mkdir -p $outDir/$subj_id

    # Copy files
    cp $subject_path/in/t1w.nii.gz $outDir/$subj_id/t1w.nii.gz

done | tee /dev/tty | tqdm --total `ls -d $inDir/*/ | wc -l` >/dev/null