#!/usr/bin/env Rscript

###########################################
# check command line
library(getopt)

#long, short, argmask, datatype, desk
#argmask 0=no arg, 1=req, 2=optional
args <- rbind(c("input", "i", 1, "character", "segment file from qdnaseq.R"),
              c("output", "o", 1, "character", "output jpg file"),
              c("chrsizes", "c", 1, "character", "chromosome sizes file"))

# opts <- getopt(args,opt = c("--input", "/home/daniel.klevebring/Crisp/clinseq/BREASTv7//K32568/K32568T/wgs/K32568T_wgs.qdnaseq.txt",
#                            "--output", "~/projects/plot.jpg",
#                            "--chrsizes", "/proj/b2010040/private/nobackup/autoseqer-genome/genome/human_g1k_v37_decoy.chrsizes.txt") )

opts <- getopt(args)
if(is.null(opts$input)){
  stop("Must specify input segments file --input/-i.")
}
if(is.null(opts$output)){
  stop("Must specify output jpg file name --output/-o.")
}
if(is.null(opts$chrsizes)){
  stop("Must specify chrsizes file --chrsizes/-c.")
}

##############################
# setup
library(data.table)
library(ggplot2)
library(clinseqr)

chrsizes <- fread(opts$chrsizes)
setnames(chrsizes, names(chrsizes), c("chr", "size"))
chrsizes$cumend <- cumsum( as.numeric( chrsizes$size) )
chrsizes$cumstart <- as.numeric(chrsizes$cumend) - as.numeric(chrsizes$size) 
chrsizes$labelpos <- cumsum( as.numeric(chrsizes$size)) - chrsizes$size/2

pten <- list(chr=10, start=89623195, end=89728532)
igf2 <- list(chr=11, start=2150342, end=2162341)
pten$cumstart <- pten$start + chrsizes$cumstart[which(chrsizes$chr==pten$chr)]
pten$cumend <- pten$end + chrsizes$cumstart[which(chrsizes$chr==pten$chr)]
igf2$cumstart <- igf2$start + chrsizes$cumstart[which(chrsizes$chr==igf2$chr)]
igf2$cumend <- igf2$end + chrsizes$cumstart[which(chrsizes$chr==igf2$chr)]

segments <- fread(opts$input)

segments$cumstart <- NA
segments$cumend   <- NA
for(chr in chrsizes$chr){ ## chr = chrsizes$chr[1]
  idx <- which( segments$chr == chr )
  cumchrsize <- chrsizes$cumend[which(chrsizes$chr == chr)] - 
    chrsizes$size[which(chrsizes$chr == chr)]
  segments$cumstart[idx] <- segments$start[idx] + cumchrsize
  segments$cumend[idx] <- segments$end[idx] + cumchrsize
}
segments$centerpos <- segments$cumstart+(segments$cumend-segments$cumstart)/2

col_scale  <- scale_color_manual(values=c('dodgerblue1','dodgerblue4', "forestgreen", 
                                          "firebrick4", "firebrick1"), 
                                 breaks=factor(-2:2, levels=-2:2),
                                 labels=c("HOMDEL", "HETDEL", "NORMAL", "GAIN", "AMP"), 
                                 drop=FALSE, name="")

yvar <- ( (1:nrow(chrsizes)) %% 2 ) / 6
p <- ggplot(segments, aes(x=centerpos, y=log2(copynumber))) + geom_point(alpha=.5) + 
  geom_point(aes(x=centerpos, y=log2(segmented), colour=factor(call, levels=-2:2))) + 
  col_scale + ylab("log2(CN Ratio)") + xlab("Chr") + theme_bw() + 
  geom_vline(xintercept=pten$cumstart, colour="hotpink") + 
  geom_vline(xintercept=igf2$cumstart, colour="gold") + 
  geom_vline(xintercept=0, linetype="dotted", colour="gray50") + 
  geom_vline(xintercept=chrsizes$cumend, linetype="dotted", colour="gray50") + 
  annotate("text", x=as.numeric(chrsizes$labelpos), y=-1.3+yvar, 
           label=chrsizes$chr, size=4, colour="gray50") + 
  theme(axis.text.x=element_blank(),axis.ticks.x=element_blank(), panel.grid=element_blank()) + 
  ggtitle("Copy Number Profile")


p.pten <- ggplot(segments, aes(x=centerpos, y=log2(copynumber))) + geom_point(alpha=.5) + 
  xlim(pten$cumstart-1.5e6, pten$cumend+1.5e6 ) + 
  geom_point(aes(x=centerpos, y=log2(segmented), colour=factor(call, levels=-2:2))) + 
  col_scale + ylab("log2(CN Ratio)") + xlab("Chr") + theme_bw() + 
  geom_vline(xintercept=pten$cumstart, colour="hotpink") + 
  geom_vline(xintercept=pten$cumend, colour="hotpink") + 
  geom_vline(xintercept=0, linetype="dotted", colour="gray50") + 
  geom_vline(xintercept=chrsizes$cumend, linetype="dotted", colour="gray50") + 
  theme(axis.text.x=element_blank(),axis.ticks.x=element_blank(), panel.grid=element_blank()) + 
  ggtitle("PTEN")

p.igf2 <- ggplot(segments, aes(x=centerpos, y=log2(copynumber))) + geom_point(alpha=.5) + 
  xlim(igf2$cumstart-1.5e6, igf2$cumend+1.5e6 ) + 
  geom_point(aes(x=centerpos, y=log2(segmented), colour=factor(call, levels=-2:2))) + 
  col_scale + ylab("log2(CN Ratio)") + xlab("Chr") + theme_bw() + 
  geom_vline(xintercept=igf2$cumstart, colour="gold") + 
  geom_vline(xintercept=igf2$cumend, colour="gold") + 
  geom_vline(xintercept=0, linetype="dotted", colour="gray50") + 
  geom_vline(xintercept=chrsizes$cumend, linetype="dotted", colour="gray50") + 
  theme(axis.text.x=element_blank(),axis.ticks.x=element_blank(), panel.grid=element_blank()) + 
  ggtitle("IGF2")


jpeg(opts$output, width=2500, height=1000, quality = 100)
  multiplot(p, p.pten, p.igf2, layout=matrix(c(1,1,2,3), nc=2, byrow=TRUE))
dev.off()
