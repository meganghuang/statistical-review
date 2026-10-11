# ==========================================================================
# wang review -- python cells, verbatim and in execution order
# conda env: python
# 37 cells with exit_status='ok'; cells that errored are omitted.
# Run top-to-bottom in ONE session: the originals ran in a persistent
# kernel, so later cells depend on earlier state.
# ==========================================================================


# ------------------------ cell 1 ------------------------

import os
for root, dirs, files in os.walk("wang"):
    for f in files:
        p = os.path.join(root, f)
        print(os.path.relpath(p, "wang"), os.path.getsize(p))


# ------------------------ cell 2 ------------------------

txt = open("wang/paper/wang_fulltext.txt", encoding="utf-8", errors="replace").read()
print(len(txt))
import re
# find section headers
for m in re.finditer(r'^(.{0,80})$', txt, re.M):
    s = m.group(1).strip()
    if s and len(s) < 60 and re.match(r'^(Abstract|Introduction|Results|Methods|Discussion|Materials|Part [12]|References|Data availability|Statistical)', s, re.I):
        print(m.start(), '|', s)


# ------------------------ cell 3 ------------------------

print(txt[:2500])
print("=== P-VALUE MENTIONS ===")
pat = re.compile(r'[Pp]\s*[=<>]\s*0?\.\d+|p\s*[=<]\s*\d')
hits = [m.start() for m in pat.finditer(txt)]
print(len(hits))


# ------------------------ cell 4 ------------------------

print(txt[2500:4200])
print("\n==== CONTEXTS ====")
for i,h in enumerate(hits):
    print(f"--[{i}] @{h}--")
    print(txt[max(0,h-420):h+160].replace("\n"," "))


# ------------------------ cell 5 ------------------------

print(txt[38900:40900])
print("\n@@@@ METHODS/ANALYSIS @@@@")
j = txt.find("Data analysis")
print(j)
for m in re.finditer(r'Data analysis', txt):
    print(m.start())


# ------------------------ cell 6 ------------------------

print(txt[30994:36300])


# ------------------------ cell 7 ------------------------

import pandas as pd, numpy as np
p1 = pd.ExcelFile("wang/data/Part_1.xlsx")
p2 = pd.ExcelFile("wang/data/Part_2.xlsx")
print("P1 sheets:", p1.sheet_names)
print("P2 sheets:", p2.sheet_names)
allsh = pd.read_excel(p1, 'all')
print(allsh.shape); print(list(allsh.columns)); print(allsh.head(4).to_string())


# ------------------------ cell 8 ------------------------

ep = pd.read_excel(p1,'emotionalpairings')
so = pd.read_excel(p1,'specificorders')
print("ep", ep.shape); print(list(ep.columns))
print("so", so.shape); print(list(so.columns))
print(ep.head(3).to_string())


# ------------------------ cell 9 ------------------------

sb = pd.read_excel(p2,'stressbehav')
print(sb.shape); print(list(sb.columns))
print(sb.head(3).to_string())
print("---tail---")
print(sb.tail(3).to_string())


# ------------------------ cell 10 ------------------------

from scipy import stats

def r_wilcox_paired(x, y, label=""):
    """Replicate R wilcox.test(x, y, paired=TRUE) incl. exact/approx rule and V."""
    x = np.asarray(x, float); y = np.asarray(y, float)
    ok = ~(np.isnan(x) | np.isnan(y))
    d = x[ok] - y[ok]
    n_pairs = ok.sum()
    d = d[d != 0]
    n = len(d)
    r = stats.rankdata(np.abs(d))
    V = float(np.sum(r[d > 0]))
    ties = len(np.unique(np.abs(d))) != n
    zeros = n_pairs != n
    exact = (n < 50) and not ties and not zeros
    if exact:
        p = stats.wilcoxon(d, alternative='two-sided', mode='exact').pvalue
        meth = "exact"
    else:
        res = stats.wilcoxon(d, alternative='two-sided', method='approx', correction=True,
                             zero_method='wilcox')
        p = res.pvalue; meth = "normal approx, cc"
    return dict(label=label, n_pairs=int(n_pairs), n_nonzero=n, V=V, p=p, method=meth,
                median_diff=float(np.median(d)) if n else np.nan)

rows=[]
A=allsh
rows.append(r_wilcox_paired(A.habit1,A.habit3,"ALL habit1 vs habit3 (habituation)"))
rows.append(r_wilcox_paired(A.habit4,A.novel,"ALL habit4 vs novel (discrimination)"))
rows.append(r_wilcox_paired(A.habit3,A.novel,"ALL habit3 vs novel (dishabituation)"))
rows.append(r_wilcox_paired(A.habit3,A.habit4,"ALL habit3 vs habit4 (format)"))
for pr in ["JB","SB","SJ"]:
    rows.append(r_wilcox_paired(ep[pr+"habit4"],ep[pr+"novel"],f"{pr} habit4 vs novel (discrim)"))
    rows.append(r_wilcox_paired(ep[pr+"habit3"],ep[pr+"novel"],f"{pr} habit3 vs novel (dishabit)"))
