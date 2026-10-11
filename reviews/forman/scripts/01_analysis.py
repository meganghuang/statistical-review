# ==========================================================================
# forman review -- python cells, verbatim and in execution order
# conda env: python
# 32 cells with exit_status='ok'; cells that errored are omitted.
# Run top-to-bottom in ONE session: the originals ran in a persistent
# kernel, so later cells depend on earlier state.
# ==========================================================================


# ------------------------ cell 1 ------------------------

import os
for root, dirs, files in os.walk('forman'):
    for f in files:
        p = os.path.join(root, f)
        print(f"{os.path.relpath(p,'forman')}  {os.path.getsize(p)}")


# ------------------------ cell 2 ------------------------

import pandas as pd, numpy as np
d = pd.read_csv('forman/data/41598_2023_47409_MOESM3_ESM.csv')
print(d.shape)
for i,c in enumerate(d.columns):
    print(i, repr(c), d[c].dtype, d[c].nunique(dropna=True), d[c].isna().sum())


# ------------------------ cell 3 ------------------------

print(d['ppl_demographics_repeated'].value_counts(dropna=False))
print()
for c in ['current_previous','trained','initiate_fetch','end_fetch','cat_sex','life_stage','general_breed','times_object_retrieved_typical','fetch_recent_range','fetch_monthly_range','multicat_household_time_fetch']:
    print(c, dict(d[c].value_counts(dropna=False)))
print()
print(d[['times_object_retrieved_recent','times_monthly_fetch_sessions','fetch_age_months_total']].describe())


# ------------------------ cell 4 ------------------------

import zipfile, re
def docx_text(p):
    with zipfile.ZipFile(p) as z:
        xml = z.read('word/document.xml').decode('utf8')
    xml = re.sub(r'</w:p>', '\n', xml)
    xml = re.sub(r'<w:tab[^>]*/>', '\t', xml)
    return re.sub(r'<[^>]+>', '', xml)
t2 = docx_text('forman/data/41598_2023_47409_MOESM2_ESM.docx')
print(len(t2))
open('s2_code.txt','w',encoding='utf8').write(t2)
# print only lines mentioning tests
for i,l in enumerate(t2.split('\n')):
    if re.search(r'chisq|kruskal|wilcox|shapiro|levene|pairwise|wilcox_test|chisq_test|identify_outliers|cramer|effsize|dunn', l, re.I):
        print(i, l.strip()[:200])


# ------------------------ cell 5 ------------------------

lines = t2.split('\n')
import html
for i,l in enumerate(lines):
    s = html.unescape(l).strip()
    if re.search(r'kruskal|wilcox|shapiro|levene|outlier|mann|effect|wilcox_test|pairwise', s, re.I):
        print(i, s[:300]); print('---')


# ------------------------ cell 6 ------------------------

import html
code = html.unescape(t2)
pats = ['pairwise.wilcox.test','wilcox_test','wilcox.test','kruskal.test','chisq.test(','leveneTest','CramerV','epsilon','effsize','wilcox_effsize','p.adjust']
for p in pats:
    print(p, '->', code.count(p))
# show the distinct short call signatures
import re
for m in sorted(set(re.findall(r'(?:pairwise\.wilcox\.test|wilcox_test|wilcox\.test|kruskal\.test|leveneTest)\([^\n]{0,160}', code))):
    print('|', m[:170])


# ------------------------ cell 7 ------------------------

import numpy as np, pandas as pd
d['_rep'] = d['ppl_demographics_repeated']
# owner id: new owner whenever _rep is NaN
newowner = d['_rep'].isna().values
owner = np.cumsum(newowner) - 1
d['owner_id'] = owner
sizes = d.groupby('owner_id').size()
print("n_owner_blocks:", len(sizes), " total cats:", sizes.sum())
print("cats per owner:", dict(sizes.value_counts().sort_index()))

# validation 1: demographic signature constant within block?
sig_cols = ['country','ppl_count_household','person_one_age','person_one_gender','person_two_age','person_two_gender','dogs_household','number_dogs_household']
sig = d[sig_cols].astype(str).agg('|'.join, axis=1)
d['_sig'] = sig
mismatch = d.groupby('owner_id')['_sig'].nunique()
print("blocks with >1 distinct owner-demographic signature:", (mismatch>1).sum(), "/", len(mismatch))

# validation 2: for multi-cat blocks, does number_other_fetch_cats_household agree with block size-1?
blk = d.groupby('owner_id').agg(n=('cat_name','size'),
                                other_fetch=('number_other_fetch_cats_household','max'))
m = blk.dropna()
print("\nblock size vs reported #other fetching cats in household (first row of block):")
print(pd.crosstab(m['n'], m['other_fetch']).to_string())


# ------------------------ cell 8 ------------------------

