# ==========================================================================
# alavinaini review -- python cells, verbatim and in execution order
# conda env: python
# 21 cells with exit_status='ok'; cells that errored are omitted.
# Run top-to-bottom in ONE session: the originals ran in a persistent
# kernel, so later cells depend on earlier state.
# ==========================================================================


# ------------------------ cell 2 ------------------------

import pandas as pd, numpy as np
bob = pd.read_csv("bundle/data/Bobcat_Data.csv", dtype=str)
cat = pd.read_csv("bundle/data/Domestic_Cat_Data.csv", dtype=str)
print(list(bob.columns))
print(bob.shape, cat.shape)
print(bob.head(2).to_string())


# ------------------------ cell 3 ------------------------

for d,s in ((bob,'bobcat'),(cat,'domestic_cat')):
    d['species_group']=s
d = pd.concat([bob,cat],ignore_index=True)
d['ts_utc']=pd.to_datetime(d['Timestamp (UTC)'],format='ISO8601',utc=True)
d['ts_loc']=d['ts_utc'].dt.tz_convert('America/Chicago')
d['site']=d['SiteAbbr'].str.strip()

sites=d.groupby('site')['species_group'].agg(lambda x:set(x))
cls={}
for s,v in sites.items():
    cls[s]='both' if len(v)==2 else ('bobcat_solo' if 'bobcat' in v else 'cat_solo')
d['site_cat']=d['site'].map(cls)
print("n sites:",len(cls), pd.Series(cls).value_counts().to_dict())
print(pd.crosstab(d['site_cat'],d['species_group']))

# detections per site within each analysis group
for sc,sp in [('bobcat_solo','bobcat'),('cat_solo','domestic_cat'),('both','bobcat'),('both','domestic_cat')]:
    sub=d[(d.site_cat==sc)&(d.species_group==sp)]
    vc=sub.groupby('site').size().sort_values(ascending=False)
    print(f"{sc}/{sp}: n={len(sub)} sites={len(vc)} per-site={list(vc.values)}")


# ------------------------ cell 4 ------------------------

d=d.sort_values(['site','species_group','ts_utc']).reset_index(drop=True)
def filt(df, mins):
    keep=[]
    for (s,sp),g in df.groupby(['site','species_group'],sort=False):
        last=None
        for i,t in zip(g.index, g['ts_utc']):
            if last is None or (t-last).total_seconds()>=mins*60:
                keep.append(i); last=t
    return df.loc[sorted(keep)]

rows=[]
for m in [0,5,15,30,60]:
    f = d if m==0 else filt(d,m)
    r={'thresh_min':m}
    for sc,sp,lab in [('bobcat_solo','bobcat','bob_solo'),('cat_solo','domestic_cat','cat_solo'),
                      ('both','bobcat','bob_both'),('both','domestic_cat','cat_both')]:
        r[lab]=int(((f.site_cat==sc)&(f.species_group==sp)).sum())
    rows.append(r)
ev=pd.DataFrame(rows); print(ev.to_string(index=False))

# gap distribution within site+species
gaps=[]
for (s,sp),g in d.groupby(['site','species_group']):
    t=g['ts_utc'].sort_values().diff().dt.total_seconds().dropna()/60
    gaps+= list(t)
gaps=np.array(gaps)
print("\nconsecutive gaps (min) within site+species: n=%d"%len(gaps))
print("  <1min: %d (%.1f%%)  <5: %d  <15: %d  <30: %d (%.1f%%)  <60: %d"%(
    (gaps<1).sum(),100*(gaps<1).mean(),(gaps<5).sum(),(gaps<15).sum(),(gaps<30).sum(),100*(gaps<30).mean(),(gaps<60).sum()))
print("  median gap (h): %.2f"%(np.median(gaps)/60))


# ------------------------ cell 5 ------------------------

import re
mat=open("bundle/data/Watsons U2 and Polar Plot.m",encoding='utf-8',errors='replace').read()
def grab(name):
    m=re.search(re.escape(name)+r"\s*=\s*\[(.*?)\]",mat,re.S)
    return np.array([float(x) for x in m.group(1).split()])
arr={k:grab(k) for k in ['bobcat_both','cat_both','bobcat_only','cat_only']}
print({k:len(v) for k,v in arr.items()})

