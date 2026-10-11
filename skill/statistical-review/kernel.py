
import numpy as np

def stat_mean_difference(x, y):
    """Default permutation statistic: difference in means."""
    return float(np.mean(x) - np.mean(y))


def stat_qq_panel(groups, paired=False, title=None):
    """Normal Q-Q panel for assumption review (skill section 4).

    groups: dict {label: 1-D array}. With paired=True and exactly two entries,
    the panel shows the WITHIN-PAIR DIFFERENCES -- the quantity a paired test
    assumes normal -- not the two marginals. Independent groups get one panel
    each; never pool groups with different means. Returns a Figure.
    """
    import matplotlib.pyplot as plt
    from scipy import stats as sps
    items = [(k, np.asarray(v, dtype=float)) for k, v in groups.items()]
    items = [(k, v[~np.isnan(v)]) for k, v in items]
    if paired:
        if len(items) != 2:
            raise ValueError("paired=True needs exactly two groups")
        (ka, a), (kb, b) = items
        if len(a) != len(b):
            raise ValueError("paired groups must have equal length")
        items = [("%s - %s (paired differences)" % (ka, kb), a - b)]
    fig, axes = plt.subplots(1, len(items), figsize=(3.6 * len(items), 3.4),
                             squeeze=False)
    for ax, (label, v) in zip(axes[0], items):
        sps.probplot(v, dist="norm", plot=ax)
        ax.set_title("%s  (n=%d)" % (label, len(v)), fontsize=10)
        ax.get_lines()[0].set(marker="o", markersize=4, linestyle="none")
        ax.get_lines()[1].set(linewidth=1)
    if title:
        fig.suptitle(title)
    fig.tight_layout()
    return fig


def stat_permutation_p(a, b, statistic=None, paired=False, n_perm=10000, seed=0):
    """Two-sided permutation p-value with explicit resolution (section 5c).

    Unpaired: shuffles group labels -- the null is that the two whole
    distributions are identical. Paired: flips signs within pairs -- the null
    is within-pair exchangeability. The two schemes encode different nulls;
    pick the one matching the design (R5.7).

    statistic: unpaired, f(x, y) -> float, default mean difference; paired,
    f(differences) -> float, default mean. Returns dict with p = (k+1)/(N+1),
    k, n_perm, resolution and the null vector.
    """
    rng = np.random.default_rng(seed)
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    null = np.empty(n_perm)
    if paired:
        if len(a) != len(b):
            raise ValueError("paired permutation needs equal-length arrays")
        d = a - b
        if statistic is None:
            statistic = np.mean
        obs = float(statistic(d))
        for i in range(n_perm):
            s = rng.choice([-1.0, 1.0], size=len(d))
            null[i] = statistic(d * s)
    else:
        if statistic is None:
            statistic = stat_mean_difference
        obs = float(statistic(a, b))
        pooled = np.concatenate([a, b])
        na = len(a)
        for i in range(n_perm):
            q = rng.permutation(pooled)
            null[i] = statistic(q[:na], q[na:])
    k = int(np.sum(np.abs(null) >= abs(obs) - 1e-12))
    return {"statistic": obs, "p": (k + 1) / (n_perm + 1), "k_as_extreme": k,
            "n_perm": n_perm, "resolution": 1.0 / (n_perm + 1), "null": null}


def stat_two_group(a, b, paired=False, n_perm=10000, seed=0):
    """Candidate tests side by side for one two-group claim (section 9 step 4).

    Returns a DataFrame (test, statistic, p, assumption) showing how much the
    conclusion depends on the test choice. .attrs["effects"] carries the
    estimate, 95% CI, standardised effect size and, unpaired, the probability
    of superiority and variance ratio.
    """
    import pandas as pd
    from scipy import stats as sps
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    a = a[~np.isnan(a)]
    b = b[~np.isnan(b)]
    rows = []
    if paired:
        if len(a) != len(b):
            raise ValueError("paired comparison needs equal-length arrays")
        d = a - b
        t = sps.ttest_rel(a, b)
        rows.append(("paired t", float(t.statistic), float(t.pvalue),
                     "paired differences normal"))
        w = sps.wilcoxon(a, b)
        rows.append(("Wilcoxon signed-rank", float(w.statistic), float(w.pvalue),
                     "differences symmetric about the null median"))
        nz = d[d != 0]
        pos = int(np.sum(nz > 0))
        sg = sps.binomtest(pos, len(nz), 0.5)
        rows.append(("sign test", float(pos), float(sg.pvalue),
                     "independent pairs; sign balance under H0"))
        pm = stat_permutation_p(a, b, paired=True, n_perm=n_perm, seed=seed)
        rows.append(("permutation (sign-flip)", pm["statistic"], pm["p"],
                     "within-pair exchangeability"))
        est = float(np.mean(d))
        sd = float(np.std(d, ddof=1))
        ci = sps.t.interval(0.95, len(d) - 1, loc=est, scale=sps.sem(d))
        eff = {"mean_difference": est, "ci95": (float(ci[0]), float(ci[1])),
               "cohen_dz": est / sd if sd > 0 else float("nan"),
               "n_pairs": int(len(d)), "n_zero_differences": int(len(d) - len(nz)),
               "min_attainable_p_sign": stat_min_attainable_p(len(nz), kind="sign")}
    else:
        tw = sps.ttest_ind(a, b, equal_var=False)
        rows.append(("Welch t (unequal variance)", float(tw.statistic),
                     float(tw.pvalue), "within-group normality; variances may differ"))
        tp = sps.ttest_ind(a, b, equal_var=True)
        rows.append(("pooled t (equal variance)", float(tp.statistic),
                     float(tp.pvalue), "within-group normality AND equal variance"))
        mw = sps.mannwhitneyu(a, b, alternative="two-sided")
        rows.append(("Mann-Whitney U", float(mw.statistic), float(mw.pvalue),
                     "identical distributions under H0 (not equal medians)"))
        pm = stat_permutation_p(a, b, n_perm=n_perm, seed=seed)
        rows.append(("permutation (label swap)", pm["statistic"], pm["p"],
                     "exchangeable labels: whole distribution identical"))
        na, nb = len(a), len(b)
        va, vb = float(np.var(a, ddof=1)), float(np.var(b, ddof=1))
        sp = np.sqrt(((na - 1) * va + (nb - 1) * vb) / (na + nb - 2))
        g = (np.mean(a) - np.mean(b)) / sp if sp > 0 else float("nan")
        g = g * (1 - 3 / (4 * (na + nb) - 9))
        se = np.sqrt(va / na + vb / nb)
        df = se ** 4 / ((va / na) ** 2 / (na - 1) + (vb / nb) ** 2 / (nb - 1))
        est = float(np.mean(a) - np.mean(b))
        ci = sps.t.interval(0.95, df, loc=est, scale=se)
        eff = {"mean_difference": est, "ci95": (float(ci[0]), float(ci[1])),
               "hedges_g": float(g), "welch_df": float(df),
               "prob_superiority": float(mw.statistic / (na * nb)),
               "var_ratio": va / vb if vb > 0 else float("nan"), "n": (na, nb),
               "min_attainable_p_perm": stat_min_attainable_p(na, nb, "permutation")}
    out = pd.DataFrame(rows, columns=["test", "statistic", "p", "assumption"])
    out.attrs["effects"] = eff
    return out


