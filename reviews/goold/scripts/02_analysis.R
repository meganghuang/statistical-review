# ==========================================================================
# goold review -- r cells, verbatim and in execution order
# conda env: goold-net
# 14 cells with exit_status='ok'; cells that errored are omitted.
# Run top-to-bottom in ONE session: the originals ran in a persistent
# kernel, so later cells depend on earlier state.
# ==========================================================================


# ------------------------ cell 10 ------------------------

r <- try(cor_auto(patrolDogs, forcePD=TRUE), silent=TRUE); cat("forcePD try:", class(r), "\n")
r2 <- try(cor_auto(patrolDogs, ordinalLevelMax=7, missing="pairwise"), silent=TRUE); cat("pairwise try:", class(r2), "\n")
suppressPackageStartupMessages(library(psych))
pp <- psych::polychoric(as.matrix(patrolDogs))$rho
cat("psych polychoric ok; min eig:", min(eigen(pp, only.values=TRUE)$values), "\n")
pubP <- as.matrix(read.csv("goold/data/PatrolDog_GGM_AssociationMatrix.csv", row.names=1))[nodes,nodes]
ep <- EBICglasso(pp, n=116, gamma=0.65)
ut <- upper.tri(pubP)
cat("psych-polychoric edges:", sum(ep[ut]!=0), " published:", sum(pubP[ut]!=0),
    " agree:", sum((ep[ut]!=0)==(pubP[ut]!=0)), "/190\n")
cat("max|dw|:", round(max(abs(ep[ut]-pubP[ut])),4), " cor of weights:", round(cor(ep[ut],pubP[ut]),4), "\n")


# ------------------------ cell 11 ------------------------

patrolData <- cor_auto(patrolDogs, forcePD=TRUE, verbose=FALSE)
dd <- try(cor_auto(detectDogs, forcePD=TRUE, verbose=FALSE), silent=TRUE)
cat("detect forcePD:", class(dd), if(inherits(dd,"try-error")) as.character(dd) else "", "\n")
if (inherits(dd,"try-error")) {
  dd <- try(cor_auto(detectDogs, forcePD=TRUE, missing="pairwise", verbose=FALSE), silent=TRUE)
  cat("detect pairwise:", class(dd), "\n")
}
pubP <- as.matrix(read.csv("goold/data/PatrolDog_GGM_AssociationMatrix.csv", row.names=1))[nodes,nodes]
pubD <- as.matrix(read.csv("goold/data/DetectionDog_GGM_AssociationMatrix.csv", row.names=1))[nodes,nodes]
ut <- upper.tri(pubP)
EBICpatrol <- EBICglasso(patrolData, n=116, gamma=0.65)
cat(sprintf("PATROL  repro edges=%d published=%d  agree=%d/190  max|dw|=%.4f  r=%.4f\n",
   sum(EBICpatrol[ut]!=0), sum(pubP[ut]!=0), sum((EBICpatrol[ut]!=0)==(pubP[ut]!=0)),
   max(abs(EBICpatrol[ut]-pubP[ut])), cor(EBICpatrol[ut],pubP[ut])))
if (!inherits(dd,"try-error")) {
  detectData <- dd
  EBICdetect <- EBICglasso(detectData, n=54, gamma=0.65)
  cat(sprintf("DETECT  repro edges=%d published=%d  agree=%d/190  max|dw|=%.4f  r=%.4f\n",
   sum(EBICdetect[ut]!=0), sum(pubD[ut]!=0), sum((EBICdetect[ut]!=0)==(pubD[ut]!=0)),
   max(abs(EBICdetect[ut]-pubD[ut])), cor(EBICdetect[ut],pubD[ut])))
  cat("CUR-SOC polychoric P/D:", round(patrolData["CUR","SOC"],3), round(detectData["CUR","SOC"],3),
      "| GGM edge P/D:", EBICpatrol["CUR","SOC"], EBICdetect["CUR","SOC"], "\n")
}


# ------------------------ cell 12 ------------------------

cent <- function(W){ q <- qgraph(W, DoNotPlot=TRUE); ct <- centrality(q)
  data.frame(node=colnames(W), betweenness=ct$Betweenness, strength=ct$InDegree) }
cp <- cent(EBICpatrol); cd <- cent(EBICdetect)
tabS4 <- data.frame(node=cp$node, Pb=cp$betweenness, Db=cd$betweenness,
                    Ps=round(cp$strength,3), Ds=round(cd$strength,3))
print(tabS4, row.names=FALSE)
t0 <- Sys.time()
for(i in 1:5){ idx <- sample(nrow(patrolDogs), replace=TRUE)
  invisible(EBICglasso(cor_auto(patrolDogs[idx,], forcePD=TRUE, verbose=FALSE), n=116, gamma=0.65)) }