# CSV-derived local clock minutes
d['loc_min']=(d['ts_loc'].dt.hour*60+d['ts_loc'].dt.minute+d['ts_loc'].dt.second/60)
# note: README says Local Time Value uses fixed CST (UTC-6), no DST. Build that too:
d['cst_min']=((d['ts_utc'].dt.hour*60+d['ts_utc'].dt.minute+d['ts_utc'].dt.second/60)-360)%1440
sub=lambda sc,sp,col: d[(d.site_cat==sc)&(d.species_group==sp)][col].values
for lab,(sc,sp),key in [('bob_solo',('bobcat_solo','bobcat'),'bobcat_only'),
                        ('cat_solo',('cat_solo','domestic_cat'),'cat_only'),
                        ('bob_both',('both','bobcat'),'bobcat_both'),
                        ('cat_both',('both','domestic_cat'),'cat_both')]:
    a=np.sort(sub(sc,sp,'cst_min')); b=np.sort(arr[key])
    ok = len(a)==len(b) and np.allclose(a,b,atol=0.02)
    print(f"{lab}: n_csv={len(a)} n_matlab={len(b)} identical={ok} maxdiff={np.max(np.abs(a-b)) if len(a)==len(b) else 'NA'}")


# ------------------------ cell 6 ------------------------

def grab(name):
    m=re.search(r"(?<![A-Za-z_])"+re.escape(name)+r"\s*=\s*\[(.*?)\]",mat,re.S)
    return np.array([float(x) for x in m.group(1).split()])
arr={k:grab(k) for k in ['bobcat_both','cat_both','bobcat_only','cat_only']}
print({k:len(v) for k,v in arr.items()})
pairs=[('bob_solo',('bobcat_solo','bobcat'),'bobcat_only'),('cat_solo',('cat_solo','domestic_cat'),'cat_only'),
       ('bob_both',('both','bobcat'),'bobcat_both'),('cat_both',('both','domestic_cat'),'cat_both')]
for lab,(sc,sp),key in pairs:
    a=np.sort(sub(sc,sp,'cst_min')); b=np.sort(arr[key])
    print(f"{lab}: n_csv={len(a)} n_matlab={len(b)} identical={len(a)==len(b) and np.allclose(a,b,atol=0.02)}")

def watson_u2(a,b):
    n1,n2=len(a),len(b); N=n1+n2
    alld=np.concatenate([a,b]); grp=np.concatenate([np.ones(n1),2*np.ones(n2)])
    o=np.argsort(alld,kind='stable'); g=grp[o]
    F1=np.cumsum(g==1)/n1; F2=np.cumsum(g==2)/n2
    dk=F1-F2
    return (n1*n2/N**2)*(np.sum(dk**2)-np.sum(dk)**2/N)
def watson_p(u2,M=200):
    m=np.arange(1,M+1)
    return float(np.clip(2*np.sum((-1)**(m-1)*np.exp(-2*m**2*np.pi**2*u2)),0,1))

for lab,k1,k2 in [('solo (bobcat vs cat)','bobcat_only','cat_only'),('shared (bobcat vs cat)','bobcat_both','cat_both')]:
    u=watson_u2(arr[k1],arr[k2]); print(f"{lab}: U2={u:.4f} asym p={watson_p(u):.4f}  (n={len(arr[k1])},{len(arr[k2])})")
print("check: p at U2=0.187 ->",round(watson_p(0.187),4), " at 0.152 ->",round(watson_p(0.152),4))


# ------------------------ cell 7 ------------------------

rng=np.random.default_rng(1)
# --- the paper's untested headline contrast: cats at solo vs cats at shared sites
u_cat = watson_u2(arr['cat_only'],arr['cat_both']); 
u_bob = watson_u2(arr['bobcat_only'],arr['bobcat_both'])
print(f"UNTESTED cat solo vs cat shared : U2={u_cat:.4f} p={watson_p(u_cat):.4g} (n=696,99)")
print(f"UNTESTED bobcat solo vs shared  : U2={u_bob:.4f} p={watson_p(u_bob):.4g} (n=49,32)")

# --- shared-site structure: are bobcat- and cat-heavy sites the same?
sh=d[d.site_cat=='both']
print("\nshared-site detections by site:\n", pd.crosstab(sh['site'],sh['species_group']).to_string())

