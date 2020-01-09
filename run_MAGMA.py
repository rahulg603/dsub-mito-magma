#!/usr/bin/env python3
import sys
from subprocess import check_output
import os
from gcp_downloader import download_blob
import pandas as pd
import hail as hl
hl.init()


# set up function to check line count
def wc(filename):
    return(int(check_output(["wc", "-l", filename]).split()[0]) - 1)


# obtain argument-value pairs
arg_vals = {}
for i in range(1, len(sys.argv), 2):
    arg_vals[sys.argv[i]] = sys.argv[i + 1]

fold_for_task = arg_vals["--fold"]

# set directories
reference_loc = "/mnt/data/MAGMA/files/g1000_eur"
gene_annot_loc = "/mnt/data/MAGMA/files/GRCh37_5kbup_1.5kbdown.genes.annot"
program_loc = "/home/MAGMA/magma"
genefile_output_loc = "/mnt/data/MAGMA_OUT/" + fold_for_task + "/genefiles/"
geneset_loc = "/mnt/data/MAGMA/files/genelist.tsv"
original_summstat_loc = "/mnt/data/inputs/original_stats/"
modified_summstat_loc = "/mnt/data/inputs/modified_stats/"
variant_loc = "/mnt/data/inputs/"
p_analysis_output_loc = "/mnt/data/MAGMA_OUT/" + fold_for_task + "/"

all_stat_files = arg_vals["--summary"]
split_files = all_stat_files.split(":")

# directions
dirs = ["pos", "neg", "both"]

# load in variant table
hl_variants_tbl = hl.import_table(variant_loc + "variants.tsv", impute=True)
hl_variants_tbl = hl_variants_tbl.key_by("variant")

# This has been commented out because we have trimmed the variants table
# locally.
# hl_variants_tbl = hl_variants_tbl.filter(hl_variants_tbl.info >= 0.8)
# var_new_size = hl_variants_tbl.count()

row_list = []
for file in split_files:
    # first download the file
    # gs://ukb-mega-gwas-results/round2/additive-tsvs/
    # *.gwas.imputed_v3.{female, male, both_sexes}.tsv.bgz
    original_sumstat_file_loc = original_summstat_loc + file
    download_blob("ukb-mega-gwas-results", "round2/additive-tsvs/" + file + ".bgz",
                  original_sumstat_file_loc + ".bgz")
    os.system("gunzip -c " + original_sumstat_file_loc + \
              ".bgz > " + original_sumstat_file_loc)
    sumstats_original_nrow = wc(original_sumstat_file_loc)

    # next merge this with the variant information
    hl_sumstats = hl.import_table(original_sumstat_file_loc, impute=True)
    hl_sumstats = hl_sumstats.key_by("variant")
    # sumstats_original_nrow_old = hl_sumstats.count()

    hl_sumstats = hl_sumstats.annotate(rsid=hl_variants_tbl[hl_sumstats.variant].rsid)
    hl_sumstats = hl_sumstats.rename({"pval": "P", "rsid": "SNP"})
    hl_sumstats = hl_sumstats.select(hl_sumstats.P, hl_sumstats.SNP,
                                     hl_sumstats.low_confidence_variant,
                                     hl_sumstats.minor_AF,
                                     hl_sumstats.n_complete_samples)
    hl_sumstats = hl_sumstats.filter(hl.is_missing(hl_sumstats.SNP) |
                                     hl.is_nan(hl_sumstats.P) |
                                     hl.is_nan(hl_sumstats.n_complete_samples) |
                                     hl.is_nan(hl_sumstats.minor_AF) |
                                     hl.is_missing(hl_sumstats.low_confidence_variant),
                                     keep=False)
    sumstats_new_nrow = hl_sumstats.count()

    # filter/perform QC on the data
    hl_sumstats = hl_sumstats.filter((hl_sumstats.low_confidence_variant == False) &
                                     (hl_sumstats.minor_AF >= 0.01))
    # sumstats_final_nrow_old = hl_sumstats.count()

    print("Finished QC, " + file)

    # save this data
    modified_sumstat_file_loc = modified_summstat_loc + file
    hl_sumstats.export(modified_sumstat_file_loc)
    sumstats_final_nrow = wc(modified_sumstat_file_loc)

    # clean up inputs directory
    os.system("cd " + original_summstat_loc + " && ls | grep .tsv | xargs rm")

    # run MAGMA
    cmd_genefile = program_loc + " --bfile " + reference_loc + \
        " --pval " + modified_sumstat_file_loc + " ncol=n_complete_samples" + \
        " --gene-annot " + gene_annot_loc + \
        " --out " + genefile_output_loc + file
    print("Command for genefile generation: " + cmd_genefile)
    os.system(cmd_genefile)

    for direction in dirs:
        cmd_annotation = program_loc + " --gene-results " + \
            genefile_output_loc + file + ".genes.raw" + \
            " --set-annot " + geneset_loc + " --model direction=" + direction + \
            " --out " + p_analysis_output_loc + "analysis_" + file + "_" + direction
        print("Command for p val analysis generation: " + cmd_annotation)
        os.system(cmd_annotation)

    thisdf_row = {"summstats": file,
                  "sumstats_original_nrow": sumstats_original_nrow,
                  "sumstats_post_merge_nrow": sumstats_new_nrow,
                  "sumstats_final_nrow": sumstats_final_nrow}
    row_list.append(thisdf_row)

df = pd.DataFrame(row_list, columns=["summstats",
                                     "sumstats_original_nrow",
                                     "sumstats_post_merge_nrow",
                                     "sumstats_final_nrow"])
df.to_csv(p_analysis_output_loc + 'run_statistics.csv')

print("Modified summary stat location after completion: ",
      os.listdir(modified_summstat_loc))
