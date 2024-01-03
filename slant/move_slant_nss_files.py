import os
import csv
import t1_mapping

csv_path = '/nfs/masi/saundam1/datasets/MP2RAGE_SIR_qMT/ground_truth_subjects.csv'

subject_ids = set()
with open(csv_path, 'r') as csv_file:
    csv_reader = csv.DictReader(csv_file)
    for row in csv_reader:
        subject_ids.add(row['Subject'])

# Copy over robust T1 
slant_path = '/home/saundam1/temp_data/slant_mp2rage_nss_0.25'
t1w_path = '/nfs/masi/saundam1/outputs/t1_mapping/robust_t1w_0.25'
for subj_id in subject_ids:
    print(subj_id)
    file_path = os.path.join(t1w_path, str(subj_id), 'robust_t1w.nii.gz')
    os.makedirs(os.path.join(slant_path, str(subj_id), 'in'), exist_ok=True)
    os.makedirs(os.path.join(slant_path, str(subj_id), 'out', 'pre'), exist_ok=True)
    os.makedirs(os.path.join(slant_path, str(subj_id), 'out', 'post'), exist_ok=True)
    os.makedirs(os.path.join(slant_path, str(subj_id), 'out', 'dl'), exist_ok=True)

    # Copy the file to the new directory
    os.system(f'cp {file_path} {os.path.join(slant_path, str(subj_id), "in", "t1w.nii.gz")}')