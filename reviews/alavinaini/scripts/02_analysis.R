# ==========================================================================
# alavinaini review -- r cells, verbatim and in execution order
# conda env: r
# 11 cells with exit_status='ok'; cells that errored are omitted.
# Run top-to-bottom in ONE session: the originals ran in a persistent
# kernel, so later cells depend on earlier state.
# ==========================================================================


# ------------------------ cell 15 ------------------------

ok <- c(overlap=requireNamespace("overlap",quietly=TRUE), suntools=requireNamespace("suntools",quietly=TRUE)); print(ok)


# ------------------------ cell 16 ------------------------

dir.create("rlib", showWarnings=FALSE)
r <- try(install.packages("overlap", lib="rlib", repos="https://cloud.r-project.org", type="source"), silent=TRUE)
cat("exists:", requireNamespace("overlap", lib.loc="rlib", quietly=TRUE), "\n")
cat(list.files("rlib"), "\n")


# ------------------------ cell 17 ------------------------

for (i in 1:3) {
  try(install.packages("overlap", lib="rlib", repos="https://cloud.r-project.org",
                       dependencies=FALSE, type="source", quiet=TRUE), silent=TRUE)
  if (requireNamespace("overlap", lib.loc="rlib", quietly=TRUE)) break
}
cat("overlap available:", requireNamespace("overlap", lib.loc="rlib", quietly=TRUE), "\n")


# ------------------------ cell 19 ------------------------

install.packages("overlap_0.3.9.tar.gz", lib="rlib", repos=NULL, type="source", quiet=TRUE)
cat("overlap:", requireNamespace("overlap", lib.loc="rlib", quietly=TRUE), "\n")


# ------------------------ cell 20 ------------------------

o <- capture.output(install.packages("overlap_0.3.9.tar.gz", lib=normalizePath("rlib"), repos=NULL, type="source"), type="message")
cat(tail(o,25), sep="\n")
cat("\nlib contents:", list.files("rlib"), "\n")


# ------------------------ cell 21 ------------------------

untar("overlap_0.3.9.tar.gz", exdir="ovsrc")
fs <- list.files("ovsrc/overlap/R", full.names=TRUE); cat(basename(fs), "\n")
for (f in fs) try(source(f), silent=TRUE)
cat("overlapEst:", exists("overlapEst"), " bootstrap:", exists("bootstrap"), " bootCI:", exists("bootCI"),
    " densityFit:", exists("densityFit"), " getBandWidth:", exists("getBandWidth"), "\n")


# ------------------------ cell 22 ------------------------

suppressPackageStartupMessages({library(lubridate);library(dplyr);library(readr)})
b <- read_csv("bundle/data/Bobcat_Data.csv", col_types=cols(.default=col_character())) %>% mutate(sg="bobcat")
c2<- read_csv("bundle/data/Domestic_Cat_Data.csv", col_types=cols(.default=col_character())) %>% mutate(sg="domestic_cat")
a <- bind_rows(b,c2) %>% rename(ts=`Timestamp (UTC)`, site=SiteAbbr) %>%
  mutate(ts=ymd_hms(ts,tz="UTC"), tl=with_tz(ts,"America/Chicago"),
         hd=hour(tl)+minute(tl)/60+second(tl)/3600, clock_rad=hd*2*pi/24)
st <- try(sunTime(a$clock_rad, a$tl, cbind(rep(-95.359704,nrow(a)), rep(29.760890,nrow(a)))), silent=TRUE)
cat("sunTime ok:", !inherits(st,"try-error"), "\n"); if(inherits(st,"try-error")) cat(as.character(st),"\n")


# ------------------------ cell 25 ------------------------

cat(readLines("ovsrc/overlap/R/densityFit.R"), sep="\n")
cat("\n---- overlapEst ----\n"); cat(readLines("ovsrc/overlap/R/overlapEst.R"), sep="\n")


# ------------------------ cell 26 ------------------------

densityFit <- function(x, grid, bw) {
  sapply(grid, function(t) mean(exp(bw*cos(t - x)))) / (2*pi*besselI(bw, 0))
}
dt <- read.csv("handoff_times.csv")
g <- function(S,P) dt$suntime_rad[dt$site_cat==S & dt$species_group==P]
sb<-g("bobcat_solo","bobcat"); scat<-g("cat_solo","domestic_cat"); bb<-g("both","bobcat"); bc<-g("both","domestic_cat")
cat(sprintf("n: %d %d %d %d\n",length(sb),length(scat),length(bb),length(bc)))
ds<-overlapEst(sb,scat,type="Dhat1"); db<-overlapEst(bb,bc,type="Dhat1")
cat(sprintf("Dhat1 solo=%.4f shared=%.4f   (paper: 0.852 / 0.646)\n",ds,db))
cat(sprintf("Dhat4 solo=%.4f shared=%.4f\n",overlapEst(sb,scat,type="Dhat4"),overlapEst(bb,bc,type="Dhat4")))