cat("sec per patrol network:", as.numeric(difftime(Sys.time(),t0,units="secs"))/5, "\n")


# ------------------------ cell 23 ------------------------

source("bg_analysis.R", echo=FALSE)


# ------------------------ cell 27 ------------------------

res <- readRDS("reanalysis.rds"); nodes <- res$obs$nodes
suppressPackageStartupMessages(library(effsize))
cd <- function(x,y){ ys<-sort(y); n2<-length(y)
  lt<-findInterval(x,ys,left.open=TRUE); le<-findInterval(x,ys)
  (sum(lt)-sum(n2-le))/(length(x)*n2) }
z <- function(M) t(scale(t(M)))   # standardise within each bootstrap network, across 20 nodes
nB <- min(nrow(res$bootP$betw), nrow(res$bootD$betw))
P <- lapply(res$bootP[c("betw","str")], function(m) m[1:nB,]); D <- lapply(res$bootD[c("betw","str")], function(m) m[1:nB,])
raw  <- sapply(seq_along(nodes), function(i) mean(c(cd(P$betw[,i],D$betw[,i]), cd(P$str[,i],D$str[,i]))))
Pz <- lapply(P, z); Dz <- lapply(D, z)
std  <- sapply(seq_along(nodes), function(i) mean(c(cd(Pz$betw[,i],Dz$betw[,i]), cd(Pz$str[,i],Dz$str[,i]))))
pub <- c(ACT=.282,ADP=.211,CUR=.452,DA=-.609,FDA=-.302,FIT=.136,FL=.050,FoH=.130,FSH=-.614,
  GUS=-.582,GWL=-.310,PLA=.151,PS=-.092,PSV=-.049,REC=-.063,SLP=.290,SOC=.092,STR=-.089,TOY=-.465,WIL=.019)[nodes]
cmp <- data.frame(node=nodes, published=as.numeric(pub), raw=round(raw,3), standardized=round(std,3))
print(cmp, row.names=FALSE)
cat(sprintf("\nraw: r=%.3f max|d|=%.3f | standardized: r=%.3f max|d|=%.3f\n",
  cor(raw,pub), max(abs(raw-pub)), cor(std,pub), max(abs(std-pub))))


# ------------------------ cell 29 ------------------------

cat(sprintf("edge count: patrol obs=%d bootMean=%.1f bootSD=%.2f (published SD 12.82) | detection obs=%d bootMean=%.1f bootSD=%.2f (published SD 29.75)\n",
  res$obs$edgesP, mean(res$bootP$edges), sd(res$bootP$edges),
  res$obs$edgesD, mean(res$bootD$edges), sd(res$bootD$edges)))
dg <- data.frame(node=nodes, obsPb=res$obs$betwP, bPb=round(colMeans(res$bootP$betw),1),
                 obsDb=res$obs$betwD, bDb=round(colMeans(res$bootD$betw),1),
                 obsPs=round(res$obs$strP,2), bPs=round(colMeans(res$bootP$str),2),
                 obsDs=round(res$obs$strD,2), bDs=round(colMeans(res$bootD$str),2))
print(dg, row.names=FALSE)
cat("\nquantiles of bootstrap edge counts patrol:", quantile(res$bootP$edges, c(.025,.5,.975)),
    "| detection:", quantile(res$bootD$edges, c(.025,.5,.975)), "\n")


# ------------------------ cell 31 ------------------------

diag1 <- t(sapply(1:25, function(k){
  set.seed(k); idx <- sample(116, replace=TRUE); d <- patrolDogs[idx,]
  Craw <- try(cor_auto(d, verbose=FALSE), silent=TRUE)          # no forcePD
  Cpd  <- cor_auto(d, forcePD=TRUE, verbose=FALSE)
  pdOK <- !inherits(Craw,"try-error") && min(eigen(Craw,only.values=TRUE)$values) > 0
  e_pd <- {W<-EBICglasso(Cpd,n=116,gamma=0.65); sum(W[upper.tri(W)]!=0)}
  e_raw <- if (pdOK) {W<-try(EBICglasso(Craw,n=116,gamma=0.65),silent=TRUE)
                      if(inherits(W,"try-error")) NA else sum(W[upper.tri(W)]!=0)} else NA
  c(pdOK=pdOK, maxabs=max(abs(Cpd[upper.tri(Cpd)])), edges_forcePD=e_pd, edges_raw=e_raw)
}))
print(round(diag1,3))
cat("\nfraction of resamples whose raw polychoric is PD:", mean(diag1[,"pdOK"]), "\n")
cat("mean edges forcePD:", mean(diag1[,"edges_forcePD"]), " mean edges raw(PD only):", mean(diag1[,"edges_raw"],na.rm=TRUE), "\n")


