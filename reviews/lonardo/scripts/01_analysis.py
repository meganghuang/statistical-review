# ==========================================================================
# lonardo review -- python cells, verbatim and in execution order
# conda env: python
# 49 cells with exit_status='ok'; cells that errored are omitted.
# Run top-to-bottom in ONE session: the originals ran in a persistent
# kernel, so later cells depend on earlier state.
# ==========================================================================


# ------------------------ cell 2 ------------------------

import os
root = "lonardo"
rows=[]
for dp,dn,fn in os.walk(root):
    for f in fn:
        p=os.path.join(dp,f)
        rows.append((os.path.relpath(p,root), os.path.getsize(p)))
rows.sort()
print(len(rows))
for r in rows: print(r[0], r[1])


# ------------------------ cell 3 ------------------------

import pandas as pd, numpy as np, os
base="lonardo/data/dog_non_verbal_communication_ET"
try:
    d=pd.read_parquet(f"{base}/data/dog_nonverbal_communication_samplereport_ds.parquet")
    print("ds", d.shape); print(d.dtypes); print(d.head(3).to_string())
except Exception as e:
    print("ERR", e)


# ------------------------ cell 5 ------------------------

import pyarrow.parquet as pq
ds = pq.read_table(f"{base}/data/dog_nonverbal_communication_samplereport_ds.parquet").to_pandas()
dall = pq.read_table(f"{base}/data/dog_nonverbal_communication_samplereport_ds_ALL_DATA.parquet").to_pandas()
print("ds", ds.shape, "ALL", dall.shape)
print(list(ds.columns))
print(ds.head(3).to_string())
print("subjects ds:", ds.subject.nunique(), "ALL:", dall.subject.nunique())


# ------------------------ cell 6 ------------------------

excl = ["Ace","Filou","Floki","George","Ignaz","Jimi","Lenny","Sahibu","Sheila","Timo","Zserbo"]
dat3 = ds[~ds.subject.isin(excl)].copy()
print("dat3 subjects:", dat3.subject.nunique(), "rows:", len(dat3))
print("time range ds:", ds.time.min(), ds.time.max(), "unique times:", ds.time.nunique())
# trials per subject in ds
tr = ds.groupby('subject').apply(lambda g: g[['condition','session_number']].drop_duplicates().shape[0])
print("trials per subject (ds) distribution:"); print(tr.value_counts().sort_index())
tra = dall.groupby('subject').apply(lambda g: g[['condition','session_number']].drop_duplicates().shape[0])
print("trials per subject (ALL):"); print(tra.value_counts().sort_index())
print("trial_type levels:", ds.trial_type.unique(), "conditions:", sorted(ds.condition.unique()))
print("rows per trial (ds):", ds.groupby(['subject','condition','session_number']).size().describe())
print("NaN pupil_base ds:", ds.pupil_base.isna().sum(), "ALL:", dall.pupil_base.isna().sum())


# ------------------------ cell 7 ------------------------

from scipy import stats
agg = dat3.groupby(['subject','trial_type'], observed=True)['pupil_base'].mean().unstack()
agg = agg.dropna()
print("N pairs:", len(agg))
print(dat3.groupby('trial_type', observed=True).apply(lambda g: g.groupby('subject',observed=True)['pupil_base'].mean()).groupby(level=0).agg(['mean','count']))
m = agg.mean(); se = agg.std(ddof=1)/np.sqrt(len(agg))
print("mean cong %.4f (se %.4f), incong %.4f (se %.4f)"%(m['cong'],se['cong'],m['incong'],se['incong']))
d = agg['cong']-agg['incong']
t = stats.ttest_rel(agg['cong'], agg['incong'])
print("paired t: t=%.4f df=%d p=%.5f"%(t.statistic, len(agg)-1, t.pvalue))
ci = t.confidence_interval()
print("mean diff (cong-incong) = %.4f, 95%% CI [%.4f, %.4f]"%(d.mean(), ci.low, ci.high))
print("dz = %.4f"%(d.mean()/d.std(ddof=1)))
sw = stats.shapiro(d); print("Shapiro W=%.5f p=%.6f"%(sw.statistic, sw.pvalue))
w = stats.wilcoxon(agg['cong'], agg['incong'], method='exact')
print("Wilcoxon exact: W=%.1f p=%.6f  (N nonzero=%d, ties=%d)"%(w.statistic, w.pvalue, (d!=0).sum(), (d==0).sum()))
print("T.plus style:", max(w.statistic, len(agg)*(len(agg)+1)/2 - w.statistic))


# ------------------------ cell 8 ------------------------

def paired_pupil(df, label):
    a = df.groupby(['subject','trial_type'], observed=True)['pupil_base'].mean().unstack().dropna()
    d = a['cong']-a['incong']
    t = stats.ttest_rel(a['cong'], a['incong']); ci=t.confidence_interval()
    w = stats.wilcoxon(a['cong'], a['incong'], method='exact')
    sw = stats.shapiro(d)
    return dict(label=label, n=len(a), mean_cong=a['cong'].mean(), mean_incong=a['incong'].mean(),
                diff=d.mean(), lo=ci.low, hi=ci.high, dz=d.mean()/d.std(ddof=1),
                t=t.statistic, p_t=t.pvalue, p_wilcox=w.pvalue, shapiro_p=sw.pvalue,
                p_sign=stats.binomtest((d<0).sum(), len(d), 0.5).pvalue)
res=[paired_pupil(dat3,"N=28 (authors' exclusion, ds)"),
     paired_pupil(ds,"N=39 all subjects, ds file"),
     paired_pupil(dall.dropna(subset=['pupil_base']),"N=39 ALL_DATA file")]
sens=pd.DataFrame(res)
print(sens.to_string(index=False, float_format=lambda x:"%.4f"%x))
# how many dogs in each subset contribute both trial types
for nm,df in [("ds",ds),("ALL",dall.dropna(subset=['pupil_base']))]:
    a = df.groupby(['subject','trial_type'], observed=True)['pupil_base'].mean().unstack()
    print(nm, "subjects with both:", a.dropna().shape[0], "of", a.shape[0])


# ------------------------ cell 9 ------------------------

