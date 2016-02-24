#!/usr/bin/env Rscript

###########################################
# check command line
library(getopt)

#long, short, argmask, datatype, desk
#argmask 0=no arg, 1=req, 2=optional
args <- rbind(c("bam", "b", 1, "character", "Tumor low-pass WGS bam file"),
              c("output", "o", 1, "character", "Output tsv with bed file with segmented copy numbers"),
              c("background", "x", 1, "character", "Background set to use, as a RData file"))

# opts <- getopt(args,opt = c("--bam", "~/L11466T_wgs.bam",
#                            "--output", "~/tmp/L11466T_wgs.qdnaseq.txt",
#                            "--background", "~/bin/autoseqer/resources/qdnaseq_background.Rdata") )

opts <- getopt(args)
if(is.null(opts$bam)){
  stop("Must specify input bam file --bam/-b.")
}
if(is.null(opts$output)){
  stop("Must specify output tsv file name --segments/-s.")
}
if(is.null(opts$background)){
  stop("Must specify background file --background/-x.")
}

###########################################
# load packages
library(data.table)
library(QDNAseq)
library(CGHcall)
library(Biobase)

###########################################
# run qdnaseq

bgReadCounts <- readRDS(opts$background)

bins <- getBinAnnotations(binSize=15)
readCounts <- binReadCounts(bins, bamfiles=opts$bam)
sampleName <- readCounts@phenoData@data$name
if( sampleName %in% bgReadCounts@phenoData@data$name ){
  allReadCounts <- bgReadCounts
} else {
  allReadCounts <- combine(readCounts, bgReadCounts) 
}

readCountsFiltered <- applyFilters(allReadCounts,residual=TRUE, blacklist=TRUE)
readCountsFiltered <- estimateCorrection(readCountsFiltered)
copyNumbers <- correctBins(readCountsFiltered)
copyNumbersNormalized <- normalizeBins(copyNumbers)
copyNumbersSmooth <- smoothOutlierBins(copyNumbersNormalized)
copyNumbersSegmented <- segmentBins(copyNumbersSmooth)
copyNumbersSegmentedNormalized <- normalizeSegmentedBins(copyNumbersSegmented)
copyNumbersCalled <- callBins(copyNumbersSegmentedNormalized, cellularity=.75)

##################################################################
## Make final data matrix

dat <- data.table( copyNumbersCalled@featureData@data )
dat[, readcount  := readCounts@assayData$counts]
dat[, copynumber := copynumber(copyNumbersCalled)[,sampleName] ]
dat[, segmented  := segmented(copyNumbersCalled)[,sampleName] ]
dat[, call       := calls(copyNumbersCalled)[,sampleName] ]
dat[, probdloss  := probdloss(copyNumbersCalled)[,sampleName] ]
dat[, probloss   := probloss(copyNumbersCalled)[,sampleName] ]
dat[, probnorm   := probnorm(copyNumbersCalled)[,sampleName] ]
dat[, probgain   := probgain(copyNumbersCalled)[,sampleName] ]
dat[, probamp    := probamp(copyNumbersCalled)[,sampleName] ]
dat[, probdloss  := probdloss(copyNumbersCalled)[,sampleName] ]
dat[, probdloss  := probdloss(copyNumbersCalled)[,sampleName] ]

##################################################################
## Supress scientific notation in output files
options(scipen=999)

##################################################################
## Write to outfile, gzip if outfile end with gz.
cat("Writing outfile...\n")
ofile <- opts$output
if( grepl("gz$", opts$output) ){
  ofile <- gzfile( opts$output, 'w' )
}
write.table(dat, ofile, col.names=TRUE, dec=".", quote=FALSE, sep="\t", row.names=FALSE)
if( grepl("gz$", opts$output) ){
  close(ofile)
}

cat("Done.\n")
