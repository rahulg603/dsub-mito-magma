#!/usr/bin/env python3
import subprocess
import os
from gcp_downloader import download_blob

# generate output filesystem
os.makedirs("/mnt/data/MAGMA/")
os.makedirs("/mnt/data/MAGMA/files/")

os.makedirs("/mnt/data/inputs/")
os.makedirs("/mnt/data/inputs/modified_stats/")
os.makedirs("/mnt/data/inputs/original_stats/")

FOLD = os.environ['FOLD']
os.makedirs("/mnt/data/MAGMA_OUT/")
output_folder = "/mnt/data/MAGMA_OUT/" + FOLD + "/"
os.makedirs(output_folder)
os.makedirs("/mnt/data/MAGMA_OUT/" + FOLD + "/genefiles/")

# get core files
destination_folder = "/mnt/data/MAGMA/files/"
files_to_get = ["g1000_eur.bed", "g1000_eur.bim",
                "g1000_eur.fam", "g1000_eur.synonyms",
                "GRCh37_5kbup_1.5kbdown.genes.annot", "genelist.tsv"]
x = [download_blob("rgupta", "MAGMA_files/files_for_gcloud/" + file,
     destination_folder + file) for file in files_to_get]

# get variants file
download_blob("rgupta",
              "MAGMA_files/files_for_gcloud/variants_filtered.tsv",
              "/mnt/data/inputs/variants.tsv")

# This older version downloads the variants.tsv from the source.
# The above version on rgupta has been trimmed already, info >= 0.8.
# download_blob("ukb-mega-gwas-results",
#               "round2/annotations/variants.tsv.bgz",
#               "/mnt/data/inputs/variants.tsv.bgz")
# os.system("gunzip -c /mnt/data/inputs/variants.tsv.bgz > /mnt/data/inputs/variants.tsv")
# os.system("rm /mnt/data/inputs/variants.tsv.bgz")

# Inputs
SUMMARY = os.environ['SUMMARY']

print("File folder:")
print(os.listdir(destination_folder))
print("Inputs folder:")
print(os.listdir("/mnt/data/inputs/"))

# Preprocess & run MAGMA
subprocess.call(['/home/run_MAGMA.py',
                 '--summary', SUMMARY,
                 '--fold', FOLD])

# Export to output location
# taskname folder contains genefiles folder as well as all gsa files
os.system("cp -r " + "/mnt/data/MAGMA_OUT/" + FOLD + " ${OUTPUT_PATH}")