# ------------------------ cell 34 ------------------------

source("bg_sub.R", echo=FALSE)


# ------------------------ cell 36 ------------------------

source("bg_perm2.R", echo=FALSE)


# ------------------------ cell 37 ------------------------

suppressPackageStartupMessages({library(jsonlite); library(effsize)})
p2 <- readRDS("perm2.rds"); sb <- readRDS("subsample.rds"); res <- readRDS("reanalysis.rds")
nodes <- p2$nodes; ut <- upper.tri(matrix(0,20,20))
pairnm <- outer(nodes,nodes,paste,sep="-")[ut]

## (A) omnibus: sum of squared polychoric differences
obsSS <- sum(p2$obsDiff^2); nullSS <- rowSums(p2$Dnull^2)
pSS <- (1+sum(nullSS>=obsSS))/(1+length(nullSS))
cat(sprintf("OMNIBUS structure test: SS_obs=%.3f  null median=%.3f  null 95th=%.3f  p=%.4f (resolution 1/%d)\n",
  obsSS, median(nullSS), quantile(nullSS,.95), pSS, length(nullSS)+1))
## per-pair, max-statistic FWER
mx <- apply(abs(p2$Dnull),1,max)
pPair <- sapply(seq_along(p2$obsDiff), function(j) (1+sum(abs(p2$Dnull[,j])>=abs(p2$obsDiff[j])))/(1+nrow(p2$Dnull)))
pFWER <- sapply(seq_along(p2$obsDiff), function(j) (1+sum(mx>=abs(p2$obsDiff[j])))/(1+length(mx)))
qBH <- p.adjust(pPair,"BH")
cat(sprintf("per-pair tests: raw p<.05 = %d/190 | BH q<.05 = %d | max-stat FWER<.05 = %d\n",
  sum(pPair<.05), sum(qBH<.05), sum(pFWER<.05)))
top <- order(pPair)[1:8]
print(data.frame(pair=pairnm[top], diff=round(p2$obsDiff[top],3), p=round(pPair[top],4),
                 qBH=round(qBH[top],3), pFWER=round(pFWER[top],3)), row.names=FALSE)

## (B) EBICglasso edge counts under label permutation
EB <- p2$EB
cat(sprintf("\nLabel-permutation networks: patrol-sized (n~%.0f) edges median=%.0f IQR=%.0f-%.0f, empty in %d/%d;\n  detection-sized (n~%.0f) edges median=%.0f, EMPTY in %d/%d (%.0f%%)\n",
  mean(EB[,"nP"]), median(EB[,"eP"],na.rm=TRUE), quantile(EB[,"eP"],.25,na.rm=TRUE), quantile(EB[,"eP"],.75,na.rm=TRUE),
  sum(EB[,"eP"]==0,na.rm=TRUE), nrow(EB), mean(EB[,"nD"]), median(EB[,"eD"],na.rm=TRUE),
  sum(EB[,"eD"]==0,na.rm=TRUE), nrow(EB), 100*mean(EB[,"eD"]==0,na.rm=TRUE)))