# --- 30-min independence filter, redo both reported tests (fixed-CST clock minutes)
f30=filt(d,30)
g=lambda df,sc,sp: df[(df.site_cat==sc)&(df.species_group==sp)]['cst_min'].values
for lab,(a,b) in {'solo':(g(f30,'bobcat_solo','bobcat'),g(f30,'cat_solo','domestic_cat')),
                  'shared':(g(f30,'both','bobcat'),g(f30,'both','domestic_cat'))}.items():
    u=watson_u2(a,b); print(f"\n30-min filtered {lab}: n={len(a)},{len(b)} U2={u:.4f} p={watson_p(u):.4f}")

# --- site-clustered permutation at shared sites (permute species label WITHIN site)
def perm_within_site(df, nperm=5000, col='cst_min'):
    sub=df[df.site_cat=='both'][['site','species_group',col]].copy()
    obs=watson_u2(sub[sub.species_group=='bobcat'][col].values, sub[sub.species_group=='domestic_cat'][col].values)
    lab=sub['species_group'].values.copy(); site=sub['site'].values; vals=sub[col].values
    idx={s:np.where(site==s)[0] for s in np.unique(site)}
    k=0
    for _ in range(nperm):
        L=lab.copy()
        for s,ii in idx.items(): L[ii]=rng.permutation(lab[ii])
        if watson_u2(vals[L=='bobcat'],vals[L=='domestic_cat'])>=obs: k+=1
    return obs,(k+1)/(nperm+1)
o,p=perm_within_site(d); print(f"\nshared sites, species labels permuted WITHIN site: U2={o:.4f} p={p:.4f} (5000 perms)")
o2,p2=perm_within_site(f30); print(f"  same, 30-min filtered: U2={o2:.4f} p={p2:.4f}")


# ------------------------ cell 9 ------------------------

for lo,hi,lab in [(18*60,6*60,'18:00-06:00'),(19*60,5*60,'19:00-05:00'),(20*60,6*60,'20:00-06:00'),(18*60,7*60,'18:00-07:00')]:
    night=lambda v: ((v>=lo)|(v<hi)).mean()*100
    print(f"{lab}: bob_solo={night(arr['bobcat_only']):.0f}% cat_solo={night(arr['cat_only']):.0f}% bob_both={night(arr['bobcat_both']):.0f}% cat_both={night(arr['cat_both']):.0f}%  (paper 67/85/-/51)")


# ------------------------ cell 10 ------------------------

from astral import LocationInfo
from astral.sun import sun
import datetime, functools
loc=LocationInfo("Houston","US","America/Chicago",29.760890,-95.359704)
@functools.lru_cache(maxsize=4000)
def srss(day):
    s=sun(loc.observer,date=day,tzinfo=loc.timezone)
    return s['sunrise'],s['sunset']
def is_night(ts):
    sr,ss=srss(ts.date())
    return (ts<sr) or (ts>ss)
d['night']=d['ts_loc'].apply(is_night)
tab=d.groupby(['site_cat','species_group'])['night'].agg(['mean','size'])
tab['pct_night']=(tab['mean']*100).round(1)
print("solar-night (true sunrise/sunset) percentages:\n",tab[['pct_night','size']].to_string())
print("paper: bobcat_solo 67, cat_solo 85, cat_both 51\n")

# 95% CI on nocturnal proportion: naive binomial vs site-cluster bootstrap
from scipy import stats
def cluster_boot_prop(df, nb=10000):
    sites=df['site'].unique(); out=[]
    for _ in range(nb):
        ss=rng.choice(sites,len(sites),replace=True)
        v=np.concatenate([df.loc[df.site==s,'night'].values for s in ss])
        out.append(v.mean())
    return np.percentile(out,[2.5,97.5])*100
print("%-14s %7s %6s  naive 95%%CI        site-cluster 95%%CI"%("group","n","%night"))
for sc,sp,lab in [('bobcat_solo','bobcat','bob_solo'),('cat_solo','domestic_cat','cat_solo'),
                  ('both','bobcat','bob_both'),('both','domestic_cat','cat_both')]:
    s=d[(d.site_cat==sc)&(d.species_group==sp)]
    k,n=s['night'].sum(),len(s)
    lo,hi=stats.binomtest(int(k),n).proportion_ci(0.95)
    cl,ch=cluster_boot_prop(s)
    print("%-14s %7d %6.1f  [%5.1f, %5.1f]      [%5.1f, %5.1f]"%(lab,n,100*k/n,100*lo,100*hi,cl,ch))


# ------------------------ cell 11 ------------------------

