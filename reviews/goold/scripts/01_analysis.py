# ==========================================================================
# goold review -- python cells, verbatim and in execution order
# conda env: python
# 31 cells with exit_status='ok'; cells that errored are omitted.
# Run top-to-bottom in ONE session: the originals ran in a persistent
# kernel, so later cells depend on earlier state.
# ==========================================================================


# ------------------------ cell 1 ------------------------

import os
for root, dirs, files in os.walk("goold"):
    for f in files:
        p = os.path.join(root, f)
        print(f"{os.path.getsize(p):>10}  {p}")


# ------------------------ cell 2 ------------------------

import pandas as pd, numpy as np
raw = pd.read_csv("goold/data/rawData.csv")
mi  = pd.read_csv("goold/data/finalMIdata_averaged_rounded.csv")
pat = pd.read_csv("goold/data/PatrolDog_GGM_AssociationMatrix.csv", index_col=0)
det = pd.read_csv("goold/data/DetectionDog_GGM_AssociationMatrix.csv", index_col=0)
print("raw", raw.shape, "| mi", mi.shape, "| pat", pat.shape, "| det", det.shape)
print("raw cols:", list(raw.columns))
print("mi cols:", list(mi.columns))


# ------------------------ cell 3 ------------------------

print(raw['workType'].value_counts(dropna=False).to_dict())
print(mi['workType'].value_counts(dropna=False).to_dict())
print("raw newID n unique:", raw['newID'].nunique(), " mi id n unique:", mi['id'].nunique())
vc = mi['id'].value_counts()
print("surveys per handler (MI data):", vc.value_counts().sort_index().to_dict())
print("mean/sd surveys per handler:", round(vc.mean(),3), round(vc.std(ddof=1),3))
# handlers spanning both work types
span = mi.groupby('id')['workType'].nunique()
print("handlers rating >1 workType:", int((span>1).sum()))
# per-group handler counts
for wt, g in mi.groupby('workType'):
    print(wt, "dogs:", len(g), "handlers:", g['id'].nunique(), "max dogs/handler:", g['id'].value_counts().max())
print("GGM node labels:", list(pat.columns))
print("symmetric pat:", np.allclose(pat.values, pat.values.T), "symmetric det:", np.allclose(det.values, det.values.T))
print("nonzero edges pat:", int((np.triu(pat.values,1)!=0).sum()), " det:", int((np.triu(det.values,1)!=0).sum()))


# ------------------------ cell 4 ------------------------

src = open("goold/data/Rscript.R", encoding="latin-1").read()
print(len(src.splitlines()), "lines")
import re
pats = {
 "EBICglasso": r"EBICglasso|glasso|gamma\s*=|tuning",
 "bootnet": r"bootnet|nBoots|nCores|bootstrap",
 "cliff": r"cliff|cliffs_delta|effsize|delta",
 "centrality": r"centrality|betweenness|strength|centrality_auto|centralityTable",
 "amelia": r"amelia|Amelia|m\s*=\s*15|impute",
 "ttest/lm": r"t\.test|wilcox|lmer|lme\b|glm\(|aov\(|anova|chisq|cor\.test",
 "polychoric": r"polychoric|lavCor|hetcor",
}
for k, p in pats.items():
    hits = [(i+1, l.strip()[:150]) for i,l in enumerate(src.splitlines()) if re.search(p, l)]
    print(f"\n=== {k}: {len(hits)} hits")
    for h in hits[:28]: print("  ", h[0], h[1])


# ------------------------ cell 5 ------------------------

L = src.splitlines()
def show(a,b):
    for i in range(a-1,min(b,len(L))): print(f"{i+1:4d} {L[i]}")
show(100,175)


# ------------------------ cell 6 ------------------------

show(218,330)


# ------------------------ cell 7 ------------------------

import pypdfium2 as pdfium
pdf = pdfium.PdfDocument("goold/data/Supplementary_Material_Revised.pdf")
print("pages:", len(pdf))
for i in range(len(pdf)):
    t = pdf[i].get_textpage().get_text_range()
    head = " ".join(t.split())[:160]
    print(i+1, "|", head)


# ------------------------ cell 8 ------------------------

for p in (2,5,7,8):
    print(f"\n########## PAGE {p} ##########")
    print(pdf[p-1].get_textpage().get_text_range())


# ------------------------ cell 13 ------------------------

show(752,800)


# ------------------------ cell 14 ------------------------

