#!/usr/bin/env bash

# PAR/REC folder
dataset="/home/saundam1/temp_data/7T_SIRqMT_R1maps/SIRqMT_parrec"

# Output folder
output="/home/saundam1/temp_data/7T_SIRqMT_R1maps/SIRqMT_nii"

# Loop over all directories in dataset
subjects=`ls $dataset`
for subject in $subjects
do
subject_id=$(echo "$subject" | cut -d'_' -f2)
echo $subject_id
	# Loop over all directories in subject folder that include scan number and the word MP2RAGE
	scans=`ls -d $dataset`
	for scan in $scans
	do
		# Loop over DICOM files in each scan
		dicoms=`ls $scan/*.REC`
		for dicom in $dicoms
		do
			# Make output folder if it doesn't exist
			save_folder="$output/$subject_id/"
			echo $save_folder
			mkdir -p $save_folder
			# Run conversion
			dcm2niix -o $save_folder -f %s $dicom
		done
	done
done


