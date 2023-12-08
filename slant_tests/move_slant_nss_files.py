import os
import csv

def find_mp2rage_files(root_dir, csv_path, column_name):
    mp2rage_files = []
    
    # Read the CSV file and get the subject IDs from the specified column
    subject_ids = set()
    with open(csv_path, 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            subject_ids.add(row[column_name])

    # Walk through the root directory and its subdirectories
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Get the subject ID (the first folder after root_directory)
        subject_folder = os.path.relpath(dirpath, root_dir).split(os.path.sep)[0]

        # Check if the subject ID is in the CSV's column
        if subject_folder in subject_ids:
            # Check if the folder name contains the specified string
            if 'mp2rage_v2_1' in dirpath:
                # Check if the required file is present in the directory
                if 'mp2rage.nii.gz' in filenames:
                    # Construct the full file path
                    file_path = os.path.join(dirpath, 'mp2rage.nii.gz')

                    # Exceptions
                    if subject_folder == '335586' and file_path == '/nfs/masi/saundam1/datasets/MP2RAGE/335586/335586/MP2RAGE-x-335586-x-335586-x-mp2rage_v2_1-x-8ab013bf-ba2e-4d76-bf28-8c018abe13c0/MP2RAGE/mp2rage.nii.gz':
                        continue
                    
                    # Make directories
                    print(file_path)
                    slant_path = '/home/saundam1/temp_data/slant_mp2rage_nss'
                    os.makedirs(os.path.join(slant_path, subject_folder, 'in'), exist_ok=True)
                    os.makedirs(os.path.join(slant_path, subject_folder, 'out', 'pre'), exist_ok=True)
                    os.makedirs(os.path.join(slant_path, subject_folder, 'out', 'post'), exist_ok=True)
                    os.makedirs(os.path.join(slant_path, subject_folder, 'out', 'dl'), exist_ok=True)

                    # Copy the file to the new directory
                    os.system(f'cp {file_path} {os.path.join(slant_path, subject_folder, "in", "t1w.nii.gz")}')

root_directory = '/nfs/masi/saundam1/datasets/MP2RAGE'
csv_file_path = '/nfs/masi/saundam1/datasets/MP2RAGE_SIR_qMT/ground_truth_subjects.csv'
column_with_subject_ids = 'Subject'

mp2rage_files_list = find_mp2rage_files(root_directory, csv_file_path, column_with_subject_ids)