chk = d.groupby('owner_id')['country'].nunique()
print("blocks with >1 country:", (chk>1).sum(), "/", len(chk))
# how often does a flagged row's country match the immediately preceding row?
prev_same = (d['country'].values[1:] == d['country'].values[:-1])
flag = d['_rep'].notna().values[1:]
print("flagged rows matching previous row's country: %d/%d = %.3f" % (prev_same[flag].sum(), flag.sum(), prev_same[flag].mean()))
print("unflagged rows matching previous row's country: %d/%d = %.3f" % (prev_same[~flag].sum(), (~flag).sum(), prev_same[~flag].mean()))
# ppl_count_household within block
chk2 = d.groupby('owner_id')['ppl_count_household'].nunique()
print("blocks with >1 household size:", (chk2>1).sum())
# multicat flag
print("\ncats whose owner block size>1:", (d.groupby('owner_id')['cat_name'].transform('size')>1).sum())
print("rows flagged as repeat entries (ppl_demographics_repeated not NaN):", d['_rep'].notna().sum())


# ------------------------ cell 9 ------------------------

from scipy import stats
import itertools, json

res = {}  # key -> dict

def chisq_gof(counts):
    c = np.asarray(counts, float); e = c.sum()/len(c)
    X2 = ((c-e)**2/e).sum(); df = len(c)-1
    return X2, df, stats.chi2.sf(X2, df)

rows = []
# --- chi-square family
X2,df,p = chisq_gof([617,537]); rows.append(('C2','sex ratio 617M vs 537F','chi2 GOF',X2,df,p,'5.50','0.018'))
ini = d['initiate_fetch'].value_counts()
end = d['end_fetch'].value_counts()
X2,df,p = chisq_gof([ini['Cat'],ini['About equal'],ini['Myself']]); rows.append(('C3','initiator 3-way',  'chi2 GOF',X2,df,p,'124.29','<0.001'))
for lab,a,b,rep in [('C3a','Cat','Myself','115.23'),('C3b','Cat','About equal','44.64'),('C3c','Myself','About equal','17.65')]:
    X2,df,p = chisq_gof([ini[a],ini[b]]); rows.append((lab,f'initiator {a} vs {b}','chi2 GOF',X2,df,p,rep,'<0.001'))
X2,df,p = chisq_gof([end['Cat'],end['About equal'],end['Myself']]); rows.append(('C4','ender 3-way','chi2 GOF',X2,df,p,'329.08','<0.001'))
for lab,a,b,rep,repp in [('C4a','Cat','Myself','197.54','<0.001'),('C4b','Cat','About equal','217.59','<0.001'),('C4c','Myself','About equal','0.60','0.437')]:
    X2,df,p = chisq_gof([end[a],end[b]]); rows.append((lab,f'ender {a} vs {b}','chi2 GOF',X2,df,p,rep,repp))
# sex x initiator / ender (2x3 independence)
for lab,col,rep,repp in [('C9','initiate_fetch','1.82','0.403'),('C10','end_fetch','1.97','0.374')]:
    ct = pd.crosstab(d['cat_sex'], d[col])
    X2,p,dfx,_ = stats.chi2_contingency(ct, correction=False)
    rows.append((lab,f'sex x {col}','chi2 indep',X2,dfx,p,rep,repp))

rep_df = pd.DataFrame(rows, columns=['id','what','test','X2','df','p','reported_X2','reported_p'])
pd.set_option('display.width',200)
print(rep_df.to_string(index=False, float_format=lambda v: f"{v:.4g}"))


# ------------------------ cell 10 ------------------------

def kw(y, g):
    groups = [y[g==lev] for lev in pd.unique(g)]
    H,p = stats.kruskal(*groups)
    k = len(groups); n = len(y)
    eps2 = (H - k + 1)/(n - k)        # epsilon-squared
    return H, k-1, p, eps2

def mw(a,b):
    U,p = stats.mannwhitneyu(a,b,alternative='two-sided',method='asymptotic',use_continuity=True)
    n1,n2 = len(a),len(b)
    ps = U/(n1*n2)                     # P(superiority) of a over b
    rbc = 2*ps-1                       # rank-biserial
    mu = n1*n2/2
    # tie-corrected sd
    allv = np.concatenate([a,b]); N=n1+n2
    _,cnt = np.unique(allv, return_counts=True)
    tie = (cnt**3-cnt).sum()
    sd = np.sqrt(n1*n2/12*((N+1) - tie/(N*(N-1))))
    Z = (U - mu - np.sign(U-mu)*0.5)/sd
    return U,p,ps,rbc,Z

out = []
for lab, ycol, gcol, repH, repp in [
    ('C5','times_object_retrieved_recent','initiate_fetch',13.98,'<0.001'),
    ('C6','times_object_retrieved_recent','end_fetch',110.55,'<0.001'),
    ('C7','times_monthly_fetch_sessions','initiate_fetch',52.95,'<0.001'),
    ('C8','times_monthly_fetch_sessions','end_fetch',62.97,'<0.001')]:
    y = d[ycol].values; g = d[gcol].values
    H,df_,p,eps2 = kw(y,g)
    out.append(dict(id=lab,outcome=ycol,by=gcol,H=H,df=df_,p=p,eps2=eps2,reported_H=repH))
kwdf = pd.DataFrame(out)
print(kwdf.to_string(index=False, float_format=lambda v: f"{v:.5g}"))