print(raw['handlerType'].value_counts(dropna=False).to_dict())
# align raw -> mi (one patrol dog removed)
print("raw ids==mi ids order?", list(raw['newID'])[:5], list(mi['id'])[:5], raw.shape[0], mi.shape[0])
# aggression-vs-desirable edge comparison (C16) from deposited matrices
nodes = list(pat.columns)
agg = ['DA','GWL','FDA']
undes = ['DA','GWL','FDA','STR','GUS','FoH']
des = [n for n in nodes if n not in undes]
for name, M in (("patrol", pat), ("detection", det)):
    sub = M.loc[agg, des].values
    neg = sub[sub<0]; pos = sub[sub>0]
    sub2 = M.loc[agg, [u for u in undes if u not in agg]].values
    print(f"{name}: agg-desirable edges n={int((sub!=0).sum())} neg={len(neg)} (sum={neg.sum():.3f}) pos={len(pos)} (sum={pos.sum():.3f}) | agg-other-undesirable nonzero={int((sub2!=0).sum())} sum={sub2[sub2!=0].sum():.3f}")


# ------------------------ cell 17 ------------------------

from scipy import stats
s2 = """ACT 2 0 0.988|ADP 0.93 1.069 0.301|ANX -8.13 10.131 0.001|CB 1.731 0.269 0.604|CC -4.85 6.85 0.009|CUR 2 0 0.996|DA 0.34 1.66 0.2|FDA -1.75 3.753 0.052|FHO -2.62 4.617 0.032|FIT 0.17 1.822 0.177|FL 1.99 0.011 0.915|FoH -0.62 2.626 0.105|FSH 0.1 1.9 0.168|GUS 1.69 0.31 0.578|GWL -0.76 2.762 0.097|OCD -1.99 3.985 0.046|OCN -8.46 10.46 0.001|PLA 2 0.002 0.968|PS 1.97 0.024 0.877|PSV 1.99 0.009 0.927|QU -19.13 21.133 0|REC 0.46 1.535 0.215|SLP 1.04 0.959 0.327|SOC 1.69 0.308 0.579|STR -0.54 2.536 0.111|TC -3.68 5.68 0.017|TOY 1.4 0.601 0.438|TUG -6.39 8.386 0.004|WIL -0.62 2.626 0.105"""
rows=[]
for r in s2.split("|"):
    d,a,lr,p = r.split()
    rows.append(dict(desc=d, dAIC=float(a), LR=float(lr), p_rep=float(p)))
S2 = pd.DataFrame(rows)
S2['p_chi2_1df'] = stats.chi2.sf(S2.LR, 1)            # naive null the authors used
S2['p_boundary'] = 0.5*stats.chi2.sf(S2.LR, 1)        # correct 0.5 chi2_0 + 0.5 chi2_1 null
final20 = list(pat.columns)
S2['retained'] = S2.desc.isin(final20)
S2['removed_by_authors'] = S2.p_rep < 0.05
print("reported p == chi2.sf(LR,1) to 3dp for all rows:",
      bool((np.abs(S2.p_chi2_1df.round(3) - S2.p_rep) <= 0.001).all()))