# ------------------------ cell 28 ------------------------

resamp <- function(x, n){ bw<-getBandWidth(x,kmax=3); (sample(x,n,TRUE) + rvm(n,bw)) %% (2*pi) }
rvm <- function(n,k){ # von Mises deviates, Best & Fisher
  a<-1+sqrt(1+4*k^2); b<-(a-sqrt(2*a))/(2*k); r<-(1+b^2)/(2*b); out<-numeric(n); i<-0
  while(i<n){ u1<-runif(1); z<-cos(pi*u1); f<-(1+r*z)/(r+z); c<-k*(r-f); u2<-runif(1)
    if(c*(2-c)-u2>0 || log(c/u2)+1-c>=0){ i<-i+1; out[i]<-sign(runif(1)-0.5)*acos(f) } }
  out }
bootD <- function(A,B,nb){ na<-length(A); nb2<-length(B)
  vapply(1:nb, function(i) overlapEst(resamp(A,na), resamp(B,nb2), type="Dhat1"), 0) }
set.seed(123)
Bs<-bootD(sb,scat,2000); Bb<-bootD(bb,bc,2000)
pci<-function(x) quantile(x,c(.025,.975))
basic<-function(est,x) c(2*est-quantile(x,.975), 2*est-quantile(x,.025))
cat(sprintf("smoothed bootstrap (2000) Dhat1 solo  = %.3f  perc95 [%.3f,%.3f]  basic95 [%.3f,%.3f]\n",ds,pci(Bs)[1],pci(Bs)[2],basic(ds,Bs)[1],basic(ds,Bs)[2]))
cat(sprintf("smoothed bootstrap (2000) Dhat1 shared= %.3f  perc95 [%.3f,%.3f]  basic95 [%.3f,%.3f]\n",db,pci(Bb)[1],pci(Bb)[2],basic(db,Bb)[1],basic(db,Bb)[2]))
dd<-Bs-Bb; obsd<-ds-db
cat(sprintf("DIFFERENCE solo-shared = %.3f  perc95 [%.3f,%.3f]  basic95 [%.3f,%.3f]  P(boot<=0)=%.4f\n",
  obsd,pci(dd)[1],pci(dd)[2],2*obsd-quantile(dd,.975),2*obsd-quantile(dd,.025),mean(dd<=0)))
write.csv(data.frame(det_solo=Bs,det_shared=Bb),"handoff_boot_det.csv",row.names=FALSE)


# ------------------------ cell 29 ------------------------

sboot <- function(nb=2000){
  shd<-dt[dt$site_cat=="both",]; s3<-unique(shd$site)
  bs<-dt[dt$site_cat=="bobcat_solo",]; s1<-unique(bs$site)
  cs<-dt[dt$site_cat=="cat_solo",];  s2<-unique(cs$site)
  oS<-rep(NA,nb); oH<-rep(NA,nb)
  for(i in 1:nb){
    A<-unlist(lapply(sample(s1,length(s1),TRUE),function(s) bs$suntime_rad[bs$site==s]))
    B<-unlist(lapply(sample(s2,length(s2),TRUE),function(s) cs$suntime_rad[cs$site==s]))
    if(length(A)>=8 && length(B)>=8) oS[i]<-try(overlapEst(A,B,type="Dhat1"),silent=TRUE)[1]
    ss<-sample(s3,length(s3),TRUE)
    C<-unlist(lapply(ss,function(s) shd$suntime_rad[shd$site==s & shd$species_group=="bobcat"]))
    D<-unlist(lapply(ss,function(s) shd$suntime_rad[shd$site==s & shd$species_group=="domestic_cat"]))
    if(length(C)>=8 && length(D)>=8) oH[i]<-try(overlapEst(C,D,type="Dhat1"),silent=TRUE)[1]
  }
  data.frame(solo=as.numeric(oS), shared=as.numeric(oH)) }
set.seed(7); sb2<-sboot(2000)
cs_<-sb2$solo[!is.na(sb2$solo)]; ch_<-sb2$shared[!is.na(sb2$shared)]
cat(sprintf("site-cluster bootstrap: solo   %.3f  95%% [%.3f, %.3f]  (%d/%d reps valid)\n",ds,quantile(cs_,.025),quantile(cs_,.975),length(cs_),2000))
cat(sprintf("site-cluster bootstrap: shared %.3f  95%% [%.3f, %.3f]  (%d/%d reps valid)\n",db,quantile(ch_,.025),quantile(ch_,.975),length(ch_),2000))
k<-min(length(cs_),length(ch_)); ddc<-cs_[1:k]-ch_[1:k]
cat(sprintf("site-cluster DIFFERENCE %.3f  95%% [%.3f, %.3f]  P(<=0)=%.3f\n",ds-db,quantile(ddc,.025),quantile(ddc,.975),mean(ddc<=0)))
write.csv(data.frame(site_solo=cs_[1:k],site_shared=ch_[1:k]),"handoff_boot_site.csv",row.names=FALSE)