cats=d[d.species_group=='domestic_cat'].copy()
ps=cats.groupby(['site','site_cat']).agg(n=('night','size'),pn=('night','mean')).reset_index()
ps['pn']=100*ps['pn']
print("per-site nocturnal % for domestic cats:")
print(ps.sort_values(['site_cat','n'],ascending=[True,False]).to_string(index=False))

# site-level permutation: shuffle site_cat label across the 26 cat sites
grp=ps['site_cat'].values; nn=ps['n'].values; pn=ps['pn'].values
def stat(lbl):  # detection-weighted difference in % night (same quantity the paper quotes)
    a=lbl=='cat_solo'
    return np.average(pn[a],weights=nn[a])-np.average(pn[~a],weights=nn[~a])
obs=stat(grp)
k=sum(abs(stat(rng.permutation(grp)))>=abs(obs) for _ in range(20000))
print(f"\nsite-level permutation, cat %night solo vs shared: diff={obs:.1f} pct pts, p={(k+1)/20001:.4f} (19 vs 7 sites)")
# unweighted site-mean version
def stat2(lbl):
    a=lbl=='cat_solo'; return pn[a].mean()-pn[~a].mean()
o2=stat2(grp); k2=sum(abs(stat2(rng.permutation(grp)))>=abs(o2) for _ in range(20000))
print(f"  site as unit (unweighted means): diff={o2:.1f} pct pts, p={(k2+1)/20001:.4f}")

# naive test the paper did NOT do, for contrast
ct=pd.crosstab(cats['site_cat'],cats['night'])
chi=stats.chi2_contingency(ct.values)
print(f"  naive detection-level chi-square (pseudoreplicated): p={chi.pvalue:.3g}")

# site-level permutation of Watson U2, cat solo vs shared
cm=cats['cst_min'].values; csite=cats['site'].values
sm={s:cm[csite==s] for s in ps['site']}
def u2_from(lbl):
    A=np.concatenate([sm[s] for s,l in zip(ps['site'],lbl) if l=='cat_solo'])
    B=np.concatenate([sm[s] for s,l in zip(ps['site'],lbl) if l=='both'])
    return watson_u2(A,B)
ou=u2_from(grp); ku=sum(u2_from(rng.permutation(grp))>=ou for _ in range(2000))
print(f"  Watson U2 cat solo vs shared, site-level permutation: U2={ou:.3f} p={(ku+1)/2001:.4f} (2000 perms)")


# ------------------------ cell 12 ------------------------

m=ps['n'].values>=5
pn5,g5=pn[m],grp[m]
print("sites with n>=5:", (g5=='cat_solo').sum(),"solo,",(g5=='both').sum(),"shared")
o3=pn5[g5=='cat_solo'].mean()-pn5[g5=='both'].mean()
k3=sum(abs(pn5[np.array(l)=='cat_solo'].mean()-pn5[np.array(l)=='both'].mean())>=abs(o3) for l in (rng.permutation(g5) for _ in range(20000)))
print(f"site as unit, n>=5: solo mean={pn5[g5=='cat_solo'].mean():.1f}% shared mean={pn5[g5=='both'].mean():.1f}% diff={o3:.1f} pts p={(k3+1)/20001:.4f}")
boot=[rng.choice(pn5[g5=='cat_solo'],(g5=='cat_solo').sum(),True).mean()-rng.choice(pn5[g5=='both'],(g5=='both').sum(),True).mean() for _ in range(10000)]
print("  95%% CI on site-level difference: [%.1f, %.1f] pct pts"%tuple(np.percentile(boot,[2.5,97.5])))


# ------------------------ cell 18 ------------------------

import urllib.request
url="https://cloud.r-project.org/src/contrib/overlap_0.3.9.tar.gz"
urllib.request.urlretrieve(url,"overlap_0.3.9.tar.gz")
import os; print(os.path.getsize("overlap_0.3.9.tar.gz"))


# ------------------------ cell 23 ------------------------

TWO=2*np.pi
def frac(ts):  # local day fraction
    return (ts.hour*3600+ts.minute*60+ts.second)/86400
sr=[];ss=[]
for t in d['ts_loc']:
    a,b_=srss(t.date()); sr.append(frac(a)*TWO); ss.append(frac(b_)*TWO)