def stat_multiplicity(pvals, alpha=0.05, labels=None):
    """Benjamini-Hochberg FDR and Bonferroni side by side (section 7).

    Returns a DataFrame sorted by raw p with bh_q, bonferroni_p and per-rule
    significance; .attrs["summary"] carries the discovery counts and the
    number of raw hits expected by chance.
    """
    import pandas as pd
    p = np.asarray(pvals, dtype=float)
    m = len(p)
    if labels is None:
        labels = ["test_%d" % i for i in range(m)]
    order = np.argsort(p)
    ranked = p[order]
    q = ranked * m / np.arange(1, m + 1)
    q = np.minimum(np.minimum.accumulate(q[::-1])[::-1], 1.0)
    out = pd.DataFrame({"label": np.asarray(labels)[order], "p": ranked,
                        "bh_q": q, "bonferroni_p": np.minimum(ranked * m, 1.0)})
    out["sig_raw"] = out["p"] <= alpha
    out["sig_bh"] = out["bh_q"] <= alpha
    out["sig_bonferroni"] = out["bonferroni_p"] <= alpha
    out.attrs["summary"] = {"m": m, "alpha": alpha,
                            "n_raw": int(out["sig_raw"].sum()),
                            "n_bh": int(out["sig_bh"].sum()),
                            "n_bonferroni": int(out["sig_bonferroni"].sum()),
                            "expected_false_at_raw": m * alpha}
    return out


def stat_min_attainable_p(n1, n2=None, kind="sign"):
    """Smallest two-sided p the design can possibly produce (R5.14).

    kind: "sign" or "signrank" (n1 nonzero pairs), "ranksum" or "permutation"
    (n1 vs n2, exhaustive label assignments). If this exceeds alpha, the claim
    is Not assessable however the data fall.
    """
    from math import comb
    if kind in ("sign", "signrank"):
        return min(1.0, 2.0 / 2 ** n1)
    if kind in ("ranksum", "permutation"):
        if n2 is None:
            raise ValueError("kind=%r needs n2" % kind)
        return min(1.0, 2.0 / comb(n1 + n2, n1))
    raise ValueError("kind must be sign, signrank, ranksum or permutation")


def stat_pcurve(pvals, alpha=0.05):
    """P-curve of the significant p-values (section 7 p-hacking screen).

    Right-skew (mass near 0) is what a real effect looks like; a pile-up just
    below alpha is the p-hacking fingerprint. Dashed line = flat expectation.
    Returns (fig, counts dict).
    """
    import matplotlib.pyplot as plt
    p = np.asarray(pvals, dtype=float)
    sig = p[(p > 0) & (p <= alpha)]
    edges = np.linspace(0, alpha, 6)
    counts, _ = np.histogram(sig, bins=edges)
    fig, ax = plt.subplots(figsize=(4.4, 3.3))
    centers = (edges[:-1] + edges[1:]) / 2
    ax.bar(centers, counts, width=(edges[1] - edges[0]) * 0.85, color="#4878a8")
    ax.axhline(len(sig) / 5.0, linestyle="--", linewidth=1, color="0.4")
    ax.set_xlabel("p-value")
    ax.set_ylabel("number of tests")
    ax.set_title("p-curve: %d of %d tests at p<=%g" % (len(sig), len(p), alpha),
                 fontsize=10)
    ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout()
    return fig, dict(zip(["%.3f-%.3f" % (edges[i], edges[i + 1]) for i in range(5)],
                         counts.tolist()))