ia = pd.read_csv(f"{base}/data/IA_report_IP_from_reaction.txt", sep="\t", na_values=".", low_memory=False)
iaz = pd.read_csv(f"{base}/data/IA_report_IP_from_reaction_frame579.txt", sep="\t", na_values=".", low_memory=False)
print(ia.shape, iaz.shape)
print([c for c in ia.columns])


# ------------------------ cell 10 ------------------------

demo_raw = pd.read_csv(f"{base}/data/Non_verbal_communication_counterbalancing.csv")
print(demo_raw.shape, list(demo_raw.columns))
print(demo_raw.head(4).to_string())
print(demo_raw['EDF3'].head(10).tolist())


# ------------------------ cell 11 ------------------------

import re
# step 1-2
z = iaz[iaz.RECORDING_SESSION_LABEL=="Zserbo_1"]
main = ia[~ia.RECORDING_SESSION_LABEL.isin(["Nala_2","Sahibu_2","Melody_1","Zserbo_1"])]
orig = pd.concat([main, z], ignore_index=True).sort_values("RECORDING_SESSION_LABEL")
print("orig rows:", len(orig), " (main %d + zserbo %d)"%(len(main), len(z)))
print("IA_LABEL levels:", sorted(orig.IA_LABEL.dropna().unique()))

# demo
demo = demo_raw.copy()
demo['EDF3'] = demo['EDF3'].replace({"Georgia3":"Georgia_3","Mathild3":"Mathilda_3"})
demo['subject'] = demo['EDF3'].astype(str).str.split("_").str[0]
demo.loc[demo['EDF3'].isna(),'subject']=np.nan
demo = demo[demo.subject.notna() & (demo.subject!='nan')]
print("demo subjects:", demo.subject.nunique(), len(demo))

cols = ['RECORDING_SESSION_LABEL','IP_LABEL','IA_LABEL','IA_ID','Trial_Index_','condition','trial_type','session_number','trial_number','video_file','DATA_FILE','IA_AREA','IA_AVERAGE_FIX_PUPIL_SIZE','IA_DWELL_TIME','IA_DWELL_TIME_%','IA_FIXATION_COUNT','IA_MAX_FIX_PUPIL_SIZE','INTEREST_AREA_FIXATION_SEQUENCE','TRIAL_DWELL_TIME','TRIAL_FIXATION_COUNT','TRIAL_IA_COUNT','TRIAL_TOTAL_VISITED_IA_COUNT','IA_FIRST_FIXATION_TIME']
rid = orig[cols].copy()
rec = {"Georgia1":"Georgia_1","Georgia2":"Georgia_2","Georgia3":"Georgia_3","Georgia4":"Georgia_4",
       "Mathild1":"Mathilda_1","Mathild2":"Mathilda_2","Mathild3":"Mathilda_3","Mathild4":"Mathilda_4"}
rid['RECORDING_SESSION_LABEL']=rid['RECORDING_SESSION_LABEL'].replace(rec)
rid[['subject','session.num']] = rid['RECORDING_SESSION_LABEL'].str.split("_", n=1, expand=True)
rid = rid.drop(columns=['RECORDING_SESSION_LABEL'])
# full_join then filter !is.na(session_number)
rid = rid.merge(demo, on='subject', how='outer')
rid = rid[rid.session_number.notna()]
print("reaction.ip.data rows:", len(rid), "subjects:", rid.subject.nunique())
print("sum sex==f:", (demo.sex=='f').sum(), " mean age:", pd.to_numeric(demo.age, errors='coerce').mean())


# ------------------------ cell 12 ------------------------

dw = rid[rid.IA_LABEL!="FIXATION_TRIGGER"].copy()
dw['agent_type'] = np.where(dw.IA_LABEL.str.contains("inviting|pointing"), "communicating","reacting")
dw['ia_dwell_time']=dw['IA_DWELL_TIME']
dw['proportion.dwell.time.agents']=dw.ia_dwell_time/dw.TRIAL_DWELL_TIME
print("rows:", len(dw), " IAs per trial:", dw.groupby(['subject','trial_number']).size().value_counts().to_dict())
g = dw.groupby(['subject','agent_type'], observed=True)['ia_dwell_time'].mean().unstack()
print("N subjects:", len(g), " any NA:", g.isna().sum().to_dict())
print("mean reacting = %.3f  (target 5105.282)"%g['reacting'].mean())
print("mean communicating = %.3f  (target 3217.737)"%g['communicating'].mean())
print("sd reacting = %.3f  sd communicating = %.3f"%(g['reacting'].std(ddof=1), g['communicating'].std(ddof=1)))
gg=g.dropna()
t=stats.ttest_rel(gg['reacting'],gg['communicating']); ci=t.confidence_interval()
dd=gg['reacting']-gg['communicating']
print("paired t: t=%.4f df=%d p=%.3g  diff=%.1f ms CI[%.1f, %.1f] dz=%.3f n=%d"%(
    t.statistic, len(gg)-1, t.pvalue, dd.mean(), ci.low, ci.high, dd.mean()/dd.std(ddof=1), len(gg)))


# ------------------------ cell 13 ------------------------

def count_transitions(seq):
    if not isinstance(seq,str): return 0
    s = seq.replace("[","").replace("]","").replace(" ","")
    vals=[]
    for e in s.split(","):
        try: vals.append(float(e))
        except: pass
    tr=0; prev=None
    for v in vals:
        if v in (21.0,22.0,23.0):
            if prev is not None and prev!=20.0 and prev!=v: tr+=1
            prev=v
    return tr
rid['transition_count']=rid['INTEREST_AREA_FIXATION_SEQUENCE'].map(count_transitions)
trd = rid[rid.IA_LABEL!="FIXATION_TRIGGER"].groupby(
    ['subject','trial_number','condition','trial_type','TRIAL_DWELL_TIME'], observed=True)['transition_count'].first().reset_index()
print("trials:", len(trd), "subjects:", trd.subject.nunique())
print("range %d-%d  mean %.2f  sd %.2f  zeros %d"%(trd.transition_count.min(), trd.transition_count.max(),
      trd.transition_count.mean(), trd.transition_count.std(ddof=1), (trd.transition_count==0).sum()))