sr=np.array(sr); ss=np.array(ss)
clock=np.array([frac(t)*TWO for t in d['ts_loc']])
day=(clock>sr)&(clock<ss)
startClock=np.where(day,sr,ss); dayLength=ss-sr
span=np.where(day,dayLength,TWO-dayLength); startSun=np.where(day,np.pi/2,3*np.pi/2)
d['suntime_rad']=(startSun+((clock-startClock+TWO)%TWO)/span*np.pi)%TWO
d[['site','site_cat','species_group','suntime_rad','cst_min','night']].to_csv("handoff_times.csv",index=False)
print(d.groupby(['site_cat','species_group'])['suntime_rad'].agg(['size','mean']).round(3).to_string())


# ------------------------ cell 30 ------------------------

bs=d[(d.site_cat=='bobcat_solo')]
pv=bs.groupby('site')['night'].mean().values*100
print("bobcat-only per-site %%night (7 sites): %s  mean=%.1f"%(np.round(pv,1),pv.mean()))
bb=[rng.choice(pv,len(pv),True).mean() for _ in range(10000)]
print("  site-level mean %%night 95%% CI: [%.1f, %.1f]; P(<=50)=%.3f"%(*np.percentile(bb,[2.5,97.5]),np.mean(np.array(bb)<=50)))
bsh=d[(d.site_cat=='both')&(d.species_group=='bobcat')]
pv2=bsh.groupby('site')['night'].mean().values*100
print("bobcat shared per-site %%night (7): %s mean=%.1f"%(np.round(pv2,1),pv2.mean()))
cso=d[(d.site_cat=='cat_solo')].groupby('site')['night'].mean().values*100
b2=[rng.choice(cso,len(cso),True).mean() for _ in range(10000)]
print("cat-only site-level mean %%night=%.1f 95%% CI [%.1f, %.1f]; P(<=50)=%.4f"%(cso.mean(),*np.percentile(b2,[2.5,97.5]),np.mean(np.array(b2)<=50)))

# multiplicity across the 2 reported tests
pr=np.array([0.4469,0.0476])
print("\nreported tests, Bonferroni:",np.round(np.minimum(pr*2,1),4)," BH:",np.round(stats.false_discovery_control(pr),4))
print("min attainable p check: Watson U2 is a continuous statistic; not resolution-limited at these n.")


# ------------------------ cell 31 ------------------------

bt=d[d.species_group=='bobcat'].groupby(['site_cat','site'])['night'].agg(['size','mean'])
bt['pct_night']=(100*bt['mean']).round(1); print(bt[['size','pct_night']].to_string())
sel=bt[bt['size']>=5]
print("\nbobcat sites with n>=5 (%d sites): %%night = %s ; mean=%.1f"%(len(sel),list(sel['pct_night']),sel['pct_night'].mean()))


# ------------------------ cell 32 ------------------------

import csv
cols=["id","claim","location","design","experimental_unit","n_reported","n_defensible","test_used",
      "test_indicated","reported_p","recomputed_p","effect_size_CI","verdict","severity"]
rows=[
["C1","Bobcats exhibited primarily nocturnal activity wherever they were present","Abstract; Results",
 "One-sample proportion vs 50% (solar night = half the circle), clustered by site","Camera site (7 solo, 7 shared)",
 "49 + 32 detections","7 + 7 sites","none reported","One-sample proportion with site-clustered interval","none",
 "site-level P(<=50%)=0.342 (bobcat-only sites)",
 "67.3% of detections nocturnal (naive 95% CI 52.5-80.1); site-level mean 55.8% (95% CI 30.3-82.7); 69.1% across the 7 sites with n>=5",
 "Supported, overstated","B"],
["C2","Domestic cats were primarily nocturnal at sites where no bobcats were detected","Results",
 "One-sample proportion vs 50%, clustered by site","Camera site (19)","696 detections","19 sites","none reported",
 "One-sample proportion with site-clustered interval","none","site-level P(<=50%)<0.0001",
 "85.5% nocturnal (naive 95% CI 82.6-88.0); site-level mean 80.3% (95% CI 69.8-89.3)","Supported","none"],
["C3","Diel activity of bobcats and domestic cats was similar where only one species occurred","Results; Fig 1C",
 "Two-sample circular, but species is perfectly confounded with site set","Camera site (7 bobcat-only vs 19 cat-only)",
 "49 vs 696 detections","7 vs 19 sites","Watson's U2 (two-sample)",
 "Watson's U2 is the right family; the contrast is not identifiable, and an absence claim needs an equivalence margin",
 "U2=0.0753, p<0.20","U2=0.0753 (exact reproduction), asymptotic p=0.4469; 30-min filtered U2=0.0855, p=0.3674",
 "Dhat1=0.8525; no equivalence margin stated","Mis-specified","B"],
["C4","High overlap between diel activity patterns at solo sites, Dhat = 0.852","Results; deposited figure",
 "Point estimate of a coefficient of overlap (not a test)","Camera site","49 vs 696 detections","7 vs 19 sites",
 "Dha…[+4608 chars]


# ------------------------ cell 34 ------------------------

import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,
                     'xtick.direction':'out','ytick.direction':'out','savefig.dpi':300})