# pairwise Wilcoxon, Bonferroni (3 comparisons per family)
pw = []
for lab, ycol, gcol in [('C5','times_object_retrieved_recent','initiate_fetch'),
                        ('C6','times_object_retrieved_recent','end_fetch'),
                        ('C7','times_monthly_fetch_sessions','initiate_fetch'),
                        ('C8','times_monthly_fetch_sessions','end_fetch')]:
    levs = ['Cat','About equal','Myself']
    for a,b in itertools.combinations(levs,2):
        x = d.loc[d[gcol]==a, ycol].values; z = d.loc[d[gcol]==b, ycol].values
        U,p,ps,rbc,Z = mw(x,z)
        pw.append(dict(fam=lab,outcome=ycol,by=gcol,g1=a,g2=b,n1=len(x),n2=le…[+241 chars]


# ------------------------ cell 11 ------------------------

# sex Mann-Whitney (C11, C12) ; R's wilcox.test(y ~ cat_sex) orders Female first
sexres=[]
for lab,ycol,repZ,repp in [('C11','times_object_retrieved_recent','-1.69','0.091'),
                           ('C12','times_monthly_fetch_sessions','-0.49','0.622')]:
    f = d.loc[d['cat_sex']=='Female',ycol].values; m = d.loc[d['cat_sex']=='Male',ycol].values
    U,p,ps,rbc,Z = mw(f,m)
    # Hodges-Lehmann shift + CI via rank inversion (scipy has no direct; use bootstrap of HL)
    rng = np.random.default_rng(7)
    hl = np.median(np.subtract.outer(f,m).ravel())
    bs = [np.median(np.subtract.outer(rng.choice(f,len(f)),rng.choice(m,len(m))).ravel()) for _ in range(2000)]
    # PS bootstrap CI
    bsps=[]
    for _ in range(4000):
        a=rng.choice(f,len(f)); b=rng.choice(m,len(m))
        bsps.append(stats.mannwhitneyu(a,b,alternative='two-sided',method='asymptotic')[0]/(len(a)*len(b)))
    sexres.append(dict(id=lab,outcome=ycol,nF=len(f),nM=len(m),medF=np.median(f),medM=np.median(m),
                       U=U,Z=Z,p=p,reported_Z=repZ,reported_p=repp,PS=ps,
                       PS_lo=np.percentile(bsps,2.5),PS_hi=np.percentile(bsps,97.5),
                       HL=hl,HL_lo=np.percentile(bs,2.5),HL_hi=np.percentile(bs,97.5)))
sexdf=pd.DataFrame(sexres)
print(sexdf.to_string(index=False,float_format=lambda v:f"{v:.4g}"))


# ------------------------ cell 12 ------------------------

print(d['number_other_fetch_cats_household'].value_counts(dropna=False).to_dict())
print(d['fetch_cats_household'].value_counts(dropna=False).to_dict())
print(d['total_household_number_cats'].value_counts(dropna=False).to_dict())

# ---- breakdown design effect: DEFF at which each test stops clearing its alpha
tests = []
for _,r in rep_df.iterrows():
    tests.append(dict(id=r['id'], label=r['what'], stat=r['X2'], df=int(r['df']), p=r['p'], alpha=0.05, kind='chi2'))
# post-hoc chi-squares used alpha 0.0166
for t in tests:
    if t['id'] in ('C3a','C3b','C3c','C4a','C4b','C4c'): t['alpha']=0.05/3
for _,r in kwdf.iterrows():
    tests.append(dict(id=r['id'], label=f"KW {r['outcome'].replace('times_','')} by {r['by']}", stat=r['H'], df=int(r['df']), p=r['p'], alpha=0.05, kind='chi2'))
for _,r in sexdf.iterrows():
    tests.append(dict(id=r['id'], label=f"MWU {r['outcome'].replace('times_','')} by sex", stat=r['Z']**2, df=1, p=r['p'], alpha=0.05, kind='Z2'))

for t in tests:
    crit = stats.chi2.ppf(1-t['alpha'], t['df'])
    t['breakdown_DEFF'] = t['stat']/crit if t['p']<t['alpha'] else np.nan
tdf = pd.DataFrame(tests)
print()
print(tdf[['id','label','stat','df','p','alpha','breakdown_DEFF']].to_string(index=False,float_format=lambda v:f"{v:.4g}"))


# ------------------------ cell 14 ------------------------

crit3 = stats.chi2.ppf(1-0.05/3, 1)
pwdf['breakdown_DEFF'] = np.where(pwdf['p_raw']<0.05/3, pwdf['Z']**2/crit3, np.nan)

rng = np.random.default_rng(11)
lo=[];hi=[]
for _,r in pwdf.iterrows():
    x = d.loc[d[r['by']]==r['g1'], r['outcome']].values
    z = d.loc[d[r['by']]==r['g2'], r['outcome']].values
    b=[stats.mannwhitneyu(rng.choice(x,len(x)),rng.choice(z,len(z)),method='asymptotic')[0]/(len(x)*len(z)) for _ in range(2000)]
    lo.append(np.percentile(b,2.5)); hi.append(np.percentile(b,97.5))
pwdf['PS_lo']=lo; pwdf['PS_hi']=hi
print(pwdf[['fam','outcome','by','g1','g2','med1','med2','p_bonf','PS','PS_lo','PS_hi','breakdown_DEFF']].to_string(index=False,float_format=lambda v:f"{v:.4g}"))

def m_a(sizes):
    s=np.array(sizes,float); return (s**2).sum()/s.sum()
A = [2]*230 + [1]*694
B = [4]*76 + [2]*2 + [1]*846
print("\nA:", len(A), sum(A), "  B:", len(B), sum(B))
print(f"m_a min-clustering (230 owners with 2 cats): {m_a(A):.4f}")
print(f"m_a max-cluster-4   (76 owners with 4 cats): {m_a(B):.4f}")


# ------------------------ cell 15 ------------------------

prim = [('C2',rep_df.loc[rep_df.id=='C2','p'].iloc[0]),
        ('C3',rep_df.loc[rep_df.id=='C3','p'].iloc[0]),
        ('C4',rep_df.loc[rep_df.id=='C4','p'].iloc[0]),
        ('C5',kwdf.loc[kwdf.id=='C5','p'].iloc[0]),
        ('C6',kwdf.loc[kwdf.id=='C6','p'].iloc[0]),
        ('C7',kwdf.loc[kwdf.id=='C7','p'].iloc[0]),
        ('C8',kwdf.loc[kwdf.id=='C8','p'].iloc[0]),
        ('C9',rep_df.loc[rep_df.id=='C9','p'].iloc[0]),
        ('C10',rep_df.loc[rep_df.id=='C10','p'].iloc[0]),
        ('C11',sexdf.loc[sexdf.id=='C11','p'].iloc[0]),
        ('C12',sexdf.loc[sexdf.id=='C12','p'].iloc[0])]
labs=[a for a,_ in prim]; ps=[b for _,b in prim]
mt = stat_multiplicity(ps, alpha=0.05, labels=labs)
print(mt.to_string(index=False) if hasattr(mt,'to_string') else mt)


# ------------------------ cell 16 ------------------------

import matplotlib as mpl, matplotlib.pyplot as plt
apply_figure_style(sizes=(9,8,7))
GREY='#9e9e9e'; FOCAL='#c0392b'; BLUE='#2c5f8a'; BAND='#e8b4b0'

# ---------------- FIG 1: clustering sensitivity ----------------
rowsf=[]
name = {'C2':'Sex ratio: 617 male vs 537 female',
        'C3':'Who initiates (3-way)','C3a':'Initiates: cat vs owner','C3b':'Initiates: cat vs about-equal',
        'C3c':'Initiates: owner vs about-equal','C4':'Who ends (3-way)','C4a':'Ends: cat vs owner',
        'C4b':'Ends: cat vs about-equal','C5':'Retrievals by initiator (KW)','C6':'Retrievals by ender (KW)',
        'C7':'Monthly sessions by initiator (KW)','C8':'Monthly sessions by ender (KW)'}
for _,r in tdf.iterrows():
    if np.isfinite(r['breakdown_DEFF']): rowsf.append((name[r['id']], r['breakdown_DEFF']))
short={'times_object_retrieved_recent':'Retrievals','times_monthly_fetch_sessions':'Monthly sessions'}
glab={'Cat':'cat','Myself':'owner','About equal':'about-equal'}
for _,r in pwdf.iterrows():
    if np.isfinite(r['breakdown_DEFF']):
        rowsf.append((f"{short[r['outcome']]} by {'initiator' if 'initiate' in r['by'] else 'ender'}: "
                      f"{glab[r['g1']]} vs {glab[r['g2']]}", r['breakdown_DEFF']))
f1 = pd.DataFrame(rowsf, columns=['lab','deff']).sort_values('deff')
DEFF_LO, DEFF_HI = m_a(A), m_a(B)
nfail = int((f1['deff']<DEFF_HI).sum())

fig1, ax = plt.subplots(figsize=(7.2,6.4))
y = np.arange(len(f1))
inside = f1['deff'].values < DEFF_HI
ax.axvspan(DEFF_LO, DEFF_HI, color=BAND, alpha=.55, zorder=0, lw=0)
ax.axvline(1.0, color='k', lw=.9, ls=':', zorder=1)
for yi, v, ins in zip(y, f1['deff'].values, inside):
    c = FOCAL if ins else BLUE
    ax.plot([1.0, v],[yi,yi], color=c, lw=1.2, alpha=.65, zorder=2)
    ax.plot(v, yi, 'o', ms=6, color=c, zorder=3)
ax.set_yticks(y); ax.set_yticklabels(f1['lab'].values)
ax.set_xscale('log'); ax.set_xticks([1,1.5,2,3,5,10,20,50])
ax.get_xaxis().set_major_formatter(mpl.ticker.FuncFormatter(lambda v,_: f"{v:g}"))
ax.set_xli…[+891 chars]


# ------------------------ cell 17 ------------------------

for t in list(fig1.axes[0].texts): t.remove()
fig1.axes[0].text(4.0, 0.0, 'shaded band: design effect implied by 924 owners\nreporting 1154 cats, at the worst case of perfect\nwithin-owner correlation (intraclass correlation = 1)',
                  fontsize=7, va='bottom', ha='left', color='#5a3330')
fig1.savefig('fig_forman_clustering.png', dpi=300, bbox_inches='tight')
print(audit_figure(fig1))


# ------------------------ cell 19 ------------------------

ef = pwdf.copy()
ef['outlab'] = ef['outcome'].map(short) + ' by ' + np.where(ef['by'].str.contains('initiate'),'initiator','ender')
ef['comp'] = ef['g1'].map(glab) + ' vs ' + ef['g2'].map(glab)
sx = sexdf.copy()
sx['outlab'] = sx['outcome'].map(short) + ' by cat sex'
sx['comp'] = 'female vs male'
allef = pd.concat([ef[['outlab','comp','PS','PS_lo','PS_hi','p_bonf']],
                   sx[['outlab','comp','PS','PS_lo','PS_hi']].assign(p_bonf=sx['p'].values)], ignore_index=True)
order = ['Retrievals by initiator','Retrievals by ender','Monthly sessions by initiator','Monthly sessions by ender',
         'Retrievals by cat sex','Monthly sessions by cat sex']
allef['k']=allef['outlab'].map({o:i for i,o in enumerate(order)})
allef=allef.sort_values(['k']).reset_index(drop=True)

fig2, ax = plt.subplots(figsize=(7.4,5.6))
ypos=[]; ylab=[]; cur=0; headers=[]
for grp in order:
    sub = allef[allef['outlab']==grp]
    headers.append((cur+len(sub)-0.3, grp))
    for _,r in sub.iloc[::-1].iterrows():
        ypos.append(cur); ylab.append(r['comp']); cur+=1
    cur+=0.9
allef_ord = pd.concat([allef[allef['outlab']==g].iloc[::-1] for g in order], ignore_index=True)
ax.axvline(0.5, color='k', lw=1.0, ls='--', zorder=1)
for yi,(_,r) in zip(ypos, allef_ord.iterrows()):
    sig = r['p_bonf'] < 0.05
    c = FOCAL if sig else GREY
    ax.plot([r['PS_lo'], r['PS_hi']],[yi,yi], color=c, lw=1.8, solid_capstyle='butt', zorder=2)
    ax.plot(r['PS'], yi, 'o', ms=6.5, color=c, zorder=3, mec='white', mew=.6)
ax.set_yticks(ypos); ax.set_yticklabels(allef_ord['comp'].values)
for yh, lab in headers:
    ax.text(0.22, yh, lab, fontsize=8, fontweight='bold', va='center', ha='left', color='#333333')
ax.set_xlim(0.20, 0.76); ax.set_ylim(-1.0, cur-0.4)
ax.set_xlabel('Probability of superiority  P(a random cat in group 1 > a random cat in group 2)\nwith 95% percentile-bootstrap interval; 0.5 = no difference')
ax.set_title('No effect size is reported in the paper; every rank comparison lies\nbetween…[+452 chars]


# ------------------------ cell 20 ------------------------

ax = fig2.axes[0]
for t in list(ax.texts):
    if t.get_text().startswith('red ='): t.remove()
ax.set_ylim(cur-0.4, -1.6)   # inverted: first group on top
ax.text(0.205, -1.5, 'red = significant (Bonferroni-adjusted within family)   grey = not significant   n = 1154 cats, 924 owners',
        fontsize=7, ha='left', va='top', color='#444444')
fig2.savefig('fig_forman_effects.png', dpi=300, bbox_inches='tight')
print(audit_figure(fig2))


# ------------------------ cell 21 ------------------------

plt.close(fig2)
fig2, ax = plt.subplots(figsize=(7.4,5.6))
ypos=[]; cur=0; headers=[]
blocks=[]
for grp in order:
    sub = allef[allef['outlab']==grp]
    headers.append((cur-0.75, grp))
    ys=[]
    for _,r in sub.iterrows():
        ys.append(cur); cur+=1
    blocks.append((sub, ys)); cur+=1.1
ax.axvline(0.5, color='k', lw=1.0, ls='--', zorder=1)
ytick=[]; ylab=[]
for sub, ys in blocks:
    for yi,(_,r) in zip(ys, sub.iterrows()):
        c = FOCAL if r['p_bonf']<0.05 else GREY
        ax.plot([r['PS_lo'], r['PS_hi']],[yi,yi], color=c, lw=1.8, solid_capstyle='butt', zorder=2)
        ax.plot(r['PS'], yi, 'o', ms=6.5, color=c, zorder=3, mec='white', mew=.6)
        ytick.append(yi); ylab.append(r['comp'])
ax.set_yticks(ytick); ax.set_yticklabels(ylab)
for yh, lab in headers:
    ax.text(0.205, yh, lab, fontsize=8, fontweight='bold', va='center', ha='left', color='#333333')
ax.set_xlim(0.20, 0.76); ax.set_ylim(cur-0.6, -1.5)
ax.set_xlabel('Probability of superiority  P(a random cat in group 1 > a random cat in group 2)\nwith 95% percentile-bootstrap interval; 0.5 = no difference')
ax.set_title('No effect size is reported in the paper; every rank comparison lies\nbetween 0.28 and 0.65 on the scale the rank tests actually estimate', loc='left')
ax.text(0.205, cur-0.75, 'red = significant (Bonferroni-adjusted within family)    grey = not significant    n = 1154 cats reported by 924 owners',
        fontsize=7, ha='left', va='bottom', color='#444444')
set_frame(ax)
fig2.tight_layout(); fig2.savefig('fig_forman_effects.png', dpi=300, bbox_inches='tight')
print(audit_figure(fig2))


# ------------------------ cell 22 ------------------------

plt.close('all')
fig3, axes = plt.subplots(1, 2, figsize=(7.6,4.4), sharey=True)
levels = ['Cat','About equal','Myself']
plab = {'Cat':'cat','About equal':'about-equal','Myself':'owner'}
rngj = np.random.default_rng(3)
for axi,(gcol, ttl) in zip(axes, [('initiate_fetch','Grouped by who usually initiates'),
                                  ('end_fetch','Grouped by who usually ends')]):
    for i,lev in enumerate(levels):
        v = d.loc[d[gcol]==lev,'times_object_retrieved_recent'].values
        axi.scatter(i + rngj.uniform(-.26,.26,len(v)), v, s=4, color=GREY, alpha=.30, lw=0, zorder=2)
        med = np.median(v); q1,q3 = np.percentile(v,[25,75])
        axi.plot([i-.34,i+.34],[med,med], color=FOCAL, lw=2.4, zorder=4, solid_capstyle='butt')
        axi.plot([i,i],[q1,q3], color=FOCAL, lw=1.0, zorder=3)
        axi.text(i, 72, f"n = {len(v)}", ha='center', va='bottom', fontsize=7, color='#444444')
        axi.text(i+.40, med, f"{med:g}", ha='left', va='center', fontsize=7, color=FOCAL)
    axi.set_xticks(range(3)); axi.set_xticklabels([plab[l] for l in levels])
    axi.set_xlim(-.65, 2.75); axi.set_title(ttl, loc='left', fontsize=8)
    set_frame(axi)
axes[0].set_yscale('function', functions=(lambda x: np.sqrt(np.clip(x,0,None)), lambda x: x**2))
axes[0].set_yticks([0,1,2,5,10,20,40,68])
axes[0].get_yaxis().set_major_formatter(mpl.ticker.FuncFormatter(lambda v,_: f"{v:g}"))
axes[0].set_ylim(-0.6, 84)
axes[0].set_ylabel('Retrievals in the most recent fetching session\n(square-root scale; each point is one cat)')
fig3.suptitle('The two groups the paper reports as differing in retrievals by initiator\nhave the same median (5); red bars are medians with the interquartile range',
              x=0.015, ha='left', fontsize=9)
fig3.tight_layout(rect=[0,0,1,0.88]); fig3.savefig('fig_forman_distributions.png', dpi=300, bbox_inches='tight')
print(audit_figure(fig3))


# ------------------------ cell 23 ------------------------

axes[0].set_ylabel('Retrievals in the most recent fetching session\n(square root scale; each point is one cat)')
axes[1].yaxis.set_label_position('right')
axes[1].set_ylabel('square root scale', fontsize=7, color='#444444')
fig3.tight_layout(rect=[0,0,1,0.94])
fig3.savefig('fig_forman_distributions.png', dpi=300, bbox_inches='tight')
print(audit_figure(fig3))


# ------------------------ cell 24 ------------------------

from statsmodels.stats.proportion import proportion_confint as pci


# ------------------------ cell 25 ------------------------

def wil(k,n): 
    lo,hi = pci(k,n,method='wilson'); return k/n, lo, hi
extra = {}
extra['untrained'] = wil(1089,1154)
extra['cat_init_cond'] = wil(553, 553+249)     # P(cat | not 'about equal'), initiation
extra['cat_end_cond']  = wil(675, 675+248)
extra['cat_init_uncond']= wil(553,1154); extra['own_init_uncond']=wil(249,1154)
extra['cat_end_uncond'] = wil(675,1154); extra['own_end_uncond'] =wil(248,1154)
extra['male'] = wil(617,1154)
extra['C4c_owner_vs_equal'] = wil(248,479)
for k,v in extra.items(): print(f"{k}: {v[0]:.4f} [{v[1]:.4f}, {v[2]:.4f}]")

# p-curve across the paper's significant primary + post-hoc tests
allp = list(rep_df['p'].values) + list(kwdf['p'].values) + list(sexdf['p'].values) + list(pwdf['p_bonf'].values)
sigp = [p for p in allp if p < 0.05]
print("\nn tests reconstructed:", len(allp), " significant:", len(sigp))
print("significant p in (0.01,0.05]:", sum(0.01 < p <= 0.05 for p in sigp),
      "| p<=0.001:", sum(p <= 0.001 for p in sigp))
print("max significant p:", max(sigp))


# ------------------------ cell 28 ------------------------

def fp(p):
    if p is None or (isinstance(p,float) and not np.isfinite(p)): return ''
    return f"{p:.3g}" if p >= 1e-4 else f"{p:.1e}"
R = {r['id']: r for _,r in rep_df.iterrows()}
K = {r['id']: r for _,r in kwdf.iterrows()}
S = {r['id']: r for _,r in sexdf.iterrows()}
P = {(r['fam'], r['g1'], r['g2']): r for _,r in pwdf.iterrows()}
BD = tdf.set_index('id')['breakdown_DEFF']

SURVEY = 'cross-sectional self-selected online survey; owner report; unit = cat, clustered within owner'
C = []
def add(**kw): C.append(kw)

add(id='C1', claim='94.4% of fetching cats were not explicitly trained to fetch', design=SURVEY,
    test_used='none (descriptive proportion)', test_indicated='proportion with interval, clustered by owner',
    reported_p='n/a', recomputed_p='n/a',
    effect='1089/1154 = 94.4% of cats, 95% Wilson CI 92.9-95.6% (unclustered)',
    verdict='Supported, overstated', severity='C')
add(id='C2', claim='Significantly more male (617) than female (537) fetching cats', design=SURVEY,
    test_used='chi-square goodness of fit vs 50:50, df=1',
    test_indicated='no test of this kind is informative here: the sampling frame fixes the sex composition; if tested at all, an owner-clustered binomial against a justified reference ratio',
    reported_p='0.018 (X2=5.50)', recomputed_p=f"{fp(R['C2']['p'])} (X2={R['C2']['X2']:.3f})",
    effect='53.5% male, 95% CI 50.6-56.3% (unclustered); loses significance at design effect >= 1.44; Bonferroni p over the 11 primary tests = 0.204',
    verdict='Mis-specified', severity='A')
add(id='C3', claim='Unequal distribution of who initiates fetching sessions (cat / about-equal / owner)', design=SURVEY,
    test_used='chi-square GOF, df=2', test_indicated='same, with owner-clustered variance',
    reported_p='<0.001 (X2=124.29)', recomputed_p=f"{fp(R['C3']['p'])} (X2={R['C3']['X2']:.2f})",
    effect='cat 47.9% [45.1-50.8], about-equal 30.5%, owner 21.6% [19.3-24.0]; survives design effect up to 20.7',
    verdict='Supported', severit…[+10196 chars]


# ------------------------ cell 30 ------------------------

def esc(s): return str(s).replace('|','\\|').replace('\n',' ')
cols = list(tab.columns)
lines = ['| ' + ' | '.join(cols) + ' |', '|' + '|'.join(['---']*len(cols)) + '|']
for _,r in tab.iterrows():
    lines.append('| ' + ' | '.join(esc(r[c]) for c in cols) + ' |')
md_table = '\n'.join(lines)
open('_table.md','w',encoding='utf8').write(md_table)
print(len(lines)-2, 'rows')


# ------------------------ cell 31 ------------------------

neff = 1154/m_a(B)
r5b = P[('C5','Cat','Myself')]
z2 = r5b['Z']**2
print(f"effective n worst case: {neff:.1f}")
print(f"C5b Z={r5b['Z']:.3f} Z2={z2:.3f}; crit(0.0167,df1)={crit3:.3f}")
for deff in [1.0, m_a(A), m_a(B)]:
    print(f"  DEFF={deff:.3f} -> adj chi2={z2/deff:.3f}, p={stats.chi2.sf(z2/deff,1):.4f} (threshold 0.0167)")
print(f"C2 adj: DEFF={m_a(A):.3f} p={stats.chi2.sf(R['C2']['X2']/m_a(A),1):.4f}; DEFF={m_a(B):.3f} p={stats.chi2.sf(R['C2']['X2']/m_a(B),1):.4f}")
print(f"C5 KW adj at DEFF={m_a(B):.3f}: p={stats.chi2.sf(K['C5']['H']/m_a(B),2):.4f}")


# ------------------------ cell 34 ------------------------

parts = [open(f,encoding='utf8').read() for f in ['_partA.md','_table.md','_partB.md']]
md = parts[0] + parts[1] + parts[2]
open('review_forman.md','w',encoding='utf8').write(md)
print(len(md), 'chars;', md.count('\n'), 'lines')
# read-back verification of a few quoted numbers against the computed frames
back = pd.read_csv('claims_forman.csv')
print(back.loc[back.id=='C2','effect'].iloc[0])
print(back.loc[back.id=='C5b','effect'].iloc[0])
print(back.loc[back.id=='C6b','effect'].iloc[0])
print('verdicts:', back['verdict'].value_counts().to_dict())
print('PS min/max across 14:', f"{allef['PS'].min():.3f}", f"{allef['PS'].max():.3f}")


# ------------------------ cell 35 ------------------------

import json
claims = json.load(open('handoff_claims.json')) if False else None


# ------------------------ cell 36 ------------------------

import json, os
os.makedirs('handoff', exist_ok=True)
recs = []
for _,r in claims.iterrows():
    recs.append({k: str(r[k]) for k in ['id','claim','design','test_used','test_indicated','reported_p','recomputed_p','verdict','severity']} | {'effect': str(r['effect'])})
json.dump(recs, open('handoff/claims.json','w'), indent=0)
print(len(recs))


# ------------------------ cell 37 ------------------------

import json
recs = json.load(open('handoff/claims.json'))
out = {
 "paper": "Forman J, Renner E, Leavens DA (2023). Fetching felines: a survey of cat owners on the diversity of cat (Felis catus) fetching behaviour. Scientific Reports 13:20456.",
 "doi": "10.1038/s41598-023-47409-w",
 "n_claims": len(recs),
 "claims": [{"id":r["id"],"claim":r["claim"],"design":r["design"],"test_used":r["test_used"],
             "test_indicated":r["test_indicated"],"reported_p":r["reported_p"],
             "recomputed_p":r["recomputed_p"],"effect":r["effect"],
             "verdict":r["verdict"],"severity":r["severity"]} for r in recs],
 "headline_findings": [
   "Every inferential statistic in the Results reproduced from the deposited per-cat file (MOESM3, 1154 rows) to the printed precision, with one exception: the sex-ratio chi-square is printed as 5.50 where recomputation gives 5.546 (the reported p = 0.018 matches). All group counts match exactly (553/352/249 initiator, 675/231/248 ender, 617/537 sex, 1089/65 training). 26 of 35 claims are Supported with no defect found.",
   "Severity A - the male-biased sex ratio (C2) does not survive its own design. Every test treats 1154 cats as independent when they were reported by 924 owners; the design effect this implies lies between 1.399 and 1.794 at the worst case of perfect within-owner correlation, and C2 stops clearing alpha at 1.444 (adjusted p = 0.046 to 0.079). It is also the only one of the paper's 11 primary tests to fail Bonferroni (p = 0.204), and a 50:50 reference has no population behind it in a self-selected survey of owners of fetching cats.",
   "Severity B - the pairwise comparison reported as 'significantly fewer retrievals if the owner usually initiates ... compared to the cat' (C5b) compares two groups with identical medians (5 vs 5). The rank-sum test estimates a probability of superiority of 0.565 [0.522, 0.604], a tail difference, and this is also the only pairwise result inside the clustering band (breakdown d…[+3617 chars]


# ------------------------ cell 38 ------------------------

md = open('review_forman.md',encoding='utf8').read()
old1 = "26 of 35 claims are **Supported** with no defect found."
new1 = ("26 of 35 claims are **Supported**; 19 of those carry no defect at all, and the other 7 "
        "(C4c, C5a, C7a, C9–C12) carry only a severity-C reporting defect — an absence claim stated "
        "without an interval (F-10) — which does not disturb the conclusion.")
assert md.count(old1)==1
md = md.replace(old1,new1)

old2 = "## F-10 — Severity C — Absence claims without intervals (C4c, C9–C12, C15, C17)"
old2 = "### F-10 — Severity C — Absence claims without intervals (C4c, C9–C12, C15, C17)"
assert md.count(old2)==1
md = md.replace(old2, "### F-10 — Severity C — Absence claims without intervals (C4c, C5a, C7a, C9–C12, C15, C17)")

old3 = '**What was done.** Six null results are reported as "there was not a significant difference"'
assert md.count(old3)==1
md = md.replace(old3, '**What was done.** Eight null results are reported as "there was not a significant difference", "there is no difference in retrieval number between when the cat usually initiates and when initiation is about equal" (C5a, p = 0.995), "no significant difference between the cat and if initiation is about equal" (C7a, p = 0.66)')

old4 = ("owner vs about-equal termination, 51.8% [47.3%, 56.2%]. These are informative nulls")
assert md.count(old4)==1
md = md.replace(old4, ("owner vs about-equal termination, 51.8% [47.3%, 56.2%]; cat vs about-equal initiation, "
  "retrievals 0.481 [0.442, 0.518] and monthly sessions 0.524 [0.484, 0.561]. These are informative nulls"))
open('review_forman.md','w',encoding='utf8').write(md)

chk = pd.read_csv('claims_forman.csv')
sup = chk[chk.verdict=='Supported']
print('Supported:', len(sup), '| severity none:', (sup.severity=='none').sum(),
      '| severity C:', sorted(sup.loc[sup.severity=='C','id'].tolist()))
for t in [new1.split(';')[0], 'C4c, C5a, C7a, C9–C12, C15, C17', 'Eight null results', '0.481 [0.442, 0.518]']:
    print(md…[+25 chars]


# ------------------------ cell 39 ------------------------

out["headline_findings"][0] = out["headline_findings"][0].replace(
 "26 of 35 claims are Supported with no defect found.",
 "26 of 35 claims are Supported; 19 of those carry no defect at all, and the other 7 (C4c, C5a, C7a, C9-C12) carry only a severity-C reporting defect - an absence claim stated without an interval (finding F-10) - which does not disturb the conclusion.")
assert "19 of those carry no defect" in out["headline_findings"][0]
r = host.submit_output(out,
 completion_bullets=[
   "Reproduced all 29 reported test statistics from the authors' deposited per-cat data",
   "Registered and adjudicated 35 claims: 26 Supported (19 defect-free, 7 severity C), 6 Supported-overstated, 2 Mis-specified, 1 Not assessable",
   "Bounded the unmodelled owner-clustering correction and identified the two results it can remove",
   "Delivered review_forman.md, claims_forman.csv and three figures"],
 deviations=[
   "The 924 owner clusters could not be reconstructed: the deposited file has no owner identifier and its row order does not preserve owner blocks. The clustering correction is therefore reported as a bound (design effect 1.399-1.794, derived from the published 924-owner/1154-cat totals and the largest household in the data, at the worst case of perfect within-owner correlation) rather than an exact owner-clustered re-analysis. Findings F-1 and F-2 are provisional on that bound.",
   "The thematic analysis supplements (MOESM4, MOESM5, MOESM7) and the object spreadsheet (MOESM6) were not reviewed; they make no inferential claims.",
   "Bootstrap intervals for probability of superiority use 2000 resamples per comparison (4000 for the two sex comparisons) and are unclustered, so they are slightly narrower than an owner-clustered interval would be."])
print(r['status'])