print(trd.groupby('trial_type', observed=True)['transition_count'].agg(['count','mean','std']))
# subject-level paired
tg = trd.groupby(['subject','trial_type'], observed=True)['transition_count'].mean().unstack()
print("subjects with both trial types:", tg.dropna().shape[0], "of", len(tg))
tgg=tg.dropna(); dd=tgg['incong']-tgg['cong']
t=stats.ttest_rel(tgg['incong'],tgg['cong']); ci=t.confidence_interval()
print("transitions paired t (incong-cong): diff=%.3f CI[%.3f,%.3f] t=%.3f p=%.3f dz=%.3f n=%d"%(
    dd.mean(), ci.low, ci.high, t.statistic, t.pvalue, dd.mean()/dd.std(ddof=1), len(tgg)))
print("wilcoxon p=%.4f"%stats.wilcoxon(tgg['incong'],tgg['cong']).pvalue)
# dwell time by trial type at subject level
dtg = dw.groupby(['subject','trial_type'], observed=True)['ia_dwell_time'].mean().unstack().dropna()
dd2=dtg['incong']-dtg['cong']; t2=stats.ttest_rel(dtg['incong'],dtg['cong']); ci2=t2.confidence_interval()
print("dwell paired t (incong-cong): diff=%.1f ms CI[%.1f,%.1f] t=%.3f p=%.3f dz=%.3f n=%d"%(
    dd2.mean(), ci2.low, ci2.high, t2.s…[+59 chars]


# ------------------------ cell 14 ------------------------

print([f for f in dir() if f.startswith('stat_')])
agg28 = dat3.groupby(['subject','trial_type'], observed=True)['pupil_base'].mean().unstack().dropna()
agg37 = ds.groupby(['subject','trial_type'], observed=True)['pupil_base'].mean().unstack().dropna()
agg38 = dall.dropna(subset=['pupil_base']).groupby(['subject','trial_type'], observed=True)['pupil_base'].mean().unstack().dropna()
tg2 = tg.dropna(); dtg2 = dtg
sens28 = stat_two_group(agg28['cong'].values, agg28['incong'].values, paired=True, n_perm=20000)
print(sens28.to_string())
print({k:(round(v,4) if isinstance(v,float) else v) for k,v in sens28.attrs["effects"].items()})


# ------------------------ cell 15 ------------------------

rows=[]
def addrow(name, a, b, note):
    s = stat_two_group(a, b, paired=True, n_perm=20000); e=s.attrs["effects"]
    r = {"analysis":name, "n":e["n_pairs"], "mean_diff":e["mean_difference"],
         "ci_lo":e["ci95"][0], "ci_hi":e["ci95"][1], "dz":e["cohen_dz"], "note":note}
    for _,row in s.iterrows(): r["p_"+row["test"].split()[0].lower()] = row["p"]
    rows.append(r)
addrow("Pupil cong-incong, N=28 (authors' exclusion)", agg28['cong'].values, agg28['incong'].values, "authors' reported subset")
addrow("Pupil cong-incong, N=37 (all subj, ds file)", agg37['cong'].values, agg37['incong'].values, "no subject exclusion")
addrow("Pupil cong-incong, N=38 (ALL_DATA file)", agg38['cong'].values, agg38['incong'].values, "no subject/trial exclusion")
addrow("Dwell time incong-cong, N=38", dtg2['incong'].values, dtg2['cong'].values, "null claim")
addrow("Gaze transitions incong-cong, N=38", tg2['incong'].values, tg2['cong'].values, "null claim")
addrow("Dwell reacting-communicating, N=39", g['reacting'].values, g['communicating'].values, "agent-type effect")
sens_tab = pd.DataFrame(rows)
pd.set_option("display.width",250)
print(sens_tab.to_string(index=False, float_format=lambda x:"%.4f"%x))
sens_tab.to_csv("sensitivity_table.csv", index=False)


# ------------------------ cell 16 ------------------------

r = host.exec_peek("5d4fdee4-5115-4837-8e3b-32091910c034")
print(r.get("status"))
print((r.get("stdout") or "")[-3000:])


# ------------------------ cell 17 ------------------------

r = host.exec_peek("5d4fdee4-5115-4837-8e3b-32091910c034")
print(r.get("status")); print((r.get("stdout") or "")[-2500:])


# ------------------------ cell 18 ------------------------

r = host.exec_peek("5d4fdee4-5115-4837-8e3b-32091910c034")
print(r.get("status")); print((r.get("stdout") or "")[-2500:])


# ------------------------ cell 19 ------------------------

print(host.exec_interrupt("5d4fdee4-5115-4837-8e3b-32091910c034"))


# ------------------------ cell 20 ------------------------

import matplotlib as mpl, matplotlib.pyplot as plt
apply_figure_style()
# ---- data for Fig 1
pup_all = ds.groupby(['subject','trial_type'], observed=True)['pupil_base'].mean().unstack().dropna()
pup_all = pup_all.assign(diff=pup_all['cong']-pup_all['incong'])
pup_all['included'] = ~pup_all.index.isin(excl)
inc = pup_all[pup_all.included]['diff'].values; exc = pup_all[~pup_all.included]['diff'].values
print("included dogs:", len(inc), "excluded dogs present in ds with both trial types:", len(exc))
print("mean diff included %.1f  excluded %.1f"%(inc.mean(), exc.mean()))
sets = [("Authors' analysed set\n(dogs with all 4 valid trials)", agg28),
        ("All dogs in the same file\n(no completeness exclusion)", agg37),
        ("All dogs, all trials\n(ALL_DATA file)", agg38)]
est=[]
for lab,a in sets:
    d=a['cong']-a['incong']; t=stats.ttest_rel(a['cong'],a['incong']); ci=t.confidence_interval()
    est.append((lab, len(a), d.mean(), ci.low, ci.high, t.pvalue,
                stats.wilcoxon(a['cong'],a['incong'],method='exact').pvalue))
for e in est: print(e)


# ------------------------ cell 21 ------------------------

fig, axes = plt.subplots(1, 2, figsize=(7.4, 3.5), gridspec_kw=dict(width_ratios=[1,1.25], wspace=0.45))
ax=axes[0]
rng=np.random.default_rng(7)
for i,(vals,lab,col) in enumerate([(inc,"Included\n(n = 28)","#1f4e79"),(exc,"Excluded\n(n = 9)","#b15928")]):
    x = i + rng.uniform(-0.13,0.13,len(vals))
    ax.scatter(x, vals, s=22, facecolor='none', edgecolor=col, linewidth=0.9, zorder=3)
    m=vals.mean(); sem=vals.std(ddof=1)/np.sqrt(len(vals)); h=stats.t.ppf(.975,len(vals)-1)*sem
    ax.errorbar(i, m, yerr=h, fmt='D', ms=5, color=col, capsize=4, lw=1.4, zorder=4)
ax.axhline(0, color=META_GREY, lw=0.9, zorder=1)
ax.set_xticks([0,1]); ax.set_xticklabels(["Included\n(n = 28)","Excluded\n(n = 9)"])
ax.set_ylabel("Pupil change, congruent − incongruent\n(baseline-corrected units)")
ax.set_xlabel("Dog's status in the authors' pupil analysis")
ax.set_title("The excluded dogs lean the other way", loc='left')
ax.margins(y=0.08)

ax=axes[1]
ypos=np.arange(len(est))[::-1]
for (lab,n,m,lo,hi,pt,pw),y in zip(est,ypos):
    col = "#1f4e79" if n==28 else "#4d4d4d"
    ax.plot([lo,hi],[y,y], color=col, lw=2.0, solid_capstyle='butt', zorder=3)
    ax.plot([m],[y], 'D', ms=6, color=col, zorder=4)
    ax.text(hi+14, y, "n = %d, p = %.3f"%(n,pt), va='center', ha='left', fontsize=6, color=col)
ax.axvline(0, color=META_GREY, lw=0.9, zorder=1)
ax.set_yticks(ypos); ax.set_yticklabels([e[0] for e in est], fontsize=6)
ax.set_xlabel("Mean pupil difference, congruent − incongruent\n(baseline-corrected units; bars = 95% CI of the mean)")
ax.set_title("The effect is confined to the completeness-filtered subset", loc='left')
ax.set_xlim(-300, 330); ax.margins(y=0.22)
for a in axes: set_frame(a)
fig.savefig("fig_lonardo_exclusion.png", dpi=300, bbox_inches='tight')
print(audit_figure(fig))


# ------------------------ cell 22 ------------------------

host.view_image("fig_lonardo_exclusion.png")


# ------------------------ cell 23 ------------------------

axes[0].set_title("Per-dog pupil difference, by inclusion status", loc='left')
fig.savefig("fig_lonardo_exclusion.png", dpi=300, bbox_inches='tight')

# ---- Fig 2: Q-Q of the within-subject differences the paired tests rely on
d28 = (agg28['cong']-agg28['incong']).values
d37 = (agg37['cong']-agg37['incong']).values
fig2, axs = plt.subplots(1, 2, figsize=(6.6, 3.2), sharey=False)
for ax,(dv,lab,col) in zip(axs, [(d28,"Authors' set (n = 28)\nShapiro–Wilk p = %.3f"%stats.shapiro(d28).pvalue,"#1f4e79"),
                                 (d37,"All dogs (n = 37)\nShapiro–Wilk p = %.3f"%stats.shapiro(d37).pvalue,"#4d4d4d")]):
    osm, osr = stats.probplot(dv, dist="norm", fit=False)
    ax.scatter(osm, osr, s=20, facecolor='none', edgecolor=col, linewidth=0.9, zorder=3)
    sl, ic = np.polyfit(osm, osr, 1)
    xs=np.array([osm.min(), osm.max()]); ax.plot(xs, sl*xs+ic, color=META_GREY, lw=1.0, zorder=2)
    ax.axhline(0, color=META_GREY, lw=0.6, ls=':', zorder=1)
    ax.set_title(lab, loc='left'); ax.set_xlabel("Theoretical normal quantile")
    set_frame(ax); ax.margins(0.06)
axs[0].set_ylabel("Pupil difference per dog\ncongruent − incongruent")
fig2.suptitle("Left-skew and a lower outlier in the differences the paired t-test assumes are normal",
              x=0.01, ha='left', fontsize=8)
fig2.tight_layout(rect=[0,0,1,0.93])
fig2.savefig("fig_lonardo_qq.png", dpi=300, bbox_inches='tight')
print(audit_figure(fig2))


# ------------------------ cell 24 ------------------------

axs[1].set_ylabel("Pupil difference per dog\ncongruent − incongruent")
fig2.tight_layout(rect=[0,0,1,0.93])
fig2.savefig("fig_lonardo_qq.png", dpi=300, bbox_inches='tight')
print(audit_figure(fig2))


# ------------------------ cell 25 ------------------------

lo=min(d37.min(),d28.min()); hi=max(d37.max(),d28.max()); pad=0.06*(hi-lo)
for ax in axs: ax.set_ylim(lo-pad, hi+pad)
fig2.tight_layout(rect=[0,0,1,0.93])
fig2.savefig("fig_lonardo_qq.png", dpi=300, bbox_inches='tight')
print(audit_figure(fig2))


# ------------------------ cell 26 ------------------------

r = host.exec_peek("5d4fdee4-5115-4813-8ddf".replace("4813-8ddf","8ddf") if False else "5d4fdee4-5115-4837-8e3b-32091910c034")
print(r.get("status")); print((r.get("stdout") or "")[-3000:])


# ------------------------ cell 27 ------------------------

dw_d = (dtg2['incong']-dtg2['cong']).values
tr_d = (tg2['incong']-tg2['cong']).values
base_dw = dtg2.mean(axis=1).mean(); base_tr = tg2.mean(axis=1).mean()
print("baseline dwell mean %.1f ms, transitions mean %.2f"%(base_dw, base_tr))
fig3, axs3 = plt.subplots(1, 2, figsize=(6.8, 3.3), gridspec_kw=dict(wspace=0.42))
spec = [(dw_d, "Mean dwell time to the two agents", "Difference per dog (ms)\nincongruent − congruent", base_dw, "ms"),
        (tr_d, "Gaze transitions between agents", "Difference per dog (count)\nincongruent − congruent", base_tr, "transitions")]
for ax,(dv,ttl,ylab,bm,unit) in zip(axs3, spec):
    x = 0 + rng.uniform(-0.16,0.16,len(dv))
    ax.scatter(x, dv, s=22, facecolor='none', edgecolor="#4d4d4d", linewidth=0.9, zorder=3)
    m=dv.mean(); h=stats.t.ppf(.975,len(dv)-1)*dv.std(ddof=1)/np.sqrt(len(dv))
    ax.errorbar(0.42, m, yerr=h, fmt='D', ms=6, color="#1f4e79", capsize=5, lw=1.6, zorder=4)
    ax.axhline(0, color=META_GREY, lw=0.9, zorder=1)
    ax.set_xlim(-0.35, 0.95); ax.set_xticks([0,0.42]); ax.set_xticklabels(["each dog\n(n = 38)","mean\n95% CI"])
    ax.set_ylabel(ylab); ax.set_title(ttl, loc='left')
    pct = 100*h/bm
    ax.annotate("CI half-width ±%.0f %s\n= ±%.0f%% of the %.0f %s condition mean"%(h,unit,pct,bm,unit),
                xy=(0.42,m+h), xytext=(0.50, m+h+0.20*(ax.get_ylim()[1]-ax.get_ylim()[0])),
                fontsize=6, ha='left', va='bottom', color="#1f4e79")
    set_frame(ax); ax.margins(y=0.12)
fig3.suptitle("Both null outcomes are compatible with differences of up to ~11% (dwell) and ~20% (transitions)",
              x=0.01, ha='left', fontsize=8)
fig3.tight_layout(rect=[0,0,1,0.93])
fig3.savefig("fig_lonardo_nulls.png", dpi=300, bbox_inches='tight')
print(audit_figure(fig3))
print("dwell CI half %.1f (%.1f%%), transitions CI half %.3f (%.1f%%)"%(
    stats.t.ppf(.975,37)*dw_d.std(ddof=1)/np.sqrt(38), 100*stats.t.ppf(.975,37)*dw_d.std(ddof=1)/np.sqrt(38)/base_dw,
    stats.t.ppf(.975,37)*tr_d.std(ddof=1)/np.sqrt(3…[+67 chars]


# ------------------------ cell 28 ------------------------

plt.close(fig3)
fig3, axs3 = plt.subplots(1, 2, figsize=(6.8, 3.4), gridspec_kw=dict(wspace=0.45))
spec = [(dw_d, "Mean dwell time to the two agents", "Difference per dog (ms)\nincongruent − congruent", base_dw, "%.0f", "ms"),
        (tr_d, "Gaze transitions between agents", "Difference per dog (count)\nincongruent − congruent", base_tr, "%.2f", "transitions")]
ann=[]
for ax,(dv,ttl,ylab,bm,fmt,unit) in zip(axs3, spec):
    x = 0 + rng.uniform(-0.16,0.16,len(dv))
    ax.scatter(x, dv, s=22, facecolor='none', edgecolor="#4d4d4d", linewidth=0.9, zorder=3)
    m=dv.mean(); h=stats.t.ppf(.975,len(dv)-1)*dv.std(ddof=1)/np.sqrt(len(dv))
    ax.errorbar(0.45, m, yerr=h, fmt='D', ms=6, color="#1f4e79", capsize=5, lw=1.6, zorder=4)
    ax.axhline(0, color=META_GREY, lw=0.9, zorder=1)
    ax.set_xlim(-0.35, 0.85); ax.set_xticks([0,0.45]); ax.set_xticklabels(["each dog\n(n = 38)","mean\n95% CI"])
    ax.set_ylabel(ylab); ax.set_title(ttl, loc='left'); set_frame(ax); ax.margins(y=0.18)
    txt = ("95%% CI: "+fmt+" to "+fmt+" %s\n(±%.0f%% of the "+fmt+" %s condition mean)")%(m-h, m+h, unit, 100*h/bm, bm, unit)
    ax.text(0.02, 0.02, txt, transform=ax.transAxes, fontsize=6, color="#1f4e79", ha='left', va='bottom')
fig3.suptitle("Neither null excludes a difference of ~11% (dwell time) or ~20% (transitions)",
              x=0.01, ha='left', fontsize=8)
fig3.tight_layout(rect=[0,0,1,0.94])
fig3.savefig("fig_lonardo_nulls.png", dpi=300, bbox_inches='tight')
print(audit_figure(fig3))


# ------------------------ cell 29 ------------------------

r = host.exec_peek("5d4fdee4-5115-4837-8e3b-32091910c034")
print(r.get("status")); print((r.get("stdout") or "")[-3000:])


# ------------------------ cell 31 ------------------------

setlabels = ["Authors' set\n(n = 28)", "All dogs, ds file\n(n = 37)", "ALL_DATA file\n(n = 38)"]
aggs = [agg28, agg37, agg38]
tests = ["paired t", "Wilcoxon signed-rank", "sign test", "permutation (sign-flip)"]
P = np.zeros((len(tests), len(aggs)))
for j,a in enumerate(aggs):
    s = stat_two_group(a['cong'].values, a['incong'].values, paired=True, n_perm=20000)
    for i,tname in enumerate(tests):
        P[i,j] = float(s.loc[s.test==tname,"p"].iloc[0])
pmat = pd.DataFrame(P, index=tests, columns=[l.replace("\n"," ") for l in setlabels])
print(pmat.to_string(float_format=lambda x:"%.4f"%x))
print("\nmin attainable p (sign, n=28):", stat_min_attainable_p(28, kind="sign"))
mt = stat_multiplicity(list(P[:,0]), labels=["pupil %s (n=28)"%t for t in tests])
print(mt)


# ------------------------ cell 32 ------------------------

r = host.exec_peek("5d4fdee4-5115-4837-8e3b-32091910c034")
print(r.get("status")); print((r.get("stdout") or "")[-3000:])


# ------------------------ cell 35 ------------------------

print(pd.crosstab(ds.condition, ds.trial_type))
# subject-level pupil mean per condition
pc = ds.groupby(['subject','condition'], observed=True)['pupil_base'].mean().unstack()
print("\nsubjects with each condition (ds):", pc.notna().sum().to_dict())
# within response type: approach trials = CA (cong) vs GA (incong);  leave trials = GG (cong) vs CG (incong)
for lab,(c_cong,c_incong) in {"Approach response (CA cong vs GA incong)":("CA","GA"),
                              "Walk-away response (GG cong vs CG incong)":("GG","CG")}.items():
    sub = pc[[c_cong,c_incong]].dropna()
    sub28 = sub[~sub.index.isin(excl)]
    for nm,s in [("all dogs",sub),("authors' set",sub28)]:
        d=s[c_cong]-s[c_incong]; t=stats.ttest_rel(s[c_cong],s[c_incong]); ci=t.confidence_interval()
        print("%-45s %-13s n=%2d  diff=%8.1f  CI[%8.1f,%8.1f]  t=%6.3f  p=%.4f"%(lab,nm,len(s),d.mean(),ci.low,ci.high,t.statistic,t.pvalue))


# ------------------------ cell 36 ------------------------

q = pc[['CA','GA','GG','CG']].dropna()
q28 = q[~q.index.isin(excl)]
for nm,s in [("all dogs",q),("authors' set",q28)]:
    eff_app = s['CA']-s['GA']; eff_leave = s['GG']-s['CG']
    dd = eff_app - eff_leave; t=stats.ttest_rel(eff_app, eff_leave); ci=t.confidence_interval()
    print("%-13s n=%2d  interaction (approach vs walk-away trial-type effect) = %7.1f  CI[%7.1f,%7.1f]  p=%.3f"%(
        nm,len(s),dd.mean(),ci.low,ci.high,t.pvalue))
# condition-wise subject means for context
print("\nsubject-level mean baseline-corrected pupil by condition (all dogs with that condition):")
print(pc.agg(['count','mean']).T.to_string(float_format=lambda x:"%.1f"%x))


# ------------------------ cell 37 ------------------------

r = host.exec_peek("5d4fdee4-5115-4837-8e3b-32091910c034")
print(r.get("status")); print((r.get("stdout") or "")[-3000:])


# ------------------------ cell 38 ------------------------

print(host.stop_child("5d4fdee4-5115-4837-8e3b-32091910c034"))


# ------------------------ cell 39 ------------------------

fig4, ax4 = plt.subplots(figsize=(6.4, 3.0))
cols = {0:"#1f4e79", 1:"#6a6a6a", 2:"#b15928"}
marks = {0:'D', 1:'o', 2:'s'}
setnames = ["Authors' set (n = 28)", "All dogs, same file (n = 37)", "All dogs, ALL_DATA file (n = 38)"]
ypos = np.arange(len(tests))[::-1]
for j in range(3):
    ax4.scatter(P[:,j], ypos, s=34, marker=marks[j], facecolor='none',
                edgecolor=cols[j], linewidth=1.3, zorder=3, label=setnames[j])
ax4.axvline(0.05, color=META_GREY, lw=1.0, ls='--', zorder=1)
ax4.text(0.051, ypos.max()+0.42, "α = 0.05", fontsize=6, color=META_GREY, ha='left')
ax4.set_xscale('log'); ax4.set_xlim(0.007, 0.9)
ax4.set_xticks([0.01,0.02,0.05,0.1,0.2,0.5]); ax4.set_xticklabels(["0.01","0.02","0.05","0.1","0.2","0.5"])
ax4.set_yticks(ypos); ax4.set_yticklabels(tests)
ax4.set_xlabel("Two-sided p for the congruent vs incongruent pupil contrast (log scale)")
ax4.set_title("Every test agrees; the conclusion turns on which dogs are in the sample", loc='left')
ax4.legend(frameon=False, fontsize=6, loc='lower right', handletextpad=0.3)
set_frame(ax4); ax4.margins(y=0.16)
fig4.tight_layout()
fig4.savefig("fig_lonardo_analysischoice.png", dpi=300, bbox_inches='tight')
print(audit_figure(fig4))


# ------------------------ cell 40 ------------------------

r = host.exec_peek("36adacf0-37d4-4c42-8b9a-1f141cc34b49")
print(r.get("status")); print((r.get("stdout") or "")[-2000:])


# ------------------------ cell 41 ------------------------

leg = ax4.get_legend(); leg.remove()
ax4.set_title("Every test agrees; the conclusion turns on which dogs are in the sample", loc='left', pad=22)
ax4.legend(frameon=False, fontsize=6, ncol=3, loc='lower left', bbox_to_anchor=(0.0, 1.005),
           handletextpad=0.3, columnspacing=1.2)
fig4.tight_layout()
fig4.savefig("fig_lonardo_analysischoice.png", dpi=300, bbox_inches='tight')
print(audit_figure(fig4))


# ------------------------ cell 42 ------------------------

r = host.exec_peek("36adacf0-37d4-4c42-8b9a-1f141cc34b49")
print(r.get("status")); print((r.get("stdout") or "")[-2000:])


# ------------------------ cell 45 ------------------------

dwc = dw.groupby(['subject','trial_type','agent_type'], observed=True)['ia_dwell_time'].mean().unstack([1,2])
dwc = dwc.dropna()
eff_c = dwc[('cong','reacting')]-dwc[('cong','communicating')]
eff_i = dwc[('incong','reacting')]-dwc[('incong','communicating')]
dd = eff_c-eff_i; t=stats.ttest_rel(eff_c, eff_i); ci=t.confidence_interval()
print("C8 trial_type x agent_type interaction on dwell time: n=%d  dd=%.1f ms CI[%.1f,%.1f] t=%.3f p=%.3f"%(
    len(dwc), dd.mean(), ci.low, ci.high, t.statistic, t.pvalue))
# C9: condition (4 levels) effect on mean dwell time to agents, dog-level complete cases
dcond = dw.groupby(['subject','condition'], observed=True)['ia_dwell_time'].mean().unstack().dropna()
print("C9 complete-case dogs for 4 conditions:", len(dcond))
fr = stats.friedmanchisquare(*[dcond[c].values for c in ['CA','CG','GA','GG']])
print("C9 Friedman on dog means: chi2=%.3f df=3 p=%.3f"%(fr.statistic, fr.pvalue))
print(dcond.mean().round(1).to_dict())
# C9b condition x agent_type interaction, dog-level
dca = dw.groupby(['subject','condition','agent_type'], observed=True)['ia_dwell_time'].mean().unstack([1,2]).dropna()
effs = {c: dca[(c,'reacting')]-dca[(c,'communicating')] for c in ['CA','CG','GA','GG']}
fr2 = stats.friedmanchisquare(*[v.values for v in effs.values()])
print("C9b Friedman on per-dog agent-preference by condition: n=%d chi2=%.3f p=%.3f"%(len(dca), fr2.statistic, fr2.pvalue))
print({k: round(v.mean(),1) for k,v in effs.items()})


# ------------------------ cell 46 ------------------------

pr = dw.groupby(['subject','condition','agent_type'], observed=True)['proportion.dwell.time.agents'].mean().unstack([1,2]).dropna()
effp = {c: pr[(c,'reacting')]-pr[(c,'communicating')] for c in ['CA','CG','GA','GG']}
fr3 = stats.friedmanchisquare(*[v.values for v in effp.values()])
print("condition x agent_type on the authors' DV (proportion): n=%d Friedman chi2=%.3f df=3 p=%.4f"%(len(pr), fr3.statistic, fr3.pvalue))
print({k: round(v.mean(),3) for k,v in effp.items()})
# collapse to response type: approach (CA,GA) vs walk-away (GG,CG)
app = (effp['CA']+effp['GA'])/2; lev = (effp['GG']+effp['CG'])/2
d=app-lev; t=stats.ttest_rel(app,lev); ci=t.confidence_interval()
print("\nagent preference (reacting-communicating, proportion of trial dwell time):")
print("  approach responses mean %.3f ; walk-away responses mean %.3f"%(app.mean(), lev.mean()))
print("  difference %.3f  95%% CI [%.3f, %.3f]  t=%.3f  p=%.2g  n=%d"%(d.mean(), ci.low, ci.high, t.statistic, t.pvalue, len(d)))
print("  Wilcoxon p=%.2g"%stats.wilcoxon(app,lev).pvalue)
# also in ms
appm=(effs['CA']+effs['GA'])/2; levm=(effs['GG']+effs['CG'])/2
dm=appm-levm; tm=stats.ttest_rel(appm,levm); cim=tm.confidence_interval()
print("  in ms: difference %.0f ms CI[%.0f,%.0f] p=%.2g"%(dm.mean(), cim.low, cim.high, tm.pvalue))


# ------------------------ cell 47 ------------------------

pp = ds.groupby(['subject','condition'], observed=True)['pupil_base'].mean().unstack()
ppc = pp.dropna()
app_p = (ppc['CA']+ppc['GA'])/2; lev_p = (ppc['GG']+ppc['CG'])/2
d=app_p-lev_p; t=stats.ttest_rel(app_p,lev_p); ci=t.confidence_interval()
print("pupil by response type (approach vs walk-away), n=%d: approach %.1f, walk-away %.1f"%(len(ppc), app_p.mean(), lev_p.mean()))
print("  difference %.1f  95%% CI [%.1f, %.1f]  p=%.3f"%(d.mean(), ci.low, ci.high, t.pvalue))
# per-dog balance of response type across trial types in the full (unexcluded) sample
bal = ds.groupby(['subject','condition'], observed=True).size().unstack().notna()
bal['balanced'] = bal[['CA','GA']].sum(axis=1)>=0
miss = bal[['CA','CG','GA','GG']]
unbal = miss[~miss.all(axis=1)]
print("\ndogs missing >=1 condition in the ds file: %d"%len(unbal))
print(unbal.astype(int).to_string())


# ------------------------ cell 48 ------------------------

r = host.exec_peek("36adacf0-37d4-4c42-8b9a-1f141cc34b49")
print(r.get("status")); print((r.get("stdout") or "")[-2500:])


# ------------------------ cell 49 ------------------------

rows = [
 dict(id="C1", claim="Dogs' looking time (dwell time to the two agents) did not differ between congruent and incongruent responses",
   source="abstract + authors' code", design="within-subject, 2 levels; unit = dog (39 dogs, 152 trials, 1 trial per condition)",
   test_used="beta GLMM on proportion dwell time, trial_type removed by LRT (glmmTMB)",
   test_indicated="same, or paired test on dog means", reported_p="not visible (paywalled)",
   recomputed_p="0.987 (paired t on dog means, n=38); 0.897 (Wilcoxon)",
   effect="-3.8 ms (incongruent - congruent), 95% CI [-466.6, +459.0]; dz = -0.003",
   verdict="Supported", severity="C"),
 dict(id="C2", claim="The number of gaze transitions between the two actresses did not differ between congruent and incongruent responses",
   source="abstract + authors' code", design="within-subject, 2 levels; unit = dog (39 dogs, 152 trials)",
   test_used="Poisson GLMM with log(trial dwell time) offset, trial_type LRT (lme4)",
   test_indicated="same, or paired test on dog means", reported_p="not visible (paywalled)",
   recomputed_p="0.763 (paired t on dog means, n=38); 0.603 (Wilcoxon)",
   effect="+0.07 transitions (incongruent - congruent), 95% CI [-0.37, +0.51]; dz = 0.049",
   verdict="Supported", severity="C"),
 dict(id="C3", claim="Pupils dilated more when watching incongruent than congruent responses (headline claim)",
   source="abstract + authors' code", design="within-subject; 41 samples per trial at 100 ms (1000-5000 ms window) nested in trial nested in dog",
   test_used="GAMM (mgcv::bam, ML, discrete): parametric trial_type + s(time, by=trial_type), random smooths by dog and by trial",
   test_indicated="GAMM is defensible; the dog-level contrast must be reported alongside it",
   reported_p="not visible (paywalled)", recomputed_p="GAMM_P3", effect="GAMM_E3",
   verdict="GAMM_V3", severity="GAMM_S3"),
 dict(id="C4", claim="The same pupil contrast at the level of the experimental unit: paired t-test on one mean…[+6054 chars]


# ------------------------ cell 50 ------------------------

md = (agg28['cong']-agg28['incong']).median()
print("median paired pupil difference n=28: %.1f"%md)
print()
import math
print("checks: dwell CI half %.1f  pct %.1f ; trans CI half %.3f pct %.1f"%(
 stats.t.ppf(.975,37)*dw_d.std(ddof=1)/np.sqrt(38), 100*stats.t.ppf(.975,37)*dw_d.std(ddof=1)/np.sqrt(38)/base_dw,
 stats.t.ppf(.975,37)*tr_d.std(ddof=1)/np.sqrt(38), 100*stats.t.ppf(.975,37)*tr_d.std(ddof=1)/np.sqrt(38)/base_tr))


# ------------------------ cell 51 ------------------------

r = host.exec_peek("36adacf0-37d4-4c42-8b9a-1f141cc34b49")
print(r.get("status")); print((r.get("stdout") or "")[-2500:])


# ------------------------ cell 52 ------------------------

print(host.stop_child("36adacf0-37d4-4c42-8b9a-1f141cc34b49"))


# ------------------------ cell 53 ------------------------

claims.loc[claims.id=="C3", ["recomputed_p","effect","verdict","severity"]] = [
 "not reproducible here: the GAMM did not complete in ~2.4 h of fitting in two R environments (mgcv::bam, 4592 rows, 112 trial-level and 28 dog-level factor smooths)",
 "not computed; the dog-level version of the same contrast is C4/C6",
 "Not assessable", "C"]
claims.loc[claims.id=="C5", "effect"] = "same contrast as C4; median paired difference -144.4 units"
claims.to_csv("claims_lonardo.csv", index=False)
print(claims[['id','verdict','severity']].to_string(index=False))
print(pd.read_csv("claims_lonardo.csv").shape)


# ------------------------ cell 55 ------------------------

import csv, json
rows=list(csv.DictReader(open("claims_lonardo.csv", encoding="utf-8")))
print(len(rows), [r["id"] for r in rows])
out = {
 "paper": "Lonardo L, Volter CJ, Huber L (2026). Pupil size changes reveal that dogs are sensitive to the social conventions behind human gestures. Cognition 274:106586.",
 "doi": "10.1016/j.cognition.2026.106586",
 "n_claims": len(rows),
 "claims": [{"id":r["id"], "claim":r["claim"], "design":r["design"], "test_used":r["test_used"],
             "test_indicated":r["test_indicated"], "reported_p":r["reported_p"],
             "recomputed_p":r["recomputed_p"], "effect":r["effect"],
             "verdict":r["verdict"], "severity":r["severity"]} for r in rows],
 "headline_findings": [
  "Severity A (C6): the headline pupil effect exists only in the 28-dog subset the authors' pupil script retains (dogs with all four valid trials). Their pipeline reproduces exactly there (paired t p=0.0204, exact Wilcoxon p=0.0110, mean difference -141.6 baseline-corrected units, 95% CI [-259.5,-23.6], dz=-0.466), but run on every dog in the same data file it gives p=0.181 (n=37, -81.3 [-202.1,+39.5]) and on the authors' own ALL_DATA file p=0.442 (n=38, -55.6 [-200.3,+89.2]). The nine excluded dogs with both trial types shift the contrast the other way (+106.2). The abstract reports the study as N=39. The exclusion rule is outcome-independent as written and has a principled rationale, but response type has no measurable effect on pupil size here (-11.4, 95% CI [-132.9,+110.1], p=0.85), so that rationale does not explain why the effect disappears without the exclusion.",
  "Severity B (C11, C10): the abstract's dissociation between gaze measures and pupil size was never tested as a contrast between measures, and its context-specificity claim is demonstrated for walking-away responses in the authors' subset only (GG-CG: -179.7 [-355.0,-4.5], p=0.045) and not for approaching responses (CA-GA: -103.4 [-268.4,+61.5], p=0.209), with no evidence that the two…[+5858 chars]


# ------------------------ cell 56 ------------------------

print(host.findings())


# ------------------------ cell 57 ------------------------

res = host.submit_output(out,
 completion_bullets=[
  "Built a 12-claim register from the abstract and the authors' R code",
  "Reproduced the authors' descriptive and paired-test values exactly from the deposited data",
  "Found the headline pupil effect confined to the 28-of-39-dog completeness subset",
  "Delivered review_lonardo.md, claims_lonardo.csv and four figures"],
 deviations=[
  "Published full text unavailable (Elsevier paywall): the review covers the publisher abstract plus the authors' deposited data and code only. No reported statistic, p-value, CI, per-analysis n or exclusion rationale from the paper could be read, so the 'reported p' column is blank for all 12 claims and no reported-versus-recomputed delta was formed anywhere. Claims C1-C3 and C10-C12 are abstract-derived; C4-C9 are reconstructed from the authors' .Rmd files and attributed to the code.",
  "The authors' pupil GAMM (mgcv::bam, 4592 rows, 112 trial-level and 28 dog-level factor smooths) did not converge: 95 min on the authors' exact ML call and 29 min on an fREML variant, in two R environments (the second environment's freshly built mgcv crashed on load). Claim C3 is recorded Not assessable; no substitute model was fitted or reported in its place.",
  "The beta GLMM (glmmTMB) and Poisson GLMM (lme4) behind C1, C2, C8 and C9 were not refitted. They were read and judged on specification, and their claims re-tested with dog-level paired tests on the same reconstructed data - correct-unit tests, but not the authors' models (no trial-number covariate, no random slopes, no exposure offset), so they do not reproduce the authors' chi-square and p-values.",
  "The deposit's workspaces/ and saves/ directories, which the .Rmd files load from and write to, are absent, so the authors' own numeric model output tables could not be read.",
  "The approach-versus-walk-away contrast in C9 is exploratory: formed from the design rather than a p-value scan, but formed after seeing the data, and counted a…[+58 chars]
