#!/usr/bin/env bash

# DICOM folder
dataset="/nfs/masi/saundam1/Datasets/MP2RAGE"

# Output folder
output="/nfs/masi/saundam1/Outputs/MP2RAGE_converted"

# Loop over all directories in dataset
subjects=`ls $dataset`
for subject in $subjects
do
	# Loop over all directories in subject folder that include scan number and the word MP2RAGE
	scans=`ls -d $dataset/$subject/$subject/[0-9]*MP2RAGE*`
	for scan in $scans
	do
		# Loop over DICOM files in each scan
		dicoms=`ls $scan/DICOM/*.dcm`
		for dicom in $dicoms
		do
			# Make output folder if it doesn't exist
			save_folder="$output/$subject/`basename $scan`"
			mkdir -p $save_folder
			# Run conversion
			dcm2niix -o $save_folder -f %s -i y $dicom
		done
	done
done


