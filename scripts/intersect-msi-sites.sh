#!/usr/bin/env bash

MSISITES=$1
TARGETS=$2
OUTPUT=$3

#create temp files
sitesheader=$(mktemp /tmp/msisensor-header.XXXXXX)
sitesbed=$(mktemp /tmp/msisensor-bed.XXXXXX)
sitestargetbed=$(mktemp /tmp/msisensor-bed-intarget.XXXXXX)

head $MSISITES | head -n 1 > $sitesheader
awk '{if(NR>1){print}}' $MSISITES | awk 'BEGIN { FS="\t"; OFS="\t" } { $2=$2 "\t" ($2+($3*$5)) } 1' > $sitesbed
bedtools intersect -wa -a $sitesbed -b $TARGETS > $sitestargetbed

# $3 is repeat unit size (1 == homopolymers)
# $5 is number of repeats (>8 means homopolymers of 9 bases or more)
cat $sitesheader <(cut -f 1,2,4- $sitestargetbed | awk '{if($5>8){print}}') > $OUTPUT

rm $sitesheader
rm $sitesbed
rm $sitestargetbed