cat(sprintf("  observed edges: patrol 55 (perm p=%.3f two-sided on edge count), detection 70 (perm p=%.4f one-sided for >=70)\n",
  (1+sum(abs(EB[,"eP"]-median(EB[,"eP"],na.rm=TRUE))>=abs(55-median…[+2701 chars]


# ------------------------ cell 39 ------------------------

source("bg_matched.R", echo=FALSE)


# ------------------------ cell 40 ------------------------

suppressPackageStartupMessages(library(jsonlite))
m <- readRDS("matched54.rds"); nodes <- m$nodes
obsD_edges <- 70
cat(sprintf("patrol networks at matched n=54: edges median=%.0f  IQR=%.0f-%.0f  empty in %d/%d (%.0f%%)  max=%.0f\n",
  median(m$edges), quantile(m$edges,.25), quantile(m$edges,.75), sum(m$edges==0), m$nok,
  100*mean(m$edges==0), max(m$edges)))
cat(sprintf("detection observed 70 edges: P(patrol-at-54 >= 70) = %.4f\n", (1+sum(m$edges>=70))/(1+m$nok)))
nz <- m$edges>0
cat(sprintf("among the %d non-empty matched-n patrol networks: edges median=%.0f IQR=%.0f-%.0f\n",
  sum(nz), median(m$edges[nz]), quantile(m$edges[nz],.25), quantile(m$edges[nz],.75)))
res <- readRDS("reanalysis.rds")
obsBD <- res$obs$betwD; obsSD <- res$obs$strD
tab <- data.frame(node=nodes, detBetw=obsBD, detStr=round(obsSD,3),
  p_betw=sapply(seq_along(nodes), function(i) (1+sum(m$betw[,i]>=obsBD[i]))/(1+m$nok)),
  p_str =sapply(seq_along(nodes), function(i) (1+sum(m$str[,i] >=obsSD[i]))/(1+m$nok)))
tab$q_betw <- p.adjust(tab$p_betw,"BH"); tab$q_str <- p.adjust(tab$p_str,"BH")
print(tab, row.names=FALSE, digits=3)
cat(sprintf("\nmatched-n: detection centrality exceeds patrol-at-54 reference at raw p<.05 -> betw %d/20, str %d/20; BH q<.05 -> %d, %d\n",
  sum(tab$p_betw<.05), sum(tab$p_str<.05), sum(tab$q_betw<.05), sum(tab$q_str<.05)))
sb <- readRDS("subsample.rds")
cat(sprintf("\nedge-count SD under 80%% subsampling: patrol %.2f, detection %.2f (published with-replacement bootstrap: 12.82, 29.75)\n",
  sd(sb$subP$edges), sd(sb$subD$edges)))
cat(sprintf("handler-cluster 80%% subsampling: patrol SD %.2f, detection SD %.2f\n", sd(sb$clkP$edges), sd(sb$clkD$edges)))
j <- fromJSON("handoff/goold_stats.json")
j$matched <- list(edges=m$edges, p_betw=tab$p_betw, p_str=tab$p_str, q_betw=tab$q_betw, q_str=tab$q_str,
                  detBetw=obsBD, detStr=obsSD, nok=m$nok,
                  mBetw=m$betw, mStr=m$str)
j$subSD <- c(P=sd(sb$subP$edges), D=sd(sb$subD$edges), kP=sd(sb$clkP$edges), kD=s…[+104 chars]


# ------------------------ cell 41 ------------------------

suppressPackageStartupMessages({library(qgraph); library(parallel); library(jsonlite)})
net <- read.csv("goold/data/finalMIdata_averaged_rounded.csv")
nodes <- c("SLP","PS","PSV","FL","CUR","PLA","FIT","SOC","DA","GWL","REC","ACT","ADP","STR","FSH","GUS","FDA","TOY","FoH","WIL")
allD <- net[,nodes]; hid <- net$id
htyp <- tapply(net$workType, net$id, function(x) as.numeric(names(which.max(table(x)))))
ut <- upper.tri(matrix(0,20,20))
pc <- function(df) cor_auto(df, forcePD=TRUE, verbose=FALSE)
oP <- pc(allD[net$workType==1,])[ut]; oD <- pc(allD[net$workType==0,])[ut]
obsStat <- mean(abs(oD)) - mean(abs(oP))
cat(sprintf("mean |polychoric r|: patrol %.4f (n=116), detection %.4f (n=54), difference %+.4f\n",
            mean(abs(oP)), mean(abs(oD)), obsStat))
cl<-makeCluster(12); clusterEvalQ(cl, suppressPackageStartupMessages(library(qgraph)))
clusterExport(cl,c("allD","hid","htyp","pc","ut"))
f <- function(s){ set.seed(9000+s); ht<-htyp; ht[]<-sample(ht); lab<-ht[as.character(hid)]
  a<-try(pc(allD[lab==1,]),silent=TRUE); b<-try(pc(allD[lab==0,]),silent=TRUE)
  if(inherits(a,"try-error")||inherits(b,"try-error")) return(NA)
  mean(abs(b[ut]))-mean(abs(a[ut])) }
clusterExport(cl,"f"); nullStat <- unlist(parLapply(cl,1:2000,f)); stopCluster(cl)
nullStat <- nullStat[!is.na(nullStat)]
p2s <- (1+sum(abs(nullStat)>=abs(obsStat)))/(1+length(nullStat))
cat(sprintf("permutation (handler-level, %d perms): null mean %+.4f sd %.4f ; two-sided p = %.4f (resolution 1/%d)\n",
  length(nullStat), mean(nullStat), sd(nullStat), p2s, length(nullStat)+1))
j <- fromJSON("handoff/goold_stats.json")
j$strength <- list(obsStat=obsStat, nullStat=nullStat, p=p2s,
                   meanAbsP=mean(abs(oP)), meanAbsD=mean(abs(oD)), rP=oP, rD=oD)
write_json(j, "handoff/goold_stats.json", digits=8, auto_unbox=TRUE); cat("written\n")


# ------------------------ cell 43 ------------------------

suppressPackageStartupMessages(library(jsonlite))
sb <- readRDS("subsample.rds"); j <- fromJSON("handoff/goold_stats.json")
j$clkStrP <- sb$clkP$str; j$clkBetwP <- sb$clkP$betw
write_json(j, "handoff/goold_stats.json", digits=8, auto_unbox=TRUE)
cat("dims:", dim(sb$clkP$str), dim(sb$subP$str), "\n")