print("removed by authors (p<.05):", sorted(S2[S2.removed_by_authors].desc), " n =", int(S2.removed_by_authors.sum()))
flip = S2[(~S2.removed_by_authors) & (S2.p_boundary < 0.05)]
print("\nRetained by authors but significant under boundary-corrected null:")
print(flip[['desc','LR','p_rep','p_boundary','retained']].to_string(index=False))
# BH across the 29 screening tests, naive null
from statsmodels.stats.multitest import multipletests
S2['q_BH_naive'] = multipletests(S2.p_chi2_1df, method='fdr_bh')[1]
S2['q_BH_bound'] = multipletests(S2.p_boundary, method='fdr_bh')[1]
print("\nn significant: raw-naive", int((S2.p_chi2_1df<.05).sum()),
      "| raw-boundary", int((S2.p_boundary<.05).sum()),
      "| BH-naive", int((S2.q_BH_naive<.05).sum()),
      "| BH-boundary", int((S2.q_BH_bound<.05).sum(…[+48 chars]


# ------------------------ cell 18 ------------------------

m = S2[(S2.p_chi2_1df.round(3)-S2.p_rep).abs() > 0.001]
print(m[['desc','LR','p_rep','p_chi2_1df']].to_string(index=False))


# ------------------------ cell 19 ------------------------

S4 = pd.DataFrame({
 'node':['ACT','ADP','CUR','DA','FDA','FIT','FL','FoH','FSH','GUS','GWL','PLA','PS','PSV','REC','SLP','SOC','STR','TOY','WIL'],
 'Pb':[14,52,84,0,32,32,60,0,4,8,4,108,4,8,30,42,46,0,0,40],
 'Db':[4,50,26,12,22,20,36,0,48,42,34,100,16,40,6,0,18,2,22,26],
 'Ps':[1.026,0.990,1.282,0.189,0.556,0.954,1.011,0.528,0.511,0.596,0.617,1.083,0.805,0.901,0.873,0.932,1.008,0.510,0.372,0.984],
 'Ds':[0.758,1.049,1.168,0.664,0.759,0.877,1.146,0.345,1.240,1.062,0.922,1.321,1.039,0.984,0.736,0.667,1.155,0.529,0.682,1.218]})
undes = ['DA','FDA','FoH','GUS','GWL','STR']
S4['desirable'] = ~S4.node.isin(undes)
# C5
for net_, b, s in (("patrol",'Pb','Ps'), ("detection",'Db','Ds')):
    print(f"C5 {net_}: top betw={S4.loc[S4[b].idxmax(),'node']}({S4[b].max()}), top strength={S4.loc[S4[s].idxmax(),'node']}({S4[s].max()})")
# C4
for net_, b, s in (("patrol",'Pb','Ps'), ("detection",'Db','Ds')):
    d, u = S4[S4.desirable], S4[~S4.desirable]
    rb = stats.mannwhitneyu(d[b], u[b], alternative='two-sided')
    rs = stats.mannwhitneyu(d[s], u[s], alternative='two-sided')
    print(f"C4 {net_}: betw median des/undes {d[b].median():.1f}/{u[b].median():.1f} PS={rb.statistic/(14*6):.3f} p={rb.pvalue:.4f} | "
          f"str median {d[s].median():.3f}/{u[s].median():.3f} PS={rs.statistic/(14*6):.3f} p={rs.pvalue:.4f}")
# C6 / C7
c6 = ['ACT','CUR','FIT','REC','SLP']; c7=['DA','FSH','GUS','GWL','PS','PSV','STR','TOY']
S4['patrol_higher_both'] = (S4.Pb>S4.Db)&(S4.Ps>S4.Ds); S4['det_higher_both'] = (S4.Db>S4.Pb)&(S4.Ds>S4.Ps)
print("C6 claimed:", c6, "-> actually patrol-higher-on-both:", sorted(S4[S4.patrol_higher_both].node))
print("C7 claimed:", c7, "-> actually detection-higher-on-both:", sorted(S4[S4.det_higher_both].node))
# C16 full
agg=['DA','GWL','FDA']; des=[n for n in S4.node if n not in undes]
for name, M in (("patrol",pat),("detection",det)):
    ad = M.loc[agg,des].values.ravel(); ad=ad[ad!=0]
    au = M.loc[agg,[u for u in undes if u not in agg]].values.ravel(); au=au[…[+383 chars]


# ------------------------ cell 22 ------------------------

print(host.exec_peek("d6f1a988-c91c-49a8-92fe-51cac86b53d6"))


# ------------------------ cell 25 ------------------------

import re
for i,l in enumerate(L):
    if re.search(r"patrolBootCent\s*(<-|=)|detectBootCent\s*(<-|=)|BootCent", l) and "cliff" not in l:
        print(i+1, l.strip()[:200])


# ------------------------ cell 26 ------------------------

show(555,600)


# ------------------------ cell 28 ------------------------

show(344,410)


# ------------------------ cell 33 ------------------------

S5p = pd.DataFrame({
 'node':['ACT','ADP','CUR','DA','FDA','FIT','FL','FoH','FSH','GUS','GWL','PLA','PS','PSV','REC','SLP','SOC','STR','TOY','WIL'],
 'delta':[.282,.211,.452,-.609,-.302,.136,.050,.130,-.614,-.582,-.310,.151,-.092,-.049,-.063,.290,.092,-.089,-.465,.019],
 'lo':[.249,.181,.425,-.637,-.336,.103,.019,.095,-.643,-.612,-.344,.120,-.126,-.084,-.098,.259,.059,-.125,-.496,-.014],
 'hi':[.315,.241,.478,-.579,-.268,.169,.081,.165,-.582,-.551,-.275,.181,-.057,-.015,-.027,.320,.124,.053,-.432,.053]})
S5p['hw'] = (S5p.hi-S5p.lo)/2
S5p['excl0'] = (S5p.lo*S5p.hi) > 0
S5p['negligible'] = S5p.delta.abs() <= 0.25
print("mean CI half-width:", round(S5p.hw.mean(),4), " range:", round(S5p.hw.min(),4), round(S5p.hw.max(),4))
print("CIs excluding 0:", int(S5p.excl0.sum()), "/20")
print("nodes the paper calls negligible (|d|<=0.25) whose CI still excludes 0:",
      sorted(S5p[(S5p.negligible)&(S5p.excl0)].node.tolist()), f"= {int(((S5p.negligible)&(S5p.excl0)).sum())} of {int(S5p.negligible.sum())}")
print("only node with CI containing 0:", S5p[~S5p.excl0].node.tolist())
# implied half-width at other nBoot (SE scales 1/sqrt(B))
for B in (200, 500, 2000, 20000):
    print(f"  implied mean half-width at nBoot={B}: {S5p.hw.mean()*np.sqrt(2000/B):.4f}  -> |delta| resolvable: {S5p.hw.mean()*np.sqrt(2000/B):.3f}")
S5p.to_csv("s5_published.csv", index=False)


# ------------------------ cell 42 ------------------------

import json, numpy as np, pandas as pd
J = json.load(open("handoff/goold_stats.json"))
print(sorted(J.keys()))
nodes = J['nodes']
# empirical Cliff's delta CI half-width vs number of replicates, from the 80% subsample replicates
subBP, subBD = np.array(J['subBetwP']), np.array(J['subBetwD'])
subSP, subSD = np.array(J['subStrP']),  np.array(J['subStrD'])
print("subsample replicate matrices:", subBP.shape, subBD.shape)

def cliff_ci(x, y, z=1.96):
    x = np.asarray(x); y = np.asarray(y); n1, n2 = len(x), len(y)
    ys = np.sort(y)
    lt = np.searchsorted(ys, x, side='left'); le = np.searchsorted(ys, x, side='right')
    d = (lt.sum() - (n2 - le).sum()) / (n1*n2)
    di = (lt - (n2-le))/n2                      # per-x dominance
    ys2 = np.sort(x); lt2 = np.searchsorted(ys2, y, side='left'); le2 = np.searchsorted(ys2, y, side='right')
    dj = ((n1-le2) - lt2)/n1
    s2i = di.var(ddof=1); s2j = dj.var(ddof=1)
    var = ((n2**2)*s2i + (n1**2)*s2j - s2i*s2j) / (n1*n2*(n1-1)*(n2-1)) if n1>1 and n2>1 else np.nan
    return d, z*np.sqrt(max(var, 0))

Bs = [125, 250, 500, 1000]
hw = []
for B in Bs:
    h = [np.mean([cliff_ci(subBP[:B,i], subBD[:B,i])[1], cliff_ci(subSP[:B,i], subSD[:B,i])[1]]) for i in range(20)]
    hw.append(np.mean(h))
hw = np.array(hw)
print("empirical mean CI half-width by B:", dict(zip(Bs, hw.round(4))))
print("half-width * sqrt(B):", (hw*np.sqrt(Bs)).round(3))


# ------------------------ cell 44 ------------------------

J = json.load(open("handoff/goold_stats.json"))
A = np.array(J['subStrP']); Bm = np.array(J['clkStrP'])   # two resampling distributions of the SAME quantity
i = nodes.index('CUR')
print("CUR patrol strength: dog-subsample mean/sd %.4f/%.4f | handler-subsample mean/sd %.4f/%.4f"
      % (A[:,i].mean(), A[:,i].std(ddof=1), Bm[:,i].mean(), Bm[:,i].std(ddof=1)))
Bs = np.array([50,100,200,400,800,1000])
emp = np.array([cliff_ci(A[:b,i], Bm[:b,i]) for b in Bs])
print(pd.DataFrame({'B':Bs,'delta':emp[:,0].round(4),'halfwidth':emp[:,1].round(4),
                    'hw*sqrt(B)':(emp[:,1]*np.sqrt(Bs)).round(3),
                    'CI excludes 0':(np.abs(emp[:,0])>emp[:,1])}).to_string(index=False))


# ------------------------ cell 45 ------------------------

def cliff_ci(x, y, z=1.96):
    """Cliff's delta with the consistent (Cliff 1993) variance estimator, as used by effsize."""
    x = np.asarray(x, float); y = np.asarray(y, float); n1, n2 = len(x), len(y)
    ys = np.sort(y); xs = np.sort(x)
    lt = np.searchsorted(ys, x, 'left');  le = np.searchsorted(ys, x, 'right')
    di = (lt - (n2 - le)) / n2                       # dominance of each x over all y
    lt2 = np.searchsorted(xs, y, 'left'); le2 = np.searchsorted(xs, y, 'right')
    dj = ((n1 - le2) - lt2) / n1                     # dominance of all x over each y
    d = di.mean()
    SSi = ((di - d)**2).sum(); SSj = ((dj - d)**2).sum()
    # sum over all n1*n2 pairwise dominances of (dij - d)^2  = sum dij^2 - n1*n2*d^2
    nties = (le - lt).sum()
    SSij = (n1*n2 - nties) - n1*n2*d**2
    var = (n2**2*SSi + n1**2*SSj - SSij) / (n1*n2*(n1-1)*(n2-1))
    return d, z*np.sqrt(max(var, 0.0))

# sanity: reproduce the published CI scale at B=2000 on a real pair of replicate distributions
i = nodes.index('CUR')
Bs = np.array([50,100,200,400,800,1000])
emp = np.array([cliff_ci(A[:b,i], Bm[:b,i]) for b in Bs])
tab = pd.DataFrame({'B':Bs,'delta':emp[:,0].round(4),'half_width':emp[:,1].round(4),
                    'hw*sqrt(B)':(emp[:,1]*np.sqrt(Bs)).round(3),
                    'excludes_0':(np.abs(emp[:,0])>emp[:,1])})
print(tab.to_string(index=False))
print("\npublished mean half-width at B=2000:", 0.0350,
      "| this estimator at B=1000 scaled to 2000:", round(emp[-1,1]/np.sqrt(2),4))


# ------------------------ cell 49 ------------------------

axes[1].set_xlabel('bootstrap replicates compared, $n_{boot}$ (log scale)')
axes[1].set_ylabel("95% interval half-width for $\\delta$ (log scale)")
fig.savefig("fig_goold_delta_intervals.png", dpi=300, bbox_inches='tight')
print([x for x in audit_figure(fig)])

# ---- Figure 2: edge stability under subsampling + matched-n edge counts
plt.close('all')
inclP, inclD = np.array(J['inclP']), np.array(J['inclD'])
ez, ed = np.array(J['ez'], bool), np.array(J['ed'], bool)
subEP, subED = np.array(J['subEdgesP']), np.array(J['subEdgesD'])
mEdges = np.array(J['matched']['edges'])
fig2, ax2 = plt.subplots(1, 3, figsize=(11.4, 3.9), gridspec_kw=dict(wspace=0.33))

a0 = ax2[0]
bins = np.linspace(0,1,21)
a0.hist(inclP[ez], bins=bins, color='#2166AC', alpha=0.85, label=f'patrol, published edges (n={ez.sum()})')
a0.hist(inclD[ed], bins=bins, color='#B2182B', alpha=0.70, label=f'detection, published edges (n={ed.sum()})')
a0.axvline(0.5, color='0.35', lw=0.9, ls='--')
a0.text(0.52, a0.get_ylim()[1]*0.93, 'recovered in half\nof subsamples', fontsize=7, color='0.35')
a0.set_xlabel('fraction of 80% subsamples in which the edge is non-zero')
a0.set_ylabel('number of published edges')
a0.set_title('Patrol edges reappear (median 0.88);\ndetection edges do not (median 0.02)', loc='left')
a0.legend(frameon=False, fontsize=7, loc='upper center')
panel_letter(a0, 'a')

a1 = ax2[1]
a1.hist(subEP, bins=np.arange(-2.5, 100, 5), color='#2166AC', alpha=0.85, label='patrol (n=93 per subsample)')
a1.hist(subED, bins=np.arange(-2.5, 100, 5), color='#B2182B', alpha=0.70, label='detection (n=43 per subsample)')
a1.axvline(55, color='#2166AC', lw=1.4); a1.axvline(70, color='#B2182B', lw=1.4)
a1.annotate('published\n55', (55, a1.get_ylim()[1]*0.62), fontsize=7, color='#2166AC', ha='center')
a1.annotate('published\n70', (70, a1.get_ylim()[1]*0.42), fontsize=7, color='#B2182B', ha='center')
a1.set_xlabel('edges selected (of 190 possible)'); a1.set_ylabel('subsamples (of 1000)')
a1.set_title('91% of detectio…[+812 chars]


# ------------------------ cell 50 ------------------------

a0.clear()
a0.hist(inclP[ez], bins=bins, color='#2166AC', alpha=0.85, label=f'patrol, published edges (n={ez.sum()})')
a0.hist(inclD[ed], bins=bins, color='#B2182B', alpha=0.70, label=f'detection, published edges (n={ed.sum()})')
a0.axvline(0.5, color='0.35', lw=0.9, ls='--')
a0.set_ylim(0, 78)
a0.text(0.47, 46, 'recovered in half\nof subsamples', fontsize=7, color='0.35', ha='right')
a0.set_xlabel('fraction of 80% subsamples in which the edge is non-zero')
a0.set_ylabel('number of published edges')
a0.set_title(f'Patrol edges reappear (median {np.median(inclP[ez]):.2f});\ndetection edges do not (median {np.median(inclD[ed]):.2f})', loc='left')
a0.legend(frameon=False, fontsize=7, loc='upper center')
panel_letter(a0, 'a')
fig2.savefig("fig_goold_edge_stability.png", dpi=300, bbox_inches='tight')

# ---- Figure 3: permutation tests of between-type difference
plt.close(fig)
nullSS = np.array(J['nullSS']); obsSS = J['obsSS']; pSS = J['pSS']
st = J['strength']; nullSt = np.array(st['nullStat'])
pPair = np.array(J['pPair']); qBH = np.array(J['qBH']); pF = np.array(J['pFWER'])
fig3, ax3 = plt.subplots(1, 3, figsize=(11.4, 3.8), gridspec_kw=dict(wspace=0.33))

b0 = ax3[0]
b0.hist(nullSS, bins=36, color='0.72')
b0.axvline(obsSS, color='#B2182B', lw=1.8)
b0.annotate(f'observed\n{obsSS:.1f}\np = {pSS:.2f}', (obsSS, b0.get_ylim()[1]*0.60), fontsize=7.5,
            color='#B2182B', ha='right', xytext=(-6,0), textcoords='offset points')
b0.set_xlabel('$\\Sigma$ (r$_{patrol}$ − r$_{detection}$)$^2$ over 190 descriptor pairs')
b0.set_ylabel('permutations (of 2000)')
b0.set_title('Observed structure difference is smaller\nthan the median chance relabelling', loc='left')
panel_letter(b0, 'a')

b1 = ax3[1]
b1.hist(nullSt, bins=36, color='0.72')
b1.axvline(st['obsStat'], color='#B2182B', lw=1.8)
b1.annotate(f"observed\n{st['obsStat']:+.3f}\np = {st['p']:.2f}", (st['obsStat'], b1.get_ylim()[1]*0.60),
            fontsize=7.5, color='#B2182B', ha='left', xytext=(6,0), textcoords='offse…[+1091 chars]


# ------------------------ cell 51 ------------------------

ymax = max(b0.get_ylim()[1], b1.get_ylim()[1])
b0.set_ylim(0, ymax); b1.set_ylim(0, ymax)
b2.legend(frameon=False, fontsize=7, loc='center right', bbox_to_anchor=(1.0, 0.33))
fig3.savefig("fig_goold_permutation.png", dpi=300, bbox_inches='tight')
print([x for x in audit_figure(fig3)])

# ---- Figure 4: handler dependence
plt.close(fig2)
icc = pd.DataFrame(J['icc']).sort_values('ICC')
S2 = pd.read_csv("s2_recomputed.csv")
fig4, ax4 = plt.subplots(1, 2, figsize=(10.4, 4.3), gridspec_kw=dict(width_ratios=[1,1.1], wspace=0.30))
c0 = ax4[0]
cols = ['#B2182B' if n in ('FDA','GWL') else '#2166AC' for n in icc.node]
c0.barh(np.arange(len(icc)), icc.ICC, color=cols)
c0.axvline(0.10, color='0.35', lw=0.9, ls='--')
c0.set_yticks(np.arange(len(icc))); c0.set_yticklabels(icc.node)
c0.set_xlabel('handler intraclass correlation (ordinal mixed model, 170 dogs / 117 handlers)')
c0.set_title('12 of the 20 retained descriptors carry\n>10% between-handler variance', loc='left')
c0.text(0.104, 1.0, 'ICC = 0.10', fontsize=7, color='0.35')
c0.text(0.233, 19.1, 'FDA, GWL: removed by the\ncorrected screening test', fontsize=7, color='#B2182B', ha='right', va='top')
panel_letter(c0, 'a')

c1 = ax4[1]
c1.plot([1e-4, 1], [1e-4, 1], color='0.75', lw=0.9)
rm = S2.removed_by_authors.values
c1.plot(S2.p_rep[rm], S2.p_boundary[rm], 'o', ms=5, color='0.55', label='removed by the authors (8)')
keep = ~rm & (S2.p_boundary < .05)
c1.plot(S2.p_rep[~rm & ~keep], S2.p_boundary[~rm & ~keep], 'o', ms=5, color='#2166AC', label='retained, still retained (19)')
c1.plot(S2.p_rep[keep], S2.p_boundary[keep], 'o', ms=7, color='#B2182B', label='retained, but should not be (2)')
for _, r in S2[keep].iterrows():
    c1.annotate(r.desc, (r.p_rep, r.p_boundary), textcoords='offset points', xytext=(7,-2), fontsize=7.5, color='#B2182B')
c1.axhline(0.05, color='0.35', lw=0.9, ls='--'); c1.axvline(0.05, color='0.35', lw=0.9, ls='--')
c1.set_xscale('log'); c1.set_yscale('log')
c1.set_xlim(2e-6, 1.6); c1.set_ylim(1e-6, 1.6)
…[+489 chars]


# ------------------------ cell 52 ------------------------

c0.texts[-1].remove()
c0.text(0.232, 6.5, 'FDA and GWL are removed\nby the corrected test (panel b)',
        fontsize=7.5, color='#B2182B', ha='right', va='center')
c1.set_ylim(3e-4, 2.0); c1.set_xlim(3e-4, 2.0)
c1.set_xticks([1e-3,1e-2,1e-1,1]); c1.set_xticklabels(['0.001','0.01','0.1','1'])
c1.set_yticks([1e-3,1e-2,1e-1,1]); c1.set_yticklabels(['0.001','0.01','0.1','1'])
fig4.savefig("fig_goold_handler_dependence.png", dpi=300, bbox_inches='tight')
print([x for x in audit_figure(fig4)])


# ------------------------ cell 53 ------------------------

for t in list(c0.texts):
    t.remove()
c0.text(0.104, 1.2, 'ICC = 0.10', fontsize=7, color='0.35')
c0.text(0.232, 6.5, 'FDA and GWL are removed\nby the corrected test (panel b)',
        fontsize=7.5, color='#B2182B', ha='right', va='center')
panel_letter(c0, 'a')
fig4.savefig("fig_goold_handler_dependence.png", dpi=300, bbox_inches='tight')
print([x for x in audit_figure(fig4)])


# ------------------------ cell 54 ------------------------

rows = [
dict(id="C1", claim="Abstract: networks of conditional independence relationships 'varied between dog types'",
  location="Abstract; §3.1-3.2", design="cross-sectional survey; 116 patrol vs 54 detection dogs, 20 ordinal descriptors, 2 separate GGMs",
  test_used="none (visual contrast of two separately fitted networks)",
  test_indicated="permutation test of between-group difference, handler-level label shuffle",
  reported_p="none", recomputed_p="0.666 (omnibus structure); 0.168 (mean |r|); 0/190 pairs after BH or max-stat FWER",
  effect="SS of polychoric differences 8.41 vs permutation median 9.21; mean |r| +0.090 (detection − patrol), null SD 0.063",
  verdict="Mis-specified", severity="A"),
dict(id="C2", claim="Abstract: 'Bootstrap analyses revealed the stability of network results'",
  location="Abstract; §3.3", design="resampling of dogs within each network",
  test_used="non-parametric bootstrap (nBoot=2000), node-wise and subject-wise bootstrap; no formal criterion",
  test_indicated="edge-inclusion and centrality stability at the sampled unit, reported per network",
  reported_p="none", recomputed_p="n/a",
  effect="patrol: 48/55 published edges present in >=50% of 80% subsamples (median inclusion 0.95); detection: 0/70 (median 0.08), 907/1000 subsamples return an empty network",
  verdict="Contradicted", severity="A"),
dict(id="C3", claim="Abstract: 'The most central descriptors denoted desirable characteristics in both patrol and detection dog networks'",
  location="Abstract; §3.2", design="20 nodes (14 desirable, 6 undesirable) within each fitted network",
  test_used="none (descriptive)", test_indicated="none available: nodes of one network are not independent units",
  reported_p="none", recomputed_p="not testable",
  effect="probability of superiority (desirable > undesirable): patrol 0.84 betweenness / 0.89 strength; detection 0.63 / 0.80",
  verdict="Supported, overstated", severity="C"),
dict(id="C4", claim="Abstract: 'Playful' is widely…[+12508 chars]


# ------------------------ cell 57 ------------------------

a = host.artifacts(limit=50)
for r in a['artifacts']:
    print(r['filename'], r['latest_version_id'])


# ------------------------ cell 58 ------------------------

import pandas as pd, re
txt = open("review_goold.md", encoding="utf-8").read()
print("bytes:", len(txt.encode()), "| sections:", re.findall(r'^## .*', txt, re.M))
print("figure markers:", re.findall(r'\{\{artifact:([0-9a-f-]+)\}\}', txt))
print("ends with:", repr(txt[-180:]))
cl = pd.read_csv("claims_goold.csv")
print("\nclaims:", len(cl), "| columns:", list(cl.columns))
print(cl.groupby(['verdict','severity']).size().to_string())
# table rows in the markdown verdict table
rows = [l for l in txt.split("\n") if l.startswith("| C")]
print("\nverdict-table rows:", len(rows), "| ids:", [l.split("|")[1].strip() for l in rows])


# ------------------------ cell 59 ------------------------

import json, os
os.makedirs("handoff", exist_ok=True)
cols = ['id','claim','design','test_used','test_indicated','reported_p','recomputed_p','effect','verdict','severity']
claims = cl[cols].where(pd.notnull(cl[cols]), "").to_dict('records')
out = {
 "paper": "Goold C, Vas J, Olsen C, Newberry RC (2016). Using network analysis to study behavioural phenotypes: an example using domestic dogs. Royal Society Open Science 3:160268.",
 "doi": "10.1098/rsos.160268",
 "n_claims": len(claims),
 "claims": claims,
 "headline_findings": [
  "The paper contains no inferential comparison between the patrol and detection networks. The 95% intervals on Cliff's delta in figure 3 are Monte-Carlo error, not sampling uncertainty: their half-width is 1.60/sqrt(n_boot), measured at 0.0357 for n_boot=2000 against the published mean of 0.0350, so 18 of 20 intervals exclude zero including 9 of the 11 descriptors the paper itself calls negligible. Supplying the missing reference distribution by permuting dog type at the handler level (2000 permutations) gives p=0.666 for the overall difference in correlation structure, p=0.168 for the difference in mean association strength, and 0 of 190 descriptor pairs surviving Benjamini-Hochberg (min q=0.475) or a max-statistic family-wise correction (min p=0.692).",
  "The detection-dog network is not estimable at n=54 under the chosen settings. In 1000 subsamples retaining 80% of detection dogs, 907 returned a completely empty graph and not one of the 70 published edges reappeared in half of the subsamples (median inclusion 0.08). The patrol network under the identical procedure gives median 56 edges, zero empty graphs, and 48 of 55 published edges recovered in at least half of subsamples (median inclusion 0.95). The abstract's 'bootstrap analyses revealed the stability of network results' is therefore true of the patrol network and contradicted for the detection one.",
  "One discussion claim reverses on the authors' own deposited matrices: aggression …[+2916 chars]


# ------------------------ cell 61 ------------------------

print(host.submit_output(
    out,
    completion_bullets=[
        "Reproduced both published GGMs exactly from the Dryad deposit (55/70 edges, identical edge sets)",
        "Built a 21-claim register and supplied the missing between-network permutation test (p=0.666)",
        "Showed figure 3's intervals are Monte-Carlo error scaling as 1.60/sqrt(n_boot)",
        "Delivered review_goold.md, claims_goold.csv and four figures"
    ],
    deviations=[
        "Data source substituted: the Dryad deposit (doi:10.5061/dryad.81k11) was read from the Zenodo mirror of record 4967251, which carries every file named in the Data Accessibility statement.",
        "The authors' with-replacement bootstrap is not reproducible here (bootnet 0.3 will not install against qgraph 1.10.1; bootTable*.csv not deposited), so published Cliff's deltas were not re-derived and claim C13 is marked Not assessable; see the Limitations section of review_goold.md.",
        "All stability re-analysis substitutes 80%-subsampling without replacement (1000 draws per network) for the authors' with-replacement bootstrap; the two are not numerically comparable.",
        "Permutation counts are below the 10,000 ideal for intervals: 2000 (structure, strength), 1000 (matched-n reference), 400 (label-permutation edge counts); no p below 1/2001, 1/1001 or 1/401 respectively is claimed.",
        "In the handler-level permutation null each handler was assigned one dog type by majority, affecting 1 of 117 handlers."
    ]))
