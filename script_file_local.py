#!/usr/bin/env python3
import subprocess
import os
from gcp_downloader import download_blob

# get core files
destination_folder = "/home/MAGMA/files/"
files_to_get = ["g1000_eur.bed","g1000_eur.bim",
	"g1000_eur.fam","g1000_eur.synonyms",
	"annot_try2.genes.annot","genelist.tsv"]
x = [download_blob("rgupta", "MAGMA_files/files_for_gcloud/"+file, 
	destination_folder+file) for file in files_to_get]

# get variants file
download_blob("ukb-mega-gwas-results", 
	"round2/annotations/variants.tsv.bgz", "/home/inputs/variants.tsv.bgz")
os.system("gunzip -c /home/inputs/variants.tsv.bgz > /home/inputs/variants.tsv")
os.system("rm /home/inputs/variants.tsv.bgz")

## Inputs
SUMMARY = os.environ['SUMMARY']
N = os.environ['N']
FOLD = os.environ['FOLD']

## Preprocess & run MAGMA
os.mkdir("/home/out/"+FOLD+"/")
subprocess.call(['/home/run_MAGMA.py',
	   			'--summary',SUMMARY,
       			'--N',N])

## Export to output location
# taskname folder contains genefiles folder as well as all gsa files
os.system("mv -r " + "/home/out/" + "/home/out/"+FOLD+"/")
os.system("mv -r " + "/home/MAGMA/genefiles" + "/home/out/"+FOLD+"/")
os.system("cp -r /home/out/ ${OUTPUT_PATH}")