# ---------- FIG 1: how p for C5 depends on the experimental unit ----------
labs=["As reported\n(every detection,\nasymptotic null)",
      "30-min independence\nfilter\n(asymptotic null)",
      "All detections,\nspecies labels permuted\nwithin site",
      "30-min filter +\nwithin-site\npermutation"]
pv=[0.0476,0.1036,0.0720,0.1162]
ns=["n = 32 vs 99","n = 28 vs 91","n = 32 vs 99\n(7 site strata)","n = 28 vs 91\n(7 site strata)"]
fig,ax=plt.subplots(figsize=(7.4,4.6))
x=np.arange(4)
ax.axhspan(0,0.05,color='#d8d8d8',alpha=.55,zorder=0)
ax.axhline(0.05,color='#444',lw=1,ls='--',zorder=1)
cols=['#b2182b' if p<0.05 else '#2166ac' for p in pv]
ax.scatter(x,pv,s=150,c=cols,zorder=3,edgecolor='k',linewidth=.6)
for i,(p,n) in enumerate(zip(pv,ns)):
    ax.annotate(f"p = {p:.3f}",(i,p),xytext=(0,14),textcoords='offset points',ha='center',fontsize=10,fontweight='bold')
    ax.annotate(n,(i,p),xytext=(0,-30),textcoords='offset points',ha='center',fontsize=8,color='#555')
ax.text(3.45,0.047,"α = 0.05",ha='right',va='top',fontsize=9,color='#444')
ax.set_xticks(x); ax.set_xticklabels(labs,fontsize=8.5)
ax.set_xlim(-0.5,3.5); ax.set_ylim(0,0.16)
ax.set_ylabel("Watson's $U^2$ two-sample p-value")
ax.set_title("The paper's only significant test does not survive the experimental unit\n"
             "Bobcat vs domestic cat diel activity at the 7 shared sites (claim C5)",fontsize=11,loc='left')