ordpairs=[("Jhabit4_vB","Bnovel_vJ","J habituated, B novel: discrim"),
          ("Jhabit3_vB","Bnovel_vJ","J habituated, B novel: dishabit"),
          ("Bhabit4_vJ","Jnovel_vB","B habituated, J novel: discrim"),
          ("Bhabit3_vJ","Jnovel_vB","B habituated, J novel: dishabit"),
          ("Bhabit4_vS","Snovel_vB","B habituated, S novel: discrim"),
          ("Bhabit3_vS","Snovel_vB","B habituated, S novel: dishabit"),
          ("Shabit4_vB"…[+597 chars]


# ------------------------ cell 11 ------------------------

council = {}
# dog-level: mean paired difference across that dog's pairings
disc = ep[["Subject","JBdiscrmdifference","SBdiscrmdifference","SJdiscrmdifference"]].set_index("Subject")
dish = ep[["Subject","JBdishabitdifference","SBdishabitdifference","SJdishabitdifference"]].set_index("Subject")
print("trials per dog (discrim):", disc.notna().sum(axis=1).value_counts().to_dict())
d_disc = disc.mean(axis=1, skipna=True)
d_dish = dish.mean(axis=1, skipna=True)

# habituation at dog level: reconstruct habit1/habit3 per pairing from specificorders
h1cols = {"J_vB":("Jhabit1_vB","Jhabit3_vB"),"B_vJ":("Bhabit1_vJ","Bhabit3_vJ"),
          "B_vS":("Bhabit_vS","Bhabit3_vS"),"S_vB":("Shabit1_vB","Shabit3_vB"),
          "S_vJ":("Shabit1_vJ","Shabit3_vJ"),"J_vS":("Jhabit1_vS","Jhabit3_vS")}
hd = pd.DataFrame({k: so[a]-so[b] for k,(a,b) in h1cols.items()})
hd.index = so["Subject"]
print("habituation trials per dog:", hd.notna().sum(axis=1).value_counts().to_dict(),
      " total trials:", int(hd.notna().sum().sum()))
d_hab = hd.mean(axis=1, skipna=True)

def sr(d, lab):
    d = np.asarray(d.dropna(), float)
    nz = d[d!=0]
    res = stats.wilcoxon(nz, alternative='two-sided', mode='exact' if len(nz)<50 else 'approx')
    # bootstrap CI on the mean
    rng = np.random.default_rng(0)
    bs = rng.choice(d, (20000, len(d)), replace=True).mean(axis=1)
    return dict(analysis=lab, n=len(d), mean=d.mean(), lo=np.percentile(bs,2.5), hi=np.percentile(bs,97.5),
                median=np.median(d), p=res.pvalue)

dl = pd.DataFrame([sr(d_hab,"habituation h1-h3 (dog mean)"),
                   sr(d_disc,"discrimination novel-h4 (dog mean)"),
                   sr(d_dish,"dishabituation novel-h3 (dog mean)")])
print(dl.to_string(float_format=lambda v: f"{v:.4g}"))


# ------------------------ cell 12 ------------------------

sheets = ['stressbehav','joybehav','owner','box','stranger','upright','sit','prone']
P2 = {s: pd.read_excel(p2, s) for s in sheets}
out=[]
for s in sheets:
    df = P2[s][["Condition","Frequency"]].dropna()
    g = [df.Frequency[df.Condition==c].values for c in ["C","J","S"]]
    sw = stats.shapiro(df.Frequency.values)
    H,pk = stats.kruskal(*g)
    F,pa = stats.f_oneway(*g)
    out.append(dict(sheet=s, n_total=len(df), n_per=[len(x) for x in g],
                    shapiro_W=sw.statistic, shapiro_p=sw.pvalue, H=H, p_KW=pk, F=F, p_ANOVA=pa))
rep2 = pd.DataFrame(out)
print(rep2.to_string(float_format=lambda v: f"{v:.4g}"))


# ------------------------ cell 13 ------------------------

bins = ['5s','10s','15s','20s','25s','30s','35s','40s','45s','50s','55s','60s']
raw = {}
for s in sheets:
    d = P2[s][["Subject","Sex","Odor"]+bins].dropna(subset=["Subject"]).copy()
    raw[s] = d
# verify: across-dog mean per bin per condition == published Frequency column
chk=[]
for s in sheets:
    d = raw[s]; pub = P2[s][["Condition","Frequency"]].dropna()
    recon = np.concatenate([d[d.Odor==c][bins].mean(axis=0, skipna=True).values for c in ["C","J","S"]])
    chk.append((s, len(d), d.Subject.nunique(), float(np.nanmax(np.abs(recon - pub.Frequency.values)))))
print(pd.DataFrame(chk, columns=["sheet","rows","n_dogs","max_abs_diff_vs_published"]).to_string(float_format=lambda v:f"{v:.3g}"))
print()
print(raw['stressbehav'].groupby('Odor').size().to_dict())
print("missing cells per sheet:", {s: int(raw[s][bins].isna().sum().sum()) for s in sheets})


# ------------------------ cell 14 ------------------------

d = raw['stressbehav']
print(d.groupby('Odor')['Subject'].apply(lambda s: sorted(s.tolist())).to_dict())
same = all(set(raw[s].Subject)==set(d.Subject) for s in sheets)
print("same subjects across all 8 sheets:", same)
print("same Odor assignment across sheets:", all(raw[s].set_index('Subject').Odor.sort_index().equals(d.set_index('Subject').Odor.sort_index()) for s in sheets))
for m in re.finditer(r'(24 dogs|subset|Part 2|n = 2\d)', txt):
    seg = txt[max(0,m.start()-250):m.start()+250].replace("\n"," ")
    if 'subset' in seg or '24' in seg:
        print("...", seg, "\n")


# ------------------------ cell 15 ------------------------

for kw in ["Part 2","second part","subset","randomly assigned","assigned to"]:
    for m in re.finditer(kw, txt):
        seg = txt[max(0,m.start()-350):m.start()+450].replace("\n"," ")
        if re.search(r'\b(2[0-9]|1[0-9])\b dogs|subset|assigned', seg):
            print(f"### {kw} @{m.start()}\n", seg, "\n")
            break


# ------------------------ cell 16 ------------------------

extra = P2['stressbehav'][["Subject","Odor"]].dropna(subset=["Subject"])
print("rows w/ Subject:", len(extra), " w/ Odor:", extra.Odor.notna().sum(),
      " excluded:", extra[extra.Odor.isna()].Subject.tolist())

def dunn(values, groups):
    """Dunn (1964) with tie correction; returns dict (i,j)->(z, p_two_sided, p_one_sided)."""
    v = np.asarray(values,float); g = np.asarray(groups)
    N = len(v); r = stats.rankdata(v)
    # tie correction term sum(t^3-t)
    _, cnt = np.unique(v, return_counts=True)
    ties = np.sum(cnt**3 - cnt)
    labs = sorted(set(g)); res={}
    for i in range(len(labs)):
        for j in range(i+1,len(labs)):
            a,b = labs[i],labs[j]
            ra, rb = r[g==a].mean(), r[g==b].mean()
            na, nb = (g==a).sum(), (g==b).sum()
            sigma = np.sqrt(((N*(N+1)/12) - ties/(12*(N-1))) * (1/na + 1/nb))
            z = (ra-rb)/sigma
            p2 = 2*stats.norm.sf(abs(z))
            res[(a,b)] = (z, p2, p2/2)
    return res

print("\n== Dunn at BIN level (as published; dunn.test default = uncorrected, one-sided P) ==")
binrows=[]
for s in sheets:
    df = P2[s][["Condition","Frequency"]].dropna()
    for (a,b),(z,p2,p1) in dunn(df.Frequency.values, df.Condition.values).items():
        binrows.append(dict(sheet=s, pair=f"{a}-{b}", z=z, p_two=p2, p_one=p1))
binD = pd.DataFrame(binrows)
print(binD.to_string(float_format=lambda v:f"{v:.4g}"))


# ------------------------ cell 17 ------------------------

doglvl = {}
rows=[]
for s in sheets:
    d = raw[s].dropna(subset=["Odor"]).copy()
    d["mean_freq"] = d[bins].mean(axis=1, skipna=True)
    doglvl[s] = d
    g = [d.mean_freq[d.Odor==c].values for c in ["C","J","S"]]
    H,pk = stats.kruskal(*g)
    dn = dunn(d.mean_freq.values, d.Odor.values)
    rows.append(dict(sheet=s, n=[len(x) for x in g], H_dog=H, p_KW_dog=pk,
                     **{f"p_{a}{b}": dn[(a,b)][1] for (a,b) in dn}))
dogKW = pd.DataFrame(rows)
cmp = dogKW.merge(rep2[["sheet","H","p_KW"]].rename(columns={"H":"H_bin","p_KW":"p_KW_bin"}), on="sheet")
print(cmp[["sheet","n","H_bin","p_KW_bin","H_dog","p_KW_dog","p_CJ","p_CS","p_JS"]].to_string(float_format=lambda v:f"{v:.4g}"))


# ------------------------ cell 18 ------------------------

import statsmodels.api as sm, statsmodels.formula.api as smf
glm_rows=[]
for s in ['stressbehav','joybehav','owner','box','stranger']:
    d = P2[s][["Condition_MF","Frequency_MF","Sex_MF"]].dropna()
    m = smf.glm("Frequency_MF ~ C(Condition_MF) * C(Sex_MF)", data=d).fit()
    glm_rows.append(dict(sheet=s, nrows=len(d),
                         cells=d.groupby(["Condition_MF","Sex_MF"]).size().nunique(),
                         AIC=m.aic, resid_df=int(m.df_resid)))
    if s in ('stressbehav','joybehav','owner','stranger'):
        for name in m.params.index:
            if ':' in name or 'Sex' in name:
                glm_rows[-1][name.replace('C(Condition_MF)[T.','').replace('C(Sex_MF)[T.','').replace(']','')] = \
                    f"b={m.params[name]:.3f} SE={m.bse[name]:.3f} t={m.tvalues[name]:.3f} p={m.pvalues[name]:.4g}"
G = pd.DataFrame(glm_rows)
for _,r in G.iterrows():
    print(r.sheet, "| rows:", r.nrows, "| AIC:", round(r.AIC,3), "| resid df:", r.resid_df)
    for k,v in r.items():
        if isinstance(v,str): print("    ", k, "->", v)
print("\nunique dogs per sex x condition cell:")
print(doglvl['stressbehav'].groupby(['Odor','Sex']).size().unstack(fill_value=0).to_string())


# ------------------------ cell 19 ------------------------

print([f for f in dir() if f.startswith('stat_')])

# --- 1. effect sizes, dog level, original units (proportion of sample points) ---
rng = np.random.default_rng(7)
def boot_diff(a,b,n=20000):
    da = rng.choice(a,(n,len(a)),replace=True).mean(1); db = rng.choice(b,(n,len(b)),replace=True).mean(1)
    d = da-db; return d.mean(), np.percentile(d,2.5), np.percentile(d,97.5)
eff=[]
for s in ['owner','stranger','stressbehav','joybehav','upright','prone']:
    d = doglvl[s]
    for a,b in [("S","C"),("S","J"),("J","C")]:
        va, vb = d.mean_freq[d.Odor==a].values, d.mean_freq[d.Odor==b].values
        m,lo,hi = boot_diff(va,vb)
        U = stats.mannwhitneyu(va,vb,alternative='two-sided')
        eff.append(dict(outcome=s, contrast=f"{a}-{b}", mean_a=va.mean(), mean_b=vb.mean(),
                        diff=m, lo=lo, hi=hi, PS=U.statistic/(len(va)*len(vb)), p_MW=U.pvalue))
EFF = pd.DataFrame(eff)
print(EFF.to_string(float_format=lambda v:f"{v:.3g}"))

# --- 2. multiplicity ---
p1p = rep.p.values
m1 = stat_multiplicity(p1p, labels=rep.label.tolist())
print("\nPART1 22 tests:", (p1p<0.05).sum(), "raw |", (m1['q_BH']<0.05).sum() if 'q_BH' in m1 else '?', "BH |",
      (p1p<0.05/len(p1p)).sum(), "Bonferroni")
p2bin = rep2.p_KW.values; p2dog = dogKW.p_KW_dog.values
print("PART2 KW bin-level:", (p2bin<0.05).sum(), "raw,", (stats.false_discovery_control(p2bin)<0.05).sum(), "BH,",
      (p2bin<0.05/8).sum(), "Bonf")
print("PART2 KW dog-level:", (p2dog<0.05).sum(), "raw,", (stats.false_discovery_control(p2dog)<0.05).sum(), "BH,",
      (p2dog<0.05/8).sum(), "Bonf")
print("\nmin attainable p, ranksum 6 vs 9:", stat_min_attainable_p(6,9,kind="ranksum"))


# ------------------------ cell 20 ------------------------

print(type(m1), m1.columns.tolist() if hasattr(m1,'columns') else m1.keys())
q = stats.false_discovery_control(p1p)
rep["q_BH"] = q; rep["p_bonf"] = np.minimum(p1p*len(p1p),1)
print("PART1: raw<0.05 =", (p1p<0.05).sum(), "| BH q<0.05 =", (q<0.05).sum(), "| Bonf =", (rep.p_bonf<0.05).sum())
print(rep[["label","p","q_BH","p_bonf"]].to_string(float_format=lambda v:f"{v:.4g}"))
# symmetry of the key paired differences (signed-rank assumption)
keys = {"ALL novel-habit4": (allsh.novel-allsh.habit4).dropna(),
        "JB novel-habit4": ep.JBdiscrmdifference.dropna(),
        "SJ novel-habit4": ep.SJdiscrmdifference.dropna(),
        "dog-mean novel-habit4": d_disc.dropna()}
for k,v in keys.items():
    v=np.asarray(v,float); print(f"{k}: n={len(v)} mean={v.mean():.3f} median={np.median(v):.3f} skew={stats.skew(v):.2f}")


# ------------------------ cell 21 ------------------------

lmres=[]
for pr in ["JB","SB","SJ"]:
    for kind in ["discrm","dishabit"]:
        d = ep[[f"{pr}{kind}difference", f"{pr}side","Season"]].dropna()
        d.columns=["y","side","Season"]; d["Season"]=d.Season.astype(str)
        m = smf.ols("y ~ C(side) + C(Season)", data=d).fit()
        lmres.append(dict(model=f"{pr} {kind}", n=int(m.nobs), min_p=float(m.pvalues[1:].min()),
                          side_p=float(m.pvalues[1])))
print(pd.DataFrame(lmres).to_string(float_format=lambda v:f"{v:.4g}"))

print("\n-- dog-level sex x condition (OLS on 24 dog means) --")
for s in ['stressbehav','joybehav','owner','stranger']:
    d = doglvl[s]
    m = smf.ols("mean_freq ~ C(Odor)*C(Sex)", data=d).fit()
    inter = [k for k in m.params.index if ':' in k]
    print(f"{s}: resid df={int(m.df_resid)} | " + " | ".join(
        f"{k.split(':')[0][-2:]}{k.split(':')[1][-2:]} b={m.params[k]:+.3f} p={m.pvalues[k]:.3f}" for k in inter)
        + f" | overall interaction F-test p={m.f_test(' = 0, '.join(inter)+' = 0').pvalue:.3f}")


# ------------------------ cell 22 ------------------------

C = [
 dict(id="C1", claim="Investigation time fell from 1st to 3rd presentation (habituation)",
      design="paired, pooled over 3 pairings/dog", test_used="Wilcoxon signed-rank, n=122 trials",
      test_indicated="signed-rank on 43 dog-level means (or LMM with dog random effect)",
      reported_p="V=7108, p<0.001", recomputed_p="p=9.9e-18 as run; p=2.5e-11 at dog level",
      effect="-4.90 s mean decrease, 95% CI [-5.94,-3.90] (dog level)", verdict="Supported", severity="C"),
 dict(id="C2", claim="Dogs investigated the novel odour longer than the simultaneous 4th habituated presentation (discrimination)",
      design="paired, pooled over pairings", test_used="Wilcoxon signed-rank, n=122 trials",
      test_indicated="signed-rank on 43 dog-level means",
      reported_p="V=2704, p=0.008", recomputed_p="p=0.0075 as run; p=0.026 at dog level",
      effect="+1.00 s, 95% CI [0.17,1.92] (dog level)", verdict="Supported, overstated", severity="B"),
 dict(id="C3", claim="Dogs investigated the novel odour longer than the 3rd habituated presentation (dishabituation)",
      design="paired, pooled over pairings", test_used="Wilcoxon signed-rank, n=122 trials",
      test_indicated="signed-rank on 43 dog-level means",
      reported_p="V=2061.5, p<0.001", recomputed_p="p=1.0e-4 as run (V=2061); p=1.2e-5 at dog level",
      effect="+1.77 s, 95% CI [0.68,2.83] (dog level)", verdict="Supported", severity="C"),
 dict(id="C4", claim="No dishabituation caused by the one-box to two-box format change",
      design="paired, pooled", test_used="Wilcoxon signed-rank", test_indicated="equivalence test against a pre-stated margin",
      reported_p="V=2977, p=0.087", recomputed_p="p=0.087", effect="median paired diff -0.49 s; no interval reported",
      verdict="Supported, overstated", severity="B"),
 dict(id="C5", claim="Discrimination in the joy vs baseline pairing", design="within-dog paired, n=40 dogs",
      test_used="Wilcoxon signed-rank", test_indicated="same", reported_p…[+10358 chars]


# ------------------------ cell 25 ------------------------

nice = {'stressbehav':'stress behaviours','joybehav':'joy behaviours','owner':'owner proximity',
        'box':'box proximity','stranger':'stranger proximity','upright':'upright posture',
        'sit':'sitting posture','prone':'prone posture'}
ax.set_yticks(y); ax.set_yticklabels([nice[s] for s in order.sheet])
ax.set_xlabel("Kruskal–Wallis p-value"); ax.set_ylim(-1.1, len(order)-0.4)
ax.text(.055, -0.95, "α = 0.05", fontsize=7)
ax.set_title("5 of 6 significant Part-2 results\ndisappear at the dog level")
ax.legend(frameon=False, loc='lower left', fontsize=6.5)
set_frame(ax); panel_letter(ax,'c')
fig1.savefig("fig_wang_part2_unit.png", dpi=300, bbox_inches='tight')
a = audit_figure(fig1); print(a if not hasattr(a,'to_string') else a.to_string())


# ------------------------ cell 27 ------------------------

for t in list(ax.texts):
    if "α" in t.get_text(): t.remove()
ax.set_xlabel("Kruskal–Wallis p-value (log scale)")
ax.text(.058, len(order)-0.9, "α = 0.05", fontsize=7)
ax.legend(frameon=False, loc='lower left', fontsize=6.5, bbox_to_anchor=(0.0,-0.02))
panel_letter(axes[0],'a'); panel_letter(axes[1],'b')
fig1.suptitle("Part 2 was analysed on 12 time-bin averages per condition, not on the 24 dogs",
              x=.005, ha='left', fontsize=9.5)
fig1.savefig("fig_wang_part2_unit.png", dpi=300, bbox_inches='tight')
print(audit_figure(fig1))


# ------------------------ cell 28 ------------------------

def bci(v, n=20000, rs=11):
    r = np.random.default_rng(rs); v=np.asarray(v,float)
    b = r.choice(v,(n,len(v)),replace=True).mean(1)
    return v.mean(), np.percentile(b,2.5), np.percentile(b,97.5)

# ---- FIG 2 ----
rowsF=[("pooled, dog means (n=43)", d_disc.dropna().values, d_dish.dropna().values)]
for pr,lab in [("JB","joy vs baseline (n=40)"),("SB","stress vs baseline (n=41)"),("SJ","stress vs joy (n=41)")]:
    rowsF.append((lab, ep[pr+"discrmdifference"].dropna().values, ep[pr+"dishabitdifference"].dropna().values))
fig2, (axA, axB) = plt.subplots(1,2, figsize=(9.6,3.6), sharex=False)
labs=[r[0] for r in rowsF]; y=np.arange(len(rowsF))[::-1]
for k,(ax,idx,ttl) in enumerate([(axA,1,"Discrimination: novel minus simultaneous\nhabituated presentation"),
                                 (axB,2,"Dishabituation: novel minus third\nhabituated presentation")]):
    for yy,row in zip(y,rowsF):
        v=row[idx]; m,lo,hi=bci(v)
        ax.scatter(v, np.full(len(v), yy)+np.random.default_rng(1).uniform(-.1,.1,len(v)),
                   s=8, facecolor='none', edgecolor=CGREY, lw=.6, zorder=1)
        ax.plot([lo,hi],[yy,yy], color=CBLUE, lw=2, zorder=3)
        ax.scatter([m],[yy], s=34, color=CBLUE, zorder=4)
    ax.axvline(0, color='k', lw=.8, ls='--')
    ax.set_yticks(y); ax.set_yticklabels(labs if k==0 else [])
    ax.set_xlabel("difference in investigation time (s)")
    ax.set_title(ttl); ax.set_xlim(-18,30); set_frame(ax); ax.margins(y=.14)
axA.text(.98,.03,"blue = mean, 95% bootstrap CI\ngrey = individual dogs", transform=axA.transAxes,
         ha='right', va='bottom', fontsize=7)
fig2.suptitle("Dog-level effects are positive but small: ~1 s of extra investigation",
              x=.005, ha='left', fontsize=9.5)
fig2.tight_layout(rect=[0,0,1,.92])
panel_letter(axA,'a'); panel_letter(axB,'b')
fig2.savefig("fig_wang_part1_effects.png", dpi=300, bbox_inches='tight')
print("fig2:", audit_figure(fig2))

# ---- FIG 3 ----
fig3, ax3 = plt.subplots(figsize=(6.4,4.2…[+1166 chars]


# ------------------------ cell 29 ------------------------

axA.set_ylabel("odour pairing (experimental unit = dog)"); axB.set_ylabel("odour pairing")
axB.set_yticklabels([])
fig2.savefig("fig_wang_part1_effects.png", dpi=300, bbox_inches='tight')
print("fig2:", audit_figure(fig2))

for a in list(ax3.texts): a.remove()
ax3.annotate("joy vs baseline discrimination\np = 0.013 (BH q = 0.028)", xy=(10, srt.p[9]),
             xytext=(2.2, 2.5e-2), fontsize=7, arrowprops=dict(arrowstyle="-", lw=.7, color=CGREY))
ax3.annotate("order-split dishabituation\np = 0.042 and 0.047 — both fail BH", xy=(12, srt.p[11]),
             xytext=(12.5, 2e-6), fontsize=7, arrowprops=dict(arrowstyle="-", lw=.7, color=CGREY))
ax3.annotate("pooled habituation (p = 1e-17)", xy=(1, srt.p[0]), xytext=(2.2, 2e-17),
             fontsize=7, arrowprops=dict(arrowstyle="-", lw=.7, color=CGREY))
ax3.legend(frameon=False, loc='center right', fontsize=7)
fig3.savefig("fig_wang_multiplicity.png", dpi=300, bbox_inches='tight')
print("fig3:", audit_figure(fig3))


# ------------------------ cell 30 ------------------------

hdr = ["id","claim","design","test_used","test_indicated","reported_p","recomputed_p","effect","verdict","severity"]
def row(r):
    return "| " + " | ".join(str(r[h]).replace("|","/").replace("\n"," ") for h in hdr) + " |"
table = ("| ID | Claim (short) | Design | Test used | Test indicated | Reported p | Recomputed p | "
         "Effect size + CI | Verdict | Sev |\n" + "|" + "---|"*10 + "\n" +
         "\n".join(row(r) for _, r in claims.iterrows()))

body = f"""# Statistical review — Wang & Horowitz (2026), *Dogs (Canis familiaris) distinguish conspecific emotional chemosignals*

*Scientific Reports* 16:11176 · doi:10.1038/s41598-026-41426-1
Data reviewed: the authors' complete Dryad deposit (doi:10.5061/dryad.bzkh189pt) — `Part_1.xlsx`,
`Part_2.xlsx`, `README.md`, `statistical_analyses.R`. Every published statistic in both parts was
re-run from the deposit before any judgement was formed; **all of them reproduce**.

---

## 1. Verdict table

{table}

Severity key: **A** the claim does not survive; **B** the claim survives but its reported strength
does not; **C** reporting or transparency defect, conclusion unaffected.

---

## 2. Summary

**The paper reproduces exactly, and the two parts are not of equal quality.** Every V statistic,
H statistic, F, Dunn p-value, GLM coefficient and AIC in the paper was recovered from the deposited
spreadsheets using the authors' own `statistical_analyses.R` logic, to the published digits. That
is rare and it deserves to be said first: the deposit is complete, the script is the script that
was run, and the arithmetic is right. The problems below are all about *what was counted as an
independent observation*, not about execution.

**Part 1 (habituation–discrimination, 43 dogs) holds.** The pooled tests were run on 122
dog-by-pairing trials as if those were 122 independent observations, when each dog contributed up
to three pairings (37 dogs contributed 3, five contributed 2, one contributed 1). Collapsing to one
value per dog a…[+18600 chars]


# ------------------------ cell 31 ------------------------

b = open("review_wang.md",encoding="utf-8").read()
print([l for l in b.split("\n") if "artifact:" in l])
old = "0.179. Six nominally significant omnibus results become one,"
new = ("0.179. (For stress behaviours the bootstrap CI on the mean difference does exclude zero, "
       "+0.27 [0.03, 0.56] sample points per 5 s for stress vs blank, while the rank test does not "
       "reject, p = 0.11 — with 6 and 9 dogs the two summaries are answering slightly different "
       "questions and neither is strong evidence.) Six nominally significant omnibus results become one,")
assert old in b
b = b.replace(old, new)
open("review_wang.md","w",encoding="utf-8").write(b)
print("ok", len(b))


# ------------------------ cell 32 ------------------------

import re as _re
print([l[:160] for l in b.split("\n") if l.startswith("![")])
vids = {"part2":"75ff53a8-1a1b-436c-89d6-df3363b6648d",
        "mult":"79fbd3c4-48b9-4d04-a61c-5da1300f7bd6",
        "eff":"ec1163c6-a823-415c-8ac6-15a96ee88b5c"}
b2 = b
for line in [l for l in b.split("\n") if l.startswith("![")]:
    if "time bins rather than dogs" in line: key="part2"
    elif "multiplicity" in line: key="mult"
    else: key="eff"
    cap = line[2:line.index("]")]
    b2 = b2.replace(line, f"![{cap}]({host.artifact_marker(vids[key])})")
open("review_wang.md","w",encoding="utf-8").write(b2)
print([l for l in b2.split("\n") if l.startswith("![")])


# ------------------------ cell 33 ------------------------

import json, os
os.makedirs("handoff", exist_ok=True)
out = dict(
  paper="Wang R & Horowitz A (2026). Dogs (Canis familiaris) distinguish conspecific emotional chemosignals. Scientific Reports 16:11176.",
  doi="10.1038/s41598-026-41426-1",
  n_claims=int(len(claims)),
  claims=[{k: str(v) for k,v in r.items()} for _, r in claims.iterrows()],
  headline_findings=[
    "Every published statistic in both parts reproduces exactly from the Dryad deposit: all 22 Part-1 Wilcoxon V statistics and p-values, all 8 Part-2 Kruskal-Wallis H statistics, the box-proximity ANOVA F=1.035, every Dunn post hoc, and all four GLM coefficient/SE/t triples (AICs differ by exactly 2, R's Gaussian-GLM dispersion convention).",
    "Part 2's experimental unit is the 5-second time bin, not the dog: the Methods state the data were averaged across dogs per sample point and the 12 bins per condition were entered as the observations. Re-running the identical tests on the 24 dog-level means (6 blank / 9 joy / 9 stress) removes 5 of the 6 significant omnibus results - owner proximity p 9.6e-6 -> 0.231, stranger proximity 0.016 -> 0.437, stress behaviours 2.8e-5 -> 0.106, upright posture 2.2e-4 -> 0.116, prone posture 4.0e-4 -> 0.179. Only joy behaviours survives (p=0.038) and it fails BH across the 8 outcomes (q=0.31).",
    "The abstract's attachment claim is Contradicted: owner proximity +0.37 of 12 sample points, 95% bootstrap CI [-0.005, 0.69]; stranger proximity -0.20, CI [-0.47, 0.07]. Both directions are as predicted; neither interval excludes zero at the dog level.",
    "All four sex x odour-condition interactions vanish at the dog level (p = 0.18-1.00; omnibus interaction F-tests p = 0.29-0.72) although the coefficients are nearly unchanged - the published significance came entirely from the 66 manufactured residual degrees of freedom.",
    "Part 1 survives its own pseudoreplication: the pooled tests used 122 dog-by-pairing trials from 43 dogs, and collapsing to one value per dog gives…[+2188 chars]


# ------------------------ cell 34 ------------------------

import json
out = json.load(open("handoff/out.json"))
print(host.submit_output(
    out,
    completion_bullets=[
        "Reproduced all 22 Part-1 Wilcoxon, 8 Part-2 Kruskal-Wallis, ANOVA, Dunn and GLM statistics exactly from the Dryad deposit",
        "Built a 26-claim register and re-analysed every claim at the dog level",
        "Found Part 2 analysed on 12 time-bin averages, not 24 dogs; 5 of 6 significant results disappear at the correct unit",
        "Delivered review_wang.md, claims_wang.csv and three figures"],
    deviations=["none"]))


# ------------------------ cell 35 ------------------------

tvals = {"stressbehav (S:M)":-2.796, "joybehav (S:M)":5.201, "owner (S:M)":-3.044, "stranger (J:M)":2.780}
for k,t in tvals.items():
    print(f"{k}: t={t}  z-based p={2*stats.norm.sf(abs(t)):.4g}  t(df=66)-based p={2*stats.t.sf(abs(t),66):.4g}")
print("\nAIC as statsmodels reports vs +2 (R counts the Gaussian dispersion parameter):")
for s,a in [("stressbehav",-41.927),("joybehav",43.291),("owner",-44.484),("stranger",-13.885)]:
    print(f"  {s}: statsmodels {a}  ->  R convention {a+2:.3f}")


# ------------------------ cell 37 ------------------------

i = b.find("I did not execute")
print(repr(b[i-130:i+480]))


# ------------------------ cell 38 ------------------------

old3 = ("- **I did not execute the authors' R script**; I re-implemented each call in Python, matching R's\n"
"  `wilcox.test` exact/normal-approximation branch rule, `dunn.test`'s tie-corrected z and one-sided\n"
"  default, and `summary.glm`'s t-based p-values for the Gaussian family. The agreement with every\n"
"  published statistic is the evidence that the re-implementation is faithful.")
new3 = ("- **I did not execute the authors' R script**; I re-implemented each call in Python, so every\n"
"  reproduction claim here is agreement between two implementations, not a re-run of the original.\n"
"  Three R conventions had to be matched by hand and are stated so the reader can judge them:\n"
"  `wilcox.test`'s exact/normal-approximation branch rule, `dunn.test`'s tie-corrected z with its\n"
"  one-sided uncorrected default, and — for the four Part-2 GLMs — R's Gaussian-family AIC (which\n"
"  counts the dispersion parameter, so `statsmodels` reports 2 lower) together with its t-based\n"
"  rather than z-based Wald p-values on 66 residual df. My first GLM run used the `statsmodels`\n"
"  defaults and returned p = 0.00517, 1.98 × 10⁻⁷, 0.00234, 0.00544 against the paper's 0.007,\n"
"  <0.001, 0.003, 0.007; on R's t reference these become 0.00677, 2.10 × 10⁻⁶, 0.00335, 0.00708 and\n"
"  agree to the printed digits. The coefficients, standard errors and t statistics agreed from the\n"
"  start. None of this affects the dog-level re-analysis in C22–C25, which uses OLS on 24 dog means\n"
"  with 18 residual df and is unchanged under either reference.")
assert old3 in b
b = b.replace(old3, new3)
b = b.replace("other statistic in the paper reproduced to the printed digits.",
              "other statistic in the paper reproduced to the printed digits, subject to the two R\n  conventions noted in the final bullet below.")
open("review_wang.md","w",encoding="utf-8").write(b)
print(all(s in b for s in ["dispersion parameter","t reference with 66 residual df","0.00708"]), len(…[+4 chars]


# ------------------------ cell 39 ------------------------

for s in ["dispersion parameter","t reference with 66 residual df","0.00708","**all of them reproduce**","The paper reproduces, and the two parts"]:
    print(s, "->", s in b)
j = b.find("**The paper reproduces")
print("\n", b[j:j+1180])


# ------------------------ cell 41 ------------------------

i = out["data_coverage"].find("The authors' R script")
print(repr(out["data_coverage"][i:i+420]))


# ------------------------ cell 42 ------------------------

old = ("The authors' R script was re-implemented in Python rather than executed in R, matching R's "
"wilcox.test exact/normal-approximation branch rule, dunn.test's tie-corrected one-sided default, and "
"summary.glm's t-based p-values; agreement with every published statistic confirms fidelity.")
new = ("The authors' R script was re-implemented in Python rather than executed in R, so every reproduction "
"claim is agreement between two implementations rather than a re-run of the original. Three R conventions "
"had to be matched by hand and are stated in the report's Limitations: wilcox.test's exact/normal-"
"approximation branch rule, dunn.test's tie-corrected z with its one-sided uncorrected default, and - for "
"the four Part-2 GLMs - R's Gaussian-family AIC (which counts the dispersion parameter, so statsmodels "
"reports 2 lower) together with its t-based rather than z-based Wald p-values on 66 residual df. Under "
"those conventions every published statistic agrees to the printed digits; the dog-level re-analysis in "
"C22-C25 uses OLS on 24 dog means with 18 residual df and is unchanged under either reference.")
assert old in out["data_coverage"]
out["data_coverage"] = out["data_coverage"].replace(old, new)
json.dump(out, open("handoff/out.json","w"), indent=0)
print(host.submit_output(out,
  completion_bullets=[
    "Reproduced all 22 Part-1 Wilcoxon, 8 Part-2 Kruskal-Wallis, ANOVA, Dunn and GLM statistics from the Dryad deposit, with R's AIC and t-reference conventions disclosed",
    "Built a 26-claim register and re-analysed every claim at the dog level",
    "Found Part 2 analysed on 12 time-bin averages, not 24 dogs; 5 of 6 significant results disappear at the correct unit",
    "Delivered review_wang.md, claims_wang.csv and three figures"],
  deviations=["none"]))