ax.text(0,-0.038,"A detection is not an independent animal: 11.8% of consecutive same-species, same-camera gaps are <30 min,\n"
        "and 2 of the 7 shared cameras carry 91% of the cat and 69% of the bobcat detections. "
        "Statistic reproduces exactly ($U^2$ = 0.1893).",
        transform=ax.transAxe…[+199 chars]


# ------------------------ cell 35 ------------------------

fig,ax=plt.subplots(figsize=(7.6,5.4))
ax.axhspan(0,0.05,color='#d8d8d8',alpha=.55,zorder=0)
ax.axhline(0.05,color='#444',lw=1,ls='--',zorder=1)
ax.scatter(x,pv,s=150,c=cols,zorder=3,edgecolor='k',linewidth=.6)
for i,(p,n) in enumerate(zip(pv,ns)):
    ax.annotate(f"p = {p:.3f}",(i,p),xytext=(0,13),textcoords='offset points',ha='center',fontsize=10,fontweight='bold')
    ax.annotate(n.replace("\n"," "),(i,p),xytext=(0,-20),textcoords='offset points',ha='center',fontsize=7.5,color='#555')
ax.text(3.45,0.047,"α = 0.05",ha='right',va='top',fontsize=9,color='#444')
ax.set_xticks(x); ax.set_xticklabels(labs,fontsize=8.5)
ax.set_xlim(-0.5,3.5); ax.set_ylim(0,0.16)
ax.set_ylabel("Watson's $U^2$ two-sample p-value")
ax.set_title("The paper's only significant test does not survive the experimental unit\n"
             "Bobcat vs domestic cat diel activity at the 7 shared sites (claim C5)",fontsize=11,loc='left')
fig.tight_layout(rect=[0,0.14,1,1])
fig.text(0.01,0.085,"A detection is not an independent animal: 11.8% of consecutive same-species, same-camera gaps are <30 min, and 2 of the 7 shared\n"
         "cameras carry 91% of the cat and 69% of the bobcat detections. The statistic itself reproduces exactly ($U^2$ = 0.1893); only the null changes.\n"
         "Permutation p from 5,000 within-site label shuffles. Shaded band = p < 0.05.",fontsize=7.6,color='#444',va='top')
audit_figure(fig); fig.savefig("fig_alavinaini_unit_sensitivity.png",bbox_inches='tight')
print("ok")


# ------------------------ cell 36 ------------------------

bd=pd.read_csv("handoff_boot_det.csv")
Q=lambda v:np.percentile(v,[2.5,97.5])
est={'solo':0.8525,'shared':0.6465}
dsolo,dsh=bd['det_solo'].values,bd['det_shared'].values
# site-cluster reps were only written to a file in the earlier failed cell; recompute summary from stored numbers
site_ci={'solo':(0.574,0.856),'shared':(0.494,0.759)}
det_ci={'solo':tuple(Q(dsolo)),'shared':tuple(Q(dsh))}
diff={'det':(0.206,-0.004,0.312),'site':(0.206,-0.088,0.310)}

fig,axes=plt.subplots(1,2,figsize=(9.6,4.8),gridspec_kw={'width_ratios':[1.25,1]})
ax=axes[0]
ypos={'solo':[2.15,1.85],'shared':[1.15,0.85]}
colr={'det':'#2166ac','site':'#b2182b'}
for g in ['solo','shared']:
    for sch,ci in [('det',det_ci[g]),('site',site_ci[g])]:
        y=ypos[g][0 if sch=='det' else 1]
        ax.plot(ci,[y,y],color=colr[sch],lw=3,solid_capstyle='butt')
        ax.plot(est[g],y,'o',color=colr[sch],ms=8,mec='k',mew=.6,zorder=3)
        ax.text(ci[1]+0.012,y,f"{est[g]:.3f}  [{ci[0]:.3f}, {ci[1]:.3f}]",va='center',fontsize=8.5,color=colr[sch])
ax.set_yticks([2.0,1.0]); ax.set_yticklabels(["Single-species sites\n(7 bobcat-only vs 19 cat-only;\n49 vs 696 detections)",
                                              "Shared sites\n(7 sites;\n32 vs 99 detections)"],fontsize=8.5)
ax.set_ylim(0.5,2.6); ax.set_xlim(0.45,1.14)
ax.set_xlabel("Coefficient of overlap  $\\hat{\\Delta}_1$  (0 = no overlap, 1 = identical)")
ax.set_title("Both published $\\hat{\\Delta}$ reproduce exactly;\ntheir 95% intervals overlap",fontsize=10.5,loc='left')
ax.legend(handles=[Line2D([],[],color=colr['det'],lw=3,label='bootstrap over detections (n=2,000)'),
                   Line2D([],[],color=colr['site'],lw=3,label='bootstrap over sites (n=2,000)')],
          frameon=False,fontsize=8,loc='lower left')

ax=axes[1]
for i,(k,lab) in enumerate([('det','detections'),('site','sites')]):
    e,lo,hi=diff[k]; y=1-i*0.5
    ax.plot([lo,hi],[y,y],color=colr[k],lw=3,solid_capstyle='butt')
    ax.plot(e,y,'o',color=colr[k],ms=8,mec='k',me…[+1135 chars]


# ------------------------ cell 37 ------------------------

ps_all=d.groupby(['species_group','site_cat','site'])['night'].agg(n='size',p='mean').reset_index()
ps_all['p']*=100
fig,axes=plt.subplots(1,2,figsize=(10.2,5.0),sharey=True)
layout=[('domestic_cat',[('cat_solo','Cat-only sites\n(19 cameras)'),('both','Shared sites\n(7 cameras)')],
         "Domestic cat",{'cat_solo':85.5,'both':51.5}),
        ('bobcat',[('bobcat_solo','Bobcat-only sites\n(7 cameras)'),('both','Shared sites\n(7 cameras)')],
         "Bobcat",{'bobcat_solo':67.3,'both':65.6})]
for ax,(sp,groups,title,detpct) in zip(axes,layout):
    for xi,(gc,glab) in enumerate(groups):
        s=ps_all[(ps_all.species_group==sp)&(ps_all.site_cat==gc)]
        jit=rng.uniform(-0.13,0.13,len(s))
        big=s['n']>=5
        ax.scatter(xi+jit[~big.values],s['p'][~big.values],s=np.sqrt(s['n'][~big.values])*22,
                   facecolor='none',edgecolor='#999',linewidth=1.0,zorder=2)
        ax.scatter(xi+jit[big.values],s['p'][big.values],s=np.sqrt(s['n'][big.values])*22,
                   color='#2166ac',alpha=.75,edgecolor='k',linewidth=.5,zorder=3)
        ax.hlines(detpct[gc],xi-0.28,xi+0.28,color='#b2182b',lw=2.5,zorder=4)
        ax.text(xi+0.31,detpct[gc],f"{detpct[gc]:.0f}%",color='#b2182b',fontsize=9,va='center',fontweight='bold')
        m=s['p'][big.values].mean()
        ax.hlines(m,xi-0.28,xi+0.28,color='#111',lw=1.6,ls=(0,(4,2)),zorder=4)
        ax.text(xi-0.31,m,f"{m:.0f}%",color='#111',fontsize=9,va='center',ha='right')
    ax.axhline(50,color='#bbb',lw=1,zorder=1)
    ax.set_xticks([0,1]); ax.set_xticklabels([g[1] for g in groups],fontsize=9)
    ax.set_xlim(-0.55,1.55); ax.set_ylim(-6,112); ax.set_title(title,fontsize=11,loc='left')
axes[0].set_ylabel("Detections occurring at night (%)\nper camera site")
axes[0].text(-0.5,50+3,"50% = activity uniform in solar time",fontsize=7.5,color='#888')
axes[0].legend(handles=[Line2D([],[],marker='o',color='none',mfc='#2166ac',mec='k',ms=8,label='site with ≥5 detections'),
    Line2D([],[],marker='o',color…[+1086 chars]


# ------------------------ cell 38 ------------------------

for t in axes[0].texts:
    if "uniform in solar" in t.get_text(): t.set_position((-0.5,41)); t.set_va('top')
fig.savefig("fig_alavinaini_site_unit.png",bbox_inches='tight'); print("saved")


# ------------------------ cell 42 ------------------------

import csv, json
rows=list(csv.DictReader(open("claims_alavinaini.csv",encoding="utf-8")))
claims=[{"id":r["id"],"claim":r["claim"],"design":r["design"],"test_used":r["test_used"],
         "test_indicated":r["test_indicated"],"reported_p":r["reported_p"],"recomputed_p":r["recomputed_p"],
         "effect":r["effect_size_CI"],"verdict":r["verdict"],"severity":r["severity"]} for r in rows]
out={
 "paper":"Alavi Naini L, Linde N, Malik S, Syed Y, Cheek AO (2026). Diel Activity Patterns of Bobcats and Domestic Cats in the Houston Metropolitan Area. microPublication Biology.",
 "doi":"10.17912/micropub.biology.001911",
 "n_claims":len(claims),
 "claims":claims,
 "headline_findings":[
  "The paper's only significant test (C5: bobcat vs domestic cat diel activity at the 7 shared sites, Watson's U2 = 0.189, p < 0.05) reproduces exactly (U2 = 0.1893, exact asymptotic p = 0.0476) but does not survive the experimental unit: p = 0.104 after a 30-minute camera-trap independence filter, p = 0.072 under a site-stratified permutation null on unfiltered data, and p = 0.116 under both. Detections are not independent - 11.8% of consecutive same-species same-camera gaps are under 30 minutes, and 2 of the 7 shared cameras carry 91% of the cat and 69% of the bobcat detections.",
  "The abstract's headline claim (C7: domestic cats shift to more daytime activity where bobcats are present, 51% vs 85% nocturnal) is never tested in the paper - the reported shared-site test is a cat-vs-bobcat contrast, not the cat-vs-cat contrast the claim makes. When tested, the difference is real and large (24.5 percentage points with the site as the unit, bootstrap 95% CI 11.8-36.3; site-level permutation p = 0.088; Watson's U2 = 1.281) but only 3 shared sites have enough detections to contribute, and the two site groups differ in developed land cover (65% vs 82%) and distance from downtown, so bobcat presence cannot be separated from urbanisation.",
  "Both overlap coefficients reproduce exactly (Dhat1 = …[+3220 chars]